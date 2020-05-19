# one-main-api
 One Main REST API
 created by : Tom Hyde
 last update : 2020-05-19

 api_final.py - Python  simple REST API for payments
    - uses FLASK framework and sqlite3 for database

 sqlite3 database omf.db included
   database has 3 tables
       - loan  (contains loan info)
       - payment  (contains all payment info)
       - user  (contains user info)

 API supports
 /api/v1/resources/loans/all - returns all loan information
 /api/v1/resources/loans?id=<id>  - returns loan <id> information
 /api/v1/resources/loans/showpayments?id=<id>  - returns payment history for loan <id>
 /api/v1/resources/loans/addpayment?id=<id>&amount=<amount> - adds payment for loan <id> for amount <amount>












