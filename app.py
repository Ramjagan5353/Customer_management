from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, date
import re

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('customers.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table (runs once)
conn = get_db_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS customers (
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    dob DATE NOT NULL
)
""")
conn.commit()
conn.close()

@app.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        
        # Check if customer is at least 18 years old
        birth_date = datetime.strptime(dob, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 18:
            return "Error: Customer must be at least 18 years old!"

        if not(len(phone)==13 and re.match('+91',phone[:3]) and re.match('\\d{10}',phone[3:13])):
            return "Error: Idhem number ra babu"
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO customers (name, email, phone,dob) VALUES (?, ?, ?,?)",
                (name, email, phone,dob)
            )
            conn.commit()
            conn.close()
            return "Customer Added Successfully!"
        
        except sqlite3.IntegrityError:
            return "Error: Email already exists!"

    return render_template('add_customer.html')

@app.route('/search', methods=['GET', 'POST'])
def search_customer():
    customers = []
    if request.method == 'POST':
        name = request.form['name']

        conn = get_db_connection()
        customers = conn.execute(
            "SELECT * FROM customers WHERE name LIKE ?",
            ('%' + name + '%',)
        ).fetchall()
        conn.close()

    return render_template('search_customer.html', customers=customers)

@app.route('/update/<email>', methods=['GET', 'POST'])
def update_customer(email):
    conn = get_db_connection()
    customer = conn.execute(
        "SELECT * FROM customers WHERE email = ?",
        (email,)
    ).fetchone()

    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        new_phone = request.form['phone']
        new_dob = request.form['dob']
        
        # Check if customer is at least 18 years old
        birth_date = datetime.strptime(new_dob, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 18:
            conn.close()
            return "Error: Customer must be at least 18 years old!"
        
        try:
            conn.execute(
                """
                UPDATE customers
                SET name = ?, email = ?, phone = ?,dob=?
                WHERE email = ?
                """,
                (new_name, new_email, new_phone,new_dob, email)
            )
            conn.commit()
            conn.close()
            return "Customer Updated Successfully!"

        except sqlite3.IntegrityError:
            conn.close()
            return "Error: Email already exists!"

    conn.close()
    return render_template('update_customer.html', customer=customer)

@app.route('/delete/<email>')
def delete_customer(email):
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM customers WHERE email = ?",
        (email,)
    )
    conn.commit()
    conn.close()
    return "Customer Deleted Successfully!"

@app.route('/')
def home():
    return """
    <center>
    <h2>Customer Management</h2>
    <a href='/add'>Add Customer</a><br><br>
    <a href='/search'>Search Customer</a>
    </center>
    """

if __name__ == '__main__':
    app.run(debug=True)