from flask import Flask, render_template, request, url_for, session, redirect, flash
# from waitress import serve
# import libsql_client
# from libsql_client import create_client
import libsql

import sqlite3

app = Flask(__name__)
app.secret_key = 'secret-key'

# turso db shell libsql://wattsaver-shiroewt.aws-ap-northeast-1.turso.io  eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTM5Nzg0NjYsImlkIjoiY2FmOTgzZDQtZTkyZS00MTlkLTgzMjgtYTBhM2UxZTc3ZGRmIiwicmlkIjoiNjhiNGMyODgtZjBhMi00MzYwLTg0MTctNDAzNjE3YmE0YjkyIn0.I0cd3UsLdvC9w8zy7HFONwH9UEqSGZidTE-Sp8z1fFsEWOrkW-CO63qeDZJpc8i5DcoiVPEGrcmrl2puVGvmDg

def get_db():
    # koneksi turso
    conn = libsql.connect(
        database="libsql://wattsaver-shiroewt.aws-ap-northeast-1.turso.io",
        auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTM5Nzg0NjYsImlkIjoiY2FmOTgzZDQtZTkyZS00MTlkLTgzMjgtYTBhM2UxZTc3ZGRmIiwicmlkIjoiNjhiNGMyODgtZjBhMi00MzYwLTg0MTctNDAzNjE3YmE0YjkyIn0.I0cd3UsLdvC9w8zy7HFONwH9UEqSGZidTE-Sp8z1fFsEWOrkW-CO63qeDZJpc8i5DcoiVPEGrcmrl2puVGvmDg"
    )
    # conn = sqlite3.connect('WattSaver.db')
    return conn

def check_user_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM User")
    rows = cur.fetchall()

    for row in rows:
        print(row)
    conn.close()
    

@app.route("/")

# beranda
@app.route('/index')
def index():
    return render_template("index.html")

# logged in status
@app.context_processor
def inject_logged_in():
    return dict(logged_in =('username' in session))

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']

        # connect db
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM User WHERE user_name=? AND password=?', (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username']= username
            return redirect(url_for('index'))
        else:
            flash('nama pengguna  atau password tidak sesuai')

    return render_template('login.html')


# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username = request.form['username'] # name atribut
        password = request.form['password']
        email = request.form['email']

        if len(password) < 5:
            flash("Password minimal 5 karakter")
            return render_template('register.html')
        
        # connect db
        conn = get_db()
        cur = conn.cursor()
        
        # check duplicate account
        cur.execute('SELECT * FROM User WHERE user_name=?', (username,))
        account_exist = cur.fetchone() # row from database
        if account_exist:
            conn.close()
            flash('Akun sudah ada, silahkan login')
            return render_template('register.html')

        cur.execute('INSERT INTO User(user_name, email, password) VALUES (?,?,?)', (username, email,password))
        conn.commit()
        conn.close()
        check_user_db()
        flash('Registrasi berhasil! silahkan login')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/analisis.html')
def analisis():

    return render_template("analisis.html")

@app.route('/edit.html')
def edit():
    return render_template('edit.html')

@app.route('/history.html')
def history():
    return render_template('history.html')

if __name__ == "__main__":
    # serve(app, host= "0.0.0.0", port=8000)
    app.run(debug=True)