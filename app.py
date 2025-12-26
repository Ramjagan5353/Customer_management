from flask import Flask, render_template, request
import sqlite3

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
    phone TEXT NOT NULL
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

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                (name, email, phone)
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

        try:
            conn.execute(
                """
                UPDATE customers
                SET name = ?, email = ?, phone = ?
                WHERE email = ?
                """,
                (new_name, new_email, new_phone, email)
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
    <h2>Customer Management</h2>
    <a href='/add'>Add Customer</a><br><br>
    <a href='/search'>Search Customer</a>
    """

if __name__ == '__main__':
    app.run(debug=True)