from flask import Flask, render_template, request
# from waitress import serve
import libsql_client

app = Flask(__name__)
# koneksi turso
# conn = libsql_client.connect(
#     url="libsql://wattsaver-shiroewt.aws-ap-northeast-1.turso.io",
#     auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTM5Nzg0NjYsImlkIjoiY2FmOTgzZDQtZTkyZS00MTlkLTgzMjgtYTBhM2UxZTc3ZGRmIiwicmlkIjoiNjhiNGMyODgtZjBhMi00MzYwLTg0MTctNDAzNjE3YmE0YjkyIn0.I0cd3UsLdvC9w8zy7HFONwH9UEqSGZidTE-Sp8z1fFsEWOrkW-CO63qeDZJpc8i5DcoiVPEGrcmrl2puVGvmDg"
# )


@app.route("/")

# beranda
@app.route('/index')
def index():
    return render_template("index.html")

# login
@app.route('/login')
def login():
    return render_template('login.html')

# register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/analisis.html')
def analisis():
    # backend code
    return render_template(
        "analisis.html"
    )

@app.route('/edit.html')
def edit():
    return render_template('edit.html')

@app.route('/history.html')
def history():
    return render_template('history.html')

if __name__ == "__main__":
    # serve(app, host= "0.0.0.0", port=8000)
    app.run(debug=True)