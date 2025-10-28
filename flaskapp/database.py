import os, pymysql

# ============================
# ===== Helper Functions =====
# ============================

def validate_password(password):
    # get the password hash from the secret.txt file
    with open("flaskapp/secret.txt", "r") as f:
        stored_password_hash = f.read().strip()
    return password == stored_password_hash

def get_secret_key():
    with open("flaskapp/secret_key.txt", "r") as f:
        return f.read().strip()


# =========================
# ===== Intialization =====
# =========================

def load_password():
    path = os.path.join("flaskapp/diplab-password.txt")
    with open(path) as fh:
        return fh.read().strip()

DB_PASSWORD = load_password()

def get_connection():
    return pymysql.connect(
        host="sasrdsmp01.uits.iu.edu",
        user="diplab25_root",
        password=DB_PASSWORD,
        database="api",
        cursorclass=pymysql.cursors.DictCursor,
    )

def initialize_db():
    conn = get_connection()

    _companies = """
    CREATE TABLE companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        name_slug VARCHAR(255) NOT NULL,
        user_name VARCHAR(255) NOT NULL,
        org_name VARCHAR(255) NOT NULL,
        space_score INT NOT NULL
    );
    """

    with conn.cursor() as cursor:
        #Delete the tables if they exist and recreate them
        cursor.execute("DROP TABLE IF EXISTS companies;")
        cursor.execute(_companies)

    conn.commit()
    conn.close()

# ============================
# ===== Company-Specific =====
# ============================

def add_company(company: dict) -> None:
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = """
        INSERT INTO companies (name, name_slug, user_name, org_name, space_score)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(sql, (
            company["name"],
            company["name_slug"],
            company["user_name"],
            company["org_name"],
            company["space_score"]
        ))
    conn.commit()
    conn.close()