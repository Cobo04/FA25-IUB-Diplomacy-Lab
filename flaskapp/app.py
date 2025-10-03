# flask requirements
from flask import Flask, render_template, request, redirect, url_for, session
import hashlib

# database requirements
from flaskapp import database as db



# ===== Flask Initialization =====

app = Flask(__name__)
app.secret_key = db.get_secret_key()

# ===== Routes =====

@app.route("/")
def render_index():
    session['logged_in'] = False
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        return render_template("dashboard.html")
    else:
        return redirect(url_for('login'))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        password = request.form.get("password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if db.validate_password(hashed_password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html")