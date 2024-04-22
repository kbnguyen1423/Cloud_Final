# Cloud_Final

Website URL: https://cloud-final.azurewebsites.net/

## Sign Up Page (https://cloud-final.azurewebsites.net/)
1. Sign in using email, username, password. You will be redirected to the login page.

## Login Page (https://cloud-final.azurewebsites.net/login)
2. Login using credentials from signup page. You will be redirected to the data search page.
   
## Search Data Page (https://cloud-final.azurewebsites.net/search_data)
3. Enter a HSHD_NUM to see data results. Upload CSV files here with 'transaction', 'household' or 'product' in the name.

4. ## To run the dashboard, you need to run the following files, in chronological order:

household.py

products.py

transactions.py

To run, simply do:

```python
python3 filename.py
```

These 3 files are used to upload the files given in the zip into our MySQL database hosted in Azure. product.py and transactions.py will take very long to run as they are considerably large.

After this you may run the connect.py which is used to launch the database.

The default port is set to 8080, which may be changed if it appears to be busy on your end.

**Note:**

1. Since 400_transactions.csv contains a common column, the order is important, or sqlalchemy will throw an IntegrityError.
2. If the table is already created, then a Programming Error might be thrown by sqlalchemy due to the duplicate rows. To avoid this a new database needs to be created in Azure.
