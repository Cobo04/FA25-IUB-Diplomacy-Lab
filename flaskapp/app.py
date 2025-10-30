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

@app.route("/documents")
def documents():
    return render_template("documents.html")

@app.route("/companies")
def companies():
    if 'logged_in' in session and session['logged_in']:
        companies = db.get_companies_csv()
        return render_template("companies.html", companies=companies)
    else:
        return redirect(url_for('login'))

@app.route("/admin")
def admin():
    if 'logged_in' in session and session['logged_in']:
        return render_template("admin.html")
    else:
        return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        total_companies = db.get_total_companies()
        return render_template("dashboard.html", total_companies=total_companies)
    else:
        return redirect(url_for('login'))
    
@app.route("/server-stats")
def server_stats():
    if 'logged_in' in session and session['logged_in']:
        return render_template("server_stats.html")
    else:
        return redirect(url_for('login'))

@app.route("/add-score", methods=["GET", "POST"])
def add_score():
    if 'logged_in' in session and session['logged_in']:
        return render_template("add-score.html")
    else:
        return redirect(url_for('login'))

@app.route("/add-company", methods=["GET", "POST"])
def add_company():
    if 'logged_in' in session and session['logged_in']:
        
        if request.method == "POST":
            # process form data
            user_name = request.form.get("user_name")
            org_name = request.form.get("org_name")
            company_name = request.form.get("company_name")
            # additional fields would be processed here

            new_company = {
                "name": company_name,
                "name_slug": company_name.lower().replace(" ", "-"),
                "user_name": user_name,
                "org_name": org_name,
                "space_score": 0  # default score; would be calculated based on additional fields
            }

            db.add_company(new_company)

            return redirect(url_for('companies'))
        return render_template("add-company.html")
    else:
        return redirect(url_for('login'))

@app.route("/map")
def map():
    if 'logged_in' in session and session['logged_in']:
        return render_template("map.html")
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