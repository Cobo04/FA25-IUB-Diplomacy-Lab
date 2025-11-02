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
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(row)
    return companies

# ============================
# ===== Company-Specific =====
# ============================

def get_total_companies():
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        total = sum(1 for row in reader) - 1  # subtract 1 for header
    return total

def get_company_by_name(name):
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['company_name'] == name:
                return row
    return None

def add_company_to_csv(company):
    with open("companies.csv", "a", newline='', encoding='utf-8') as f:
        fieldnames = ['user_name', 
                      'org_name', 
                      'company_name',
                      'location',
                      'chinese_name',
                      'english_translation',
                      'unofficial_registry_shareholders',
                      'unofficial_registry_ubo',
                      'affiliates',
                      'licenses',
                      'admin_penalties',
                      'icp_registration',
                      'branches',
                      'official_scope',
                      'official_legal',
                      'official_penalties',
                      'official_licenses',
                      'unified_social_credit_code',
                      'company_website',
                      'domain_info',
                      'exchange_disclosures',
                      'export_controls',
                      'sanctions',
                      'military_connection',
                      'patents_standards',
                      'government_procurement',
                      'dish_name',
                      'dish_coordinates',
                      'spectrum_registration',
                      'unoosa_filings',
                      'etc_reports',
                      'uscc_reports',
                      'casc_reports',
                      'social_network_platform',
                      'social_network_link',
                      'analyst_notes',
                      'current_date',
                      'date_last_edited'
                      ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)

# ================================
# ===== Space Score-Specific =====
# ================================

def add_space_score_to_company(company_name, space_score_data):
    companies = get_companies_csv()
    updated = False
    for company in companies:
        if company['company_name'] == company_name:
            for key, value in space_score_data.items():
                company[key] = value
            updated = True
            break
    if updated:
        # Overwrite the CSV with the updated companies list
        if companies:
            fieldnames = companies[0].keys()
            with open("companies.csv", "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(companies)

def set_space_score(company_name, space_score):
    companies = get_companies_csv()

    for company in companies:
        if company['company_name'] == company_name:
            company['space_score'] = space_score
            break