from flask import Flask, request, session, redirect, url_for, flash
import pyodbc
import pandas as pd
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Azure SQL Database connection settings
server = 'cloud-project-123.database.windows.net'
database = 'sample'
username = 'knguyen'
password = 'Pass1234'
driver = '{ODBC Driver 17 for SQL Server}'


transactions_df = pd.DataFrame()
households_df = pd.DataFrame()
products_df = pd.DataFrame()
merged_df = pd.DataFrame()

try:

    cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = cnxn.cursor()


    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='users')
        BEGIN
            CREATE TABLE users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        END
    """)

    households_query = "SELECT * FROM households"
    transactions_query = "SELECT * FROM transactions"
    products_query = "SELECT * FROM products"

    households_df = pd.read_sql(households_query, cnxn)
    transactions_df = pd.read_sql(transactions_query, cnxn)
    products_df = pd.read_sql(products_query, cnxn)

    merged_df = pd.merge(households_df, transactions_df, on='HSHD_NUM')
    merged_df = pd.merge(merged_df, products_df, on='PRODUCT_NUM')
    print("Database connection successful!")

except Exception as e:
    print("Error connecting to the database:", e)


@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

 
        try:
            cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
            cnxn.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return f"Error: {e}"

    return '''
        <form action="/" method="post">
            <label for="email">Email:</label>
            <input type="text" id="email" name="email"><br><br>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username"><br><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password"><br><br>
            <button type="submit">Sign Up</button>
        </form>
    '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['logged_in'] = True
                return redirect(url_for('search_data'))
            else:
                return 'Invalid username or password'
        except Exception as e:
            return f"Error: {e}"

    return '''
        <form action="/login" method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username"><br><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password"><br><br>
            <button type="submit">Login</button>
        </form>
    '''


@app.route('/search_data', methods=['GET', 'POST'])
def search_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        if request.method == 'POST':
            hshd_num = request.form.get('hshd_num')
        else:
            hshd_num = request.args.get('hshd_num')

        if not hshd_num:
            hshd_num = 10

     
        filtered_df = merged_df[merged_df['HSHD_NUM'] == int(hshd_num)]

 
        sorted_df = filtered_df.sort_values(by=['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY'])

   
        columns_order = ['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY'] + [col for col in sorted_df.columns if col not in ['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY']]
        sorted_df = sorted_df[columns_order]

   
        html_table = sorted_df.to_html(index=False)

    
        input_box = f"""
        <form action="/search_data" method="post">
            <label for="hshd_num">Enter HSHD_NUM:</label>
            <input type="text" id="hshd_num" name="hshd_num">
            <button type="submit">Search</button>
        </form>
        """

   
        upload_form = '''
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".csv, .xlsx, .xls">
            <button type="submit">Upload</button>
        </form>
        '''

    
        html_response = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Search Data</title>
        </head>
        <body>
            <h1>Search Data</h1>
            {input_box}
            {upload_form}
            <h2>Search Results for HSHD_NUM {hshd_num}</h2>
            {html_table}
        </body>
        </html>
        """

        return html_response

    except Exception as e:
        print("Error:", e)
        return "Error: " + str(e)


@app.route('/upload', methods=['POST'])
def upload_file():
    global transactions_df, households_df, products_df, merged_df

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        filename = file.filename.lower()
        try:
            if 'csv' in filename:
                upload_df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
            elif 'xls' in filename or 'xlsx' in filename:
                upload_df = pd.read_excel(file)

            if 'transaction' in filename:
                transactions_df = update_dataframe(transactions_df, upload_df)
            elif 'household' in filename:
                households_df = update_dataframe(households_df, upload_df)
            elif 'product' in filename:
                products_df = update_dataframe(products_df, upload_df)

     
            merged_df = pd.merge(households_df, transactions_df, on='HSHD_NUM')
            merged_df = pd.merge(merged_df, products_df, on='PRODUCT_NUM')

     
            flash('File uploaded successfully')
            return redirect(url_for('search_data'))
        except Exception as e:
            flash(f'Error processing {filename}: {str(e)}')
            return redirect(request.url)

    return redirect(request.url)

def update_dataframe(existing_df, new_df):

    common_columns = existing_df.columns.intersection(new_df.columns)
    new_df = new_df[common_columns]
    

    updated_df = pd.concat([existing_df, new_df], axis=0).drop_duplicates()
    
    return updated_df



if __name__ == '__main__':
    app.run(debug=True)
