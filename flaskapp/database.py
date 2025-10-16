import os, csv
import pymysql

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
    path = os.path.join(os.path.expanduser("~"), "diplomacy-lab-password.txt")
    with open(path) as fh:
        return fh.read().strip()


DB_PASSWORD = load_password()

def get_connection():
    """ Returns a connection to the database. """
    return pymysql.connect(
        host="db.luddy.indiana.edu",
        user="dosdl_coschul",
        password=DB_PASSWORD,
        database="dosdl_coschul",
        cursorclass=pymysql.cursors.DictCursor,
    )

def initialize_db():
    """ Initializes the database with the required tables. """
    conn = get_connection()

    _companies = """
    CREATE TABLE companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        name_slug VARCHAR(100),
        space_score INT
    ) ENGINE = InnoDB;
    """

    with conn.cursor() as curr:
        # Delete the tables if they already exist
        curr.execute("DROP TABLE IF EXISTS companies")

        # Add them again
        curr.execute(_companies)

    conn.commit()
    conn.close()

    # Add the companies csv data to the database
    with open("companies.csv") as csvf:
        companies = list(csv.DictReader(csvf))

        for row in companies:
            add_company(row)

# ============================
# ===== Company-Specific =====
# ============================

def add_company(company: dict) -> None:
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute(
            """
            INSERT INTO companies
                (name, name_slug, space_score)
            VALUES
                (%s, %s, %s)
            """,
            (company["name"], company["name_slug"], company["space_score"])
        )
    conn.commit()
    conn.close()

def get_companies() -> list[dict]:
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("SELECT * FROM companies")
        companies = curr.fetchall()
    conn.close()
    return companies