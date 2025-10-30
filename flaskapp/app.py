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
from flask import Flask, render_template, request, redirect, url_for

# database requirements
from flaskapp import database as db

# ===== Flask Initialization =====

app = Flask(__name__)

# ===== Routes =====

@app.route("/")
def render_index():
    return render_template("index.html")

@app.route("/documents")
def documents():
    return render_template("documents.html")

@app.route("/companies")
def companies():
    companies = db.get_companies_csv()
    return render_template("companies.html", companies=companies)


@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/dashboard")
def dashboard():
    total_companies = db.get_total_companies()
    return render_template("dashboard.html", total_companies=total_companies)

@app.route("/server-stats")
def server_stats():
    return render_template("server_stats.html")

@app.route("/add-score", methods=["GET", "POST"])
def add_score():
    return render_template("add-score.html")

@app.route("/add-company", methods=["GET", "POST"])
def add_company():
    return render_template("add-company.html")

@app.route("/map")
def map():
    return render_template("map.html")

# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "GET":
#         return render_template("login.html")
#     else:
#         password = request.form.get("password")
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()

#         if db.validate_password(hashed_password):
#             session['logged_in'] = True
#             return redirect(url_for('dashboard'))
#         else:
#             return render_template("login.html")