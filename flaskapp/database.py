import csv, json, math, os

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

def get_total_space_scores():
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total = sum([1 for row in reader if row["space_score"]])
    return total

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
    # Use a fixed fieldnames list matching your CSV header
    fieldnames = [
        'user_name', 'org_name', 'company_name', 'location', 'chinese_name', 'english_translation',
        'unofficial_registry_shareholders', 'unofficial_registry_ubo', 'affiliates', 'licenses',
        'admin_penalties', 'icp_registration', 'branches', 'official_scope', 'official_legal',
        'official_penalties', 'official_licenses', 'unified_social_credit_code', 'company_website',
        'domain_info', 'exchange_disclosures', 'export_controls', 'sanctions', 'military_connection',
        'patents_standards', 'government_procurement', 'dish_name', 'dish_coordinates',
        'spectrum_registration', 'unoosa_filings', 'etc_reports', 'uscc_reports', 'casc_reports',
        'social_network_platform', 'social_network_link', 'analyst_notes', 'current_date', 'date_last_edited'
    ]
    file_exists = os.path.isfile("companies.csv")
    write_header = not file_exists or os.path.getsize("companies.csv") == 0
    with open("companies.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(company)

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
            # Generate and update space_score and classification BEFORE writing to CSV
            company['space_score'], company['space_classification'], company['vector_string'] = generate_space_score(company)
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

def generate_space_score(company):
    """
    This function follows '2.3 SPACE Scoring Rubric' from the research strategy documentation.\n
    PARAMATER: company_name (str): The name of the company for which to generate the space score.\n
    RETURNS: (SPACE, classification, vector_string)\n
    WHERE: SPACE (int): An int [0, 10] representing the SPACE score.\n
    WHERE: classification (str): A string representing the risk classification based on the SPACE score.\n
    WHERE: vector_string (str): A string representing the vectorized form of the company's risk profile.
    """

    # First, we need to access the json file with the values for each criterion
    with open("space-criterion.json", "r", encoding="utf-8") as f:
        criteria_values = json.load(f)
        
        # Now we just grab the specific values for each criterion
        # Impact
        i1 = criteria_values["impact_I"]["i1_weights"][company['i1_sectoral_criticality']]
        i2 = criteria_values["impact_I"]["i2_weights"][company['i2_systemic_dependancy']]
        i3 = criteria_values["impact_I"]["i3_weights"][company['i3_replacement_cost_and_time']]
        i4 = criteria_values["impact_I"]["i4_weights"][company['i4_spillover_and_escalation_potential']]

        # Threat
        t1 = criteria_values["threat_T"]["t1_weights"][company['t1_state_alignment_and_control']]
        t2 = criteria_values["threat_T"]["t2_weights"][company['t2_strategic_intent_and_mcf_posture']]
        t3 = criteria_values["threat_T"]["t3_weights"][company['t3_operational_capability_and_technical_maturity']]
        t4 = criteria_values["threat_T"]["t4_weights"][company['t4_behavioral_and_historical_indicators']]

        # Vulnerability
        v1 = criteria_values["vulnerability_V"]["v1_weights"][company['v1_dependency_depth']]
        v2 = criteria_values["vulnerability_V"]["v2_weights"][company['v2_proximity_and_access']]
        v3 = criteria_values["vulnerability_V"]["v3_weights"][company['v3_opacity_and_assurance_deficit']]
        v4 = criteria_values["vulnerability_V"]["v4_weights"][company['v4_interoperability_hooks']]

        # Environmental Modifiers
        e1 = company['e1_mission_criticality_content_type']
        e2 = company['e2_existing_countermeasures']

        # Supplemental Context
        s1 = criteria_values["supplemental_context_S"]["s_weights"][company['supplemental_disputed_data']]

        # Now we grab the I, T, and V weights
        i1_weight = criteria_values['weights_bounds_constants']['i1_weight']
        i2_weight = criteria_values['weights_bounds_constants']['i2_weight']
        i3_weight = criteria_values['weights_bounds_constants']['i3_weight']
        i4_weight = criteria_values['weights_bounds_constants']['i4_weight']

        t1_weight = criteria_values['weights_bounds_constants']['t1_weight']
        t2_weight = criteria_values['weights_bounds_constants']['t2_weight']
        t3_weight = criteria_values['weights_bounds_constants']['t3_weight']
        t4_weight = criteria_values['weights_bounds_constants']['t4_weight']

        v1_weight = criteria_values['weights_bounds_constants']['v1_weight']
        v2_weight = criteria_values['weights_bounds_constants']['v2_weight']
        v3_weight = criteria_values['weights_bounds_constants']['v3_weight']
        v4_weight = criteria_values['weights_bounds_constants']['v4_weight']

        # Now we can actually calculate the SPACE sore

        k = criteria_values['weights_bounds_constants']['k']

        I = (i1 * i1_weight) + (i2 * i2_weight) + (i3 * i3_weight) + (i4 * i4_weight)
        T = (t1 * t1_weight) + (t2 * t2_weight) + (t3 * t3_weight) + (t4 * t4_weight)
        V = (v1 * v1_weight) + (v2 * v2_weight) + (v3 * v3_weight) + (v4 * v4_weight)
        E = float(e1) + float(e2)
        S = float(s1)

        
        SPACE = 10 * (1 - (math.e ** (-k * I * T * V * E * S)))
        # NOTE: SPACE = 10 * 1 - e ^ ((-k) * I * T * V * E * S)
        ###SPACE = 10 * (1 - (math.e ** -(k * I * T * V * E * S)))
        SPACE = round(SPACE, 1)

        # Now we need to classify the SPACE score into its risk assesment range

        if SPACE >= 0.0 and SPACE <= 3.9:
            classification = "Low Risk"
        elif SPACE >= 4.0 and SPACE <= 6.9:
            classification = "Moderate Risk"
        elif SPACE >= 7.0 and SPACE <= 8.9:
            classification = "High Risk"
        else:
            classification = "Critical Risk"

        # For housekeeping purposes, let's add the ITVES values to the csv here
        ITVES_data = {
            'I_value': round(I, 2),
            'T_value': round(T, 2),
            'V_value': round(V, 2),
            'E_value': round(E, 2),
            'S_value': round(S, 2)
        }

        # Now let's make the vector string
        vector_string = generate_vector_string(ITVES_data, SPACE)

        # Finally, we can return the SPACE score and classification
        print(SPACE, classification)
        return SPACE, classification, vector_string


def generate_vector_string(ITVES_data, space_score):
    return f"SPACE:{space_score}/I:C({ITVES_data['I_value']})/T:H({ITVES_data['T_value']})/V:H({ITVES_data['V_value']})/E:Up({ITVES_data['E_value']})/S:LoConf({ITVES_data['S_value']})"

def set_space_score(company_name, space_score):
    companies = get_companies_csv()

    for company in companies:
        if company['company_name'] == company_name:
            company['space_score'] = space_score
            break