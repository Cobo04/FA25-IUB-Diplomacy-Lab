# ———————————no sql connection?———————————
# ⠀⣞⢽⢪⢣⢣⢣⢫⡺⡵⣝⡮⣗⢷⢽⢽⢽⣮⡷⡽⣜⣜⢮⢺⣜⢷⢽⢝⡽⣝
# ⠸⡸⠜⠕⠕⠁⢁⢇⢏⢽⢺⣪⡳⡝⣎⣏⢯⢞⡿⣟⣷⣳⢯⡷⣽⢽⢯⣳⣫⠇
# ⠀⠀⢀⢀⢄⢬⢪⡪⡎⣆⡈⠚⠜⠕⠇⠗⠝⢕⢯⢫⣞⣯⣿⣻⡽⣏⢗⣗⠏⠀
# ⠀⠪⡪⡪⣪⢪⢺⢸⢢⢓⢆⢤⢀⠀⠀⠀⠀⠈⢊⢞⡾⣿⡯⣏⢮⠷⠁⠀⠀
# ⠀⠀⠀⠈⠊⠆⡃⠕⢕⢇⢇⢇⢇⢇⢏⢎⢎⢆⢄⠀⢑⣽⣿⢝⠲⠉⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⡿⠂⠠⠀⡇⢇⠕⢈⣀⠀⠁⠡⠣⡣⡫⣂⣿⠯⢪⠰⠂⠀⠀⠀⠀
# ⠀⠀⠀⠀⡦⡙⡂⢀⢤⢣⠣⡈⣾⡃⠠⠄⠀⡄⢱⣌⣶⢏⢊⠂⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⢝⡲⣜⡮⡏⢎⢌⢂⠙⠢⠐⢀⢘⢵⣽⣿⡿⠁⠁⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠨⣺⡺⡕⡕⡱⡑⡆⡕⡅⡕⡜⡼⢽⡻⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⣼⣳⣫⣾⣵⣗⡵⡱⡡⢣⢑⢕⢜⢕⡝⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⣴⣿⣾⣿⣿⣿⡿⡽⡑⢌⠪⡢⡣⣣⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⡟⡾⣿⢿⢿⢵⣽⣾⣼⣘⢸⢸⣞⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠁⠇⠡⠩⡫⢿⣝⡻⡮⣒⢽⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ————————————————————————————————————————

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
    if 'logged_in' in session and session['logged_in']:
        return render_template("documents.html")
    else:
        return redirect(url_for("login"))

@app.route("/companies")
def companies():
    if 'logged_in' in session and session['logged_in']:
        companies = db.get_companies_csv()
        return render_template("companies.html", companies=companies)
    else:
        return redirect(url_for("login"))

@app.route("/select-company", methods=["GET", "POST"])
def select_company():
    if 'logged_in' in session and session['logged_in']:
        companies = db.get_companies_csv()
        return render_template("select_company.html", companies=companies)
    else:
        return redirect(url_for("login"))

@app.route("/admin")
def admin():
    if 'logged_in' in session and session['logged_in']:
        return render_template("admin.html")
    else:
        return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        total_companies = db.get_total_companies()
        return render_template("dashboard.html", total_companies=total_companies)
    else:
        return redirect(url_for("login"))

@app.route("/server-stats")
def server_stats():
    if 'logged_in' in session and session['logged_in']:
        return render_template("server_stats.html")
    else:
        return redirect(url_for("login"))

@app.route("/add-score", methods=["GET", "POST"])
def add_score():
    if 'logged_in' in session and session['logged_in']:
        if request.method == "POST":
            company_name = request.form['company_name']
            company = db.get_company_by_name(company_name)
            return render_template("add-score.html", company=company)
        return render_template("select_company.html")
    else:
        return redirect(url_for("login"))

@app.route("/add-company", methods=["GET", "POST"])
def add_company():
    if 'logged_in' in session and session['logged_in']:
        if request.method == "POST":
            # process form data here
            user_name = request.form['user_name']
            org_name = request.form['org_name']
            company_name = request.form['company_name']
            location = request.form['location']
            chinese_name = request.form['chinese_name']
            english_translation = request.form['english_translation']
            unofficial_registry_shareholders = request.form['unofficial_registry_shareholders']
            unofficial_registry_ubo = request.form['unofficial_registry_ubo']
            affiliates = request.form['affiliates']
            licenses = request.form['licenses']
            admin_penalties = request.form['admin_penalties']
            icp_registration = request.form['icp_registration']
            branches = request.form['branches']
            official_scope = request.form['official_scope']
            official_legal = request.form['official_legal']
            official_penalties = request.form['official_penalties']
            official_licenses = request.form['official_licenses']
            unified_social_credit_code = request.form['unified_social_credit_code']
            company_website = request.form['company_website']
            domain_info = request.form['domain_info']
            exchange_disclosures = request.form['exchange_disclosures']
            export_controls = request.form['export_controls']
            sanctions = request.form['sanctions']
            military_connection = request.form['military_connection']
            patents_standards = request.form['patents_standards']
            government_procurement = request.form['government_procurement']
            dish_name = request.form['dish_name']
            dish_coordinates = request.form['dish_coordinates']
            spectrum_registration = request.form['spectrum_registration']
            unoosa_filings = request.form['unoosa_filings']
            etc_reports = request.form['etc_reports']
            uscc_reports = request.form['uscc_reports']
            casc_reports = request.form['casc_reports']
            social_network_platform = request.form['social_network_platform']
            social_network_link = request.form['social_network_link']
            analyst_notes = request.form['analyst_notes']

            company = {
                "user_name": user_name,
                "org_name": org_name,
                "company_name": company_name,
                "location": location,
                "chinese_name": chinese_name,
                "english_translation": english_translation,
                "unofficial_registry_shareholders": unofficial_registry_shareholders,
                "unofficial_registry_ubo": unofficial_registry_ubo,
                "affiliates": affiliates,
                "licenses": licenses,
                "admin_penalties": admin_penalties,
                "icp_registration": icp_registration,
                "branches": branches,
                "official_scope": official_scope,
                "official_legal": official_legal,
                "official_penalties": official_penalties,
                "official_licenses": official_licenses,
                "unified_social_credit_code": unified_social_credit_code,
                "company_website": company_website,
                "domain_info": domain_info,
                "exchange_disclosures": exchange_disclosures,
                "export_controls": export_controls,
                "sanctions": sanctions,
                "military_connection": military_connection,
                "patents_standards": patents_standards,
                "government_procurement": government_procurement,
                "dish_name": dish_name,
                "dish_coordinates": dish_coordinates,
                "spectrum_registration": spectrum_registration,
                "unoosa_filings": unoosa_filings,
                "etc_reports": etc_reports,
                "uscc_reports": uscc_reports,
                "casc_reports": casc_reports,
                "social_network_platform": social_network_platform,
                "social_network_link": social_network_link,
                "analyst_notes": analyst_notes,
            }

            return redirect(url_for("companies"))
        return render_template("add-company.html")
    else:
        return redirect(url_for("login"))

@app.route("/map")
def map():
    if 'logged_in' in session and session['logged_in']:
        return render_template("map.html")
    else:
        return redirect(url_for("login"))

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

# ===== Don't worry about it =====

@app.route("/jupiter")
def jupiter():
    if 'logged_in' in session and session['logged_in']:
        return render_template("jupiter.html")
    else:
        return redirect(url_for("login"))