from flask import Flask, request
import pyodbc
import pandas as pd

app = Flask(__name__)

# Azure SQL Database connection settings
server = 'cloud-project-123.database.windows.net'
database = 'sample'
username = 'knguyen'
password = 'Pass1234'
driver = '{ODBC Driver 17 for SQL Server}'

try:
    # Attempt to establish a connection
    cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = cnxn.cursor()

    # Print success message if connection is established

            # Execute SQL queries to fetch data from each table
    households_query = "SELECT * FROM households"
    transactions_query = "SELECT * FROM transactions"
    products_query = "SELECT * FROM products"

        # Convert query results into DataFrames
    households_df = pd.read_sql(households_query, cnxn)
    transactions_df = pd.read_sql(transactions_query, cnxn)
    products_df = pd.read_sql(products_query, cnxn)

        # Merge or join DataFrames based on common columns
    merged_df = pd.merge(households_df, transactions_df, on='HSHD_NUM')
    merged_df = pd.merge(merged_df, products_df, on='PRODUCT_NUM')
    print("Database connection successful!")

except Exception as e:
    # Print error message if connection fails
    print("Error connecting to the database:", e)

@app.route('/sample_data')
def sample_data():
    try:
        # Filter the merged DataFrame based on HSHD_NUM = 10
        filtered_df = merged_df[merged_df['HSHD_NUM'] == 10]

        # Sort the filtered DataFrame
        sorted_df = filtered_df.sort_values(by=['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY'])

        # Reorder columns
        columns_order = ['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY'] + [col for col in sorted_df.columns if col not in ['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY']]
        sorted_df = sorted_df[columns_order]

        # Convert sorted DataFrame to HTML table
        html_table = sorted_df.to_html(index=False)

        # Render HTML response
        html_response = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sample Data Pull for HSHD_NUM #10</title>
        </head>
        <body>
            <h1>Sample Data Pull for HSHD_NUM #10</h1>
            {html_table}
        </body>
        </html>
        """

        return html_response

    except Exception as e:
        print("Error:", e)
        return "Error: " + str(e)

@app.route('/search_data', methods=['GET', 'POST'])
def search_data():
    try:
        # Get the value of HSHD_NUM from the input box
        if request.method == 'POST':
            hshd_num = request.form.get('hshd_num')
        else:
            hshd_num = request.args.get('hshd_num')

        # If HSHD_NUM is not provided, set it to None
        if not hshd_num:
           hshd_num = 10

        # Filter the merged DataFrame based on the provided HSHD_NUM
        filtered_df = merged_df[merged_df['HSHD_NUM'] == int(hshd_num)]

        # Sort the filtered DataFrame
        sorted_df = filtered_df.sort_values(by=['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY'])

        # Reorder columns
        columns_order = ['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY'] + [col for col in sorted_df.columns if col not in ['HSHD_NUM', 'BASKET_NUM', 'PURCHASE', 'PRODUCT_NUM', 'DEPARTMENT', 'COMMODITY']]
        sorted_df = sorted_df[columns_order]

        # Convert sorted DataFrame to HTML table
        html_table = sorted_df.to_html(index=False)

        # Include the input box for searching
        input_box = f"""
        <form action="/search_data" method="post">
            <label for="hshd_num">Enter HSHD_NUM:</label>
            <input type="text" id="hshd_num" name="hshd_num">
            <button type="submit">Search</button>
        </form>
        """

        # Render HTML response
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
            <h2>Search Results for HSHD_NUM {hshd_num}</h2>
            {html_table}
        </body>
        </html>
        """

        return html_response

    except Exception as e:
        print("Error:", e)
        return "Error: " + str(e)


if __name__ == '__main__':
    app.run(debug=True)
