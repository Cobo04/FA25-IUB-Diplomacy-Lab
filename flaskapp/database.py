import os, csv

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

def get_total_companies():
    return len(csv_get_companies())

# =========================
# ===== Intialization =====
# =========================

def load_password():
    path = os.path.join(os.path.expanduser("~"), "diplomacy-lab-password.txt")
    with open(path) as fh:
        return fh.read().strip()


# DB_PASSWORD = load_password()


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

def csv_get_companies() -> list[dict]:
    with open("flaskapp/companies.csv") as csvf:
        companies = list(csv.DictReader(csvf))
    return companies