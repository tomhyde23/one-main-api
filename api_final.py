from datetime import datetime
import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# check loan balance
def check_loan_balance(loan_id):
    balance = 0.00
    conn = sqlite3.connect('omf.db')
    cur = conn.cursor()
    query = "SELECT (loan.loan_amount - coalesce(SUM(payment.amount), 0)) as balance FROM loan LEFT OUTER JOIN payment on loan.id=payment.loan_id"
    query += " WHERE loan.id=" + loan_id + " GROUP BY loan.id;"
    cur.execute(query)
    balance = cur.fetchone()
    conn.close()
    return balance[0]

# check loan id exists
def check_loan_exists(loan_id):
    id = 0
    conn = sqlite3.connect('omf.db')
    cur = conn.cursor()
    query = "SELECT count() FROM loan WHERE loan.id=" + loan_id + ";"
    cur.execute(query)
    id = cur.fetchone() 
    conn.close()
    if (id[0] > 0):
        return True
    else:
        return False

# dict to store query results
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# home page
@app.route('/', methods=['GET'])
def home():
    return "<h1>Payment API</h1><p>This site is a prototype API.</p>"

# return all loans
@app.route('/api/v1/resources/loans/all', methods=['GET','POST'])
def api_all():
    conn = sqlite3.connect('omf.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_loans = cur.execute("SELECT loan.id, loan.acct_id, loan.date_created, loan.loan_amount, user.name, user.state, (loan.loan_amount-coalesce(SUM(payment.amount), 0)) as balance FROM loan LEFT OUTER JOIN payment on loan.ID=payment.loan_id LEFT OUTER JOIN user on loan.acct_id = user.id GROUP BY loan.id;").fetchall()

    return jsonify(all_loans)

# return all payments by loan id
@app.route('/api/v1/resources/loans/showpayments', methods=['GET','POST'])
def api_showpayments():
    query_parameters = request.args
    id = query_parameters.get('id')

    # exit if loan_id not supplied
    if not (id):
        return "Record not found", 204

    conn = sqlite3.connect('omf.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_payments = cur.execute('SELECT * FROM payment WHERE loan_id=' + id + ' ORDER BY date DESC;').fetchall()
    return jsonify(all_payments)

# default 404 page
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

# return filtered results
@app.route('/api/v1/resources/loans', methods=['GET','POST'])
def api_filter():

    # collect args
    query_parameters = request.args

    id = query_parameters.get('id')

    # exit if arg not supplied
    if not (id):
        return "Record not found", 204

    query = "SELECT loan.id, loan.acct_id, loan.date_created, loan.loan_amount, (loan.loan_amount-coalesce(SUM(payment.amount), 0)) as balance FROM loan LEFT OUTER JOIN payment on loan.id=payment.loan_id WHERE loan.id=" + id + " GROUP BY loan.id;"

    conn = sqlite3.connect('omf.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query).fetchall()

    return jsonify(results)

# add payment method
@app.route('/api/v1/resources/loans/addpayment', methods=['GET','POST'])
def api_addpayment():

    # collect args
    query_parameters = request.args
    id = query_parameters.get('id')
    amount = query_parameters.get('amount')

    # exit if either args are missing
    if not (id and amount):
        return "Record not found", 201
    
    if (check_loan_exists(id) == False):
        return "Record not found", 201
    
# Check payment would not NET in negative balance
    if (check_loan_balance(id) - float(amount) < 0): 
        return "Cannot Process Payment for loan - " + str(id), 401
# Add payment
    query = "INSERT INTO payment (loan_id, amount, date) VALUES (" + id +"," + amount + ",'" + datetime.now().strftime("%Y-%m-%d") + "');"

    conn = sqlite3.connect('omf.db')
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    
    return "Payment Added", 200

app.run()

