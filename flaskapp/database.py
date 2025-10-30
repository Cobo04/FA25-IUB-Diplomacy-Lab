import csv

# this is cohen's message written in blood
# THIS IS NOT SECURE IN ANY WAY, SWITCH TO THE RDC DATABASE ASAP

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

def get_companies_csv():
    companies = []
    with open("flaskapp/companies.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(row)
    return companies

# ============================
# ===== Company-Specific =====
# ============================

def add_company_to_csv(company_data):
    fieldnames = ["name", "org_name", "company_name", "space_score"]
    with open("flaskapp/companies.csv", "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(company_data)

def get_total_companies():
    with open("flaskapp/companies.csv", "r") as f:
        reader = csv.reader(f)
        total = sum(1 for row in reader) - 1  # subtract 1 for header
    return total