import csv, json, math, os
from datetime import datetime
from flaskapp.vector import vector_stringify
from flaskapp.certainty import compute_coverage_quality, compute_certainty, classify_certainty, compute_ibeam

import matplotlib
matplotlib.use("Agg")  # headless backend for server (I hope this works, sorry Cohen, might require a bit of troubleshooting 😇)
import matplotlib.pyplot as plt
# FIXME: `pip install matplotlib`

# NOTE TO COHEN:
## auto_report_template.html only generates a report for one company (I misunderstood this at first).
## Once our certainty + I-beam system is finished, we can easily build a /report/all route that generates a full multi-company PDF.
## Imagine a scatter plot where each company is a point at its SPACE score, with an I-beam extending upward/downward to show uncertainty.
## Everything for this route is already implemented on the backend, we just need the Flask route + LaTeX template (which I can do quickly).


# this is cohen's message written in blood
# THIS IS NOT SECURE IN ANY WAY, SWITCH TO THE RDC DATABASE ASAP

# ============================
# ===== Helper Functions =====
# ============================

def validate_password(password):
    increment_server_api_calls()
    # get the password hash from the secret.txt file
    with open("flaskapp/secret.txt", "r") as f:
        stored_password_hash = f.read().strip()
    return password == stored_password_hash

def get_secret_key():
    increment_server_api_calls()
    with open("flaskapp/secret_key.txt", "r") as f:
        return f.read().strip()

# =============================
# ===== Server Statistics =====
# =============================

def get_company_blame():
    increment_server_api_calls()
    """Returns the number of companies analyzed by each member of the group"""
    blame = {
        "Cameron": 0,
        "Cohen": 0,
        "Eva": 0,
        "Leah": 0,
        "Reagan": 0
    }
    with open("companies.csv", "r", encoding="utf-8") as fhead:
        reader = csv.DictReader(fhead, delimiter='~')
        for row in reader:
            blame[row['user_name']] += 1

    return blame

def get_server_connection():
    increment_server_api_calls()
    return "ACTIVE", "blame-awesome"

def get_map_connection():
    increment_server_api_calls()
    return "ACTIVE", "blame-awesome"

def get_maltego_connection():
    increment_server_api_calls()
    return "LOST", "welcome-warning"

def get_server_time():
    increment_server_api_calls()
    return datetime.now().strftime("%H:%M:%S")

def get_db_connection():
    increment_server_api_calls()
    connection = True
    with open("companies.csv", "r", encoding="utf-8") as fhead:
        if fhead:
            connection = False
    if connection:
        return "LOST", "welcome-warning"
    return "ACTIVE", "blame-awesome"

def get_total_api_calls():
    # open the json server file and read the total_api_calls value
    with open("server_data.json", "r") as f:
        data = json.load(f)
        return data.get("total_api_calls", 0)

def increment_server_api_calls():
    # open the json server file and read the total_api_calls value
    with open("server_data.json", "r") as f:
        data = json.load(f)
    total_api_calls = data.get("total_api_calls", 0)
    total_api_calls += 1
    data["total_api_calls"] = total_api_calls
    # write the updated value back to the json file
    with open("server_data.json", "w") as f:
        json.dump(data, f)

# =========================
# ===== Intialization =====
# =========================

def get_companies_csv():
    increment_server_api_calls()
    companies = []
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter='~')
        for row in reader:
            companies.append(row)
    return companies

def get_total_space_scores():
    increment_server_api_calls()
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter='~')
        total = sum([1 for row in reader if row["space_score"]])
    return total

# ============================
# ===== Company-Specific =====
# ============================

def edit_company_by_name(name, updated_company):
    increment_server_api_calls()
    companies = get_companies_csv()
    fieldnames = [
        'user_name', 'org_name', 'institution_name', 'location', 'chinese_name', 'english_translation',
        'unofficial_registry_shareholders', 'unofficial_registry_ubo', 'affiliates', 'licenses',
        'admin_penalties', 'icp_registration', 'branches', 'official_scope', 'official_legal',
        'official_penalties', 'official_licenses', 'unified_social_credit_code', 'company_website',
        'domain_info', 'exchange_disclosures', 'export_controls', 'sanctions', 'military_connection',
        'patents_standards', 'government_procurement', 'dish_name', 'dish_coordinates',
        'spectrum_registration', 'unoosa_filings', 'etc_reports', 'uscc_reports', 'casc_reports',
        'social_network_platform', 'social_network_link', 'analyst_notes', 'current_date', 'date_last_edited',
        'i1_sectoral_criticality', 'i2_systemic_dependancy', 'i3_replacement_cost_and_time', 'i4_spillover_and_escalation_potential',
        't1_state_alignment_and_control', 't2_strategic_intent_and_mcf_posture', 't3_operational_capability_and_technical_maturity', 't4_behavioral_and_historical_indicators',
        'v1_dependency_depth', 'v2_proximity_and_access', 'v3_opacity_and_assurance_deficit', 'v4_interoperability_hooks',
        'e1_mission_criticality_content_type', 'e2_existing_countermeasures', 'supplemental_disputed_data',

        # SPACE score outputs
        'space_score', 'space_classification', 'vector_string',

        # Certainty + IBEAM outputs
        'certainty_score', 'certainty_band',
        'ibeam_center', 'ibeam_lower', 'ibeam_upper', 'ibeam_half_width'
    ]
    # NOTE: I changed these fieldnames (added some), but I tried to make it easy to revert if I broke something
    # the functions in this file populate the new fields, so we shouldn't need to update routes (the ones that did need updating, I updated)
    
    found = False
    for i, company in enumerate(companies):
        # Robust match: ignore case and strip whitespace
        if company['english_translation'].strip().lower() == name.strip().lower():
            for key, value in updated_company.items():
                company[key] = value
            for key in fieldnames:
                if key not in company:
                    company[key] = ''
            companies[i] = company
            found = True
            break
    with open("companies.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='~')
        writer.writeheader()
        writer.writerows(companies)

def delete_company_by_name(name):
    increment_server_api_calls()
    companies = get_companies_csv()
    companies = [company for company in companies if company['english_translation'] != name]
    # Always overwrite the CSV, even if empty (write just the header if empty)
    fieldnames = [
        'user_name', 'org_name', 'institution_name', 'location', 'chinese_name', 'english_translation',
        'unofficial_registry_shareholders', 'unofficial_registry_ubo', 'affiliates', 'licenses',
        'admin_penalties', 'icp_registration', 'branches', 'official_scope', 'official_legal',
        'official_penalties', 'official_licenses', 'unified_social_credit_code', 'company_website',
        'domain_info', 'exchange_disclosures', 'export_controls', 'sanctions', 'military_connection',
        'patents_standards', 'government_procurement', 'dish_name', 'dish_coordinates',
        'spectrum_registration', 'unoosa_filings', 'etc_reports', 'uscc_reports', 'casc_reports',
        'social_network_platform', 'social_network_link', 'analyst_notes', 'current_date', 'date_last_edited',
        'i1_sectoral_criticality', 'i2_systemic_dependancy', 'i3_replacement_cost_and_time', 'i4_spillover_and_escalation_potential',
        't1_state_alignment_and_control', 't2_strategic_intent_and_mcf_posture', 't3_operational_capability_and_technical_maturity', 't4_behavioral_and_historical_indicators',
        'v1_dependency_depth', 'v2_proximity_and_access', 'v3_opacity_and_assurance_deficit', 'v4_interoperability_hooks',
        'e1_mission_criticality_content_type', 'e2_existing_countermeasures', 'supplemental_disputed_data',

        # SPACE score outputs
        'space_score', 'space_classification', 'vector_string',

        # Certainty + IBEAM outputs
        'certainty_score', 'certainty_band',
        'ibeam_center', 'ibeam_lower', 'ibeam_upper', 'ibeam_half_width'
    ]

    with open("companies.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='~')
        writer.writeheader()
        if companies:
            writer.writerows(companies)

def get_total_companies():
    increment_server_api_calls()
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter='~')
        total = sum(1 for row in reader) - 1  # subtract 1 for header
    return total

def get_company_by_name(name):
    increment_server_api_calls()
    with open("companies.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter='~')
        for row in reader:
            if row['english_translation'] == name:
                return row
    return None

def add_company_to_csv(company):
    increment_server_api_calls()
    # Use a fixed fieldnames list matching your CSV header
    fieldnames = [
        'user_name', 'org_name', 'institution_name', 'location', 'chinese_name', 'english_translation',
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
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='~')
        if write_header:
            writer.writeheader()
        writer.writerow(company)

# ================================
# ===== Space Score-Specific =====
# ================================

def add_space_score_to_company(company_name, space_score_data):
    increment_server_api_calls()
    companies = get_companies_csv()
    updated = False
    for company in companies:
        if company['english_translation'] == company_name:
            for key, value in space_score_data.items():
                company[key] = value
            # Generate and update space_score and classification BEFORE writing to CSV
            ## NOW INCLUDES CERTAINTY AND IBEAM
            #company['space_score'], company['space_classification'], company['vector_string'] = generate_space_score(company)
            SPACE, classification, vector_string, C, C_band, ibeam = generate_space_score(company)

            company['space_score'] = f"{SPACE:.1f}"
            company['space_classification'] = classification
            company['vector_string'] = vector_string

            # new fields (ADDED):
            company['certainty_score'] = f"{C:.3f}"
            company['certainty_band'] = C_band

            company['ibeam_center'] = f"{ibeam['center']:.2f}"
            company['ibeam_lower'] = f"{ibeam['lower']:.2f}"
            company['ibeam_upper'] = f"{ibeam['upper']:.2f}"
            company['ibeam_half_width'] = f"{ibeam['half_width']:.2f}"
            
            # set the time for the last edit
            last_edited = str(datetime.now().strftime("%m/%d/%Y"))
            company['date_last_edited'] = last_edited
            updated = True
            break
    if updated:
        # Overwrite the CSV with the updated companies list
        if companies:
            fieldnames = companies[0].keys()
            with open("companies.csv", "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='~')
                writer.writeheader()
                writer.writerows(companies)

def generate_space_score(company):
    increment_server_api_calls()
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

        # Environmental Modifiers (E) normalization
        E1_map = {
            "High Mission Criticality": 1.1,
            "Moderate": 1.0,
            "Low Criticality / Strong Mitigations": 0.9,
            "None": 1.0
        }

        # IMPORTANT:
        # Convert company['e1_mission_criticality_content_type'] and company['e2_existing_countermeasures']
        # to their mapped values (they must match keys exactly)
        e1_value = E1_map.get(company['e1_mission_criticality_content_type'], 1.0)
        e2_value = E1_map.get(company['e2_existing_countermeasures'], 1.0)

        # Multiply, don't add, and cap to [0.8, 1.2] (check whitepaper)
        E = max(0.8, min(1.2, e1_value * e2_value))

        # Supplemental (S) normalization
        S_map = criteria_values["supplemental_context_S"]["s_weights"]
        S = float(S_map.get(company['supplemental_disputed_data'], 1.0))

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

        ###E = float(e1) + float(e2)
        ###S = float(s1)

        # NOTE: I still tweaked this a bit for clarity, but the ** notation worked fine
        SPACE = 10 * (1 - math.exp(-k * I * T * V * E * S))
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

        # ============================
        # Certainty + I-beam logic
        # ============================

        # Pull weights into the shape expected by compute_coverage_quality
        weights = {
            "I": {
                "i1": i1_weight,
                "i2": i2_weight,
                "i3": i3_weight,
                "i4": i4_weight,
            },
            "T": {
                "t1": t1_weight,
                "t2": t2_weight,
                "t3": t3_weight,
                "t4": t4_weight,
            },
            "V": {
                "v1": v1_weight,
                "v2": v2_weight,
                "v3": v3_weight,
                "v4": v4_weight,
            },
        }

        # Observed flags inferred from existing ratings
        # FIXME: simple default idea: anything not "None" counts as observed = 1.0 (WE NEED TO FIGURE THIS BIT OUT, DOES THIS LOGIC WORK?)
        def observed_flag(value: str) -> float:
            return 0.0 if value == "None" else 1.0

        observed = {
            "I": {
                "i1": observed_flag(company['i1_sectoral_criticality']),
                "i2": observed_flag(company['i2_systemic_dependancy']),
                "i3": observed_flag(company['i3_replacement_cost_and_time']),
                "i4": observed_flag(company['i4_spillover_and_escalation_potential']),
            },
            "T": {
                "t1": observed_flag(company['t1_state_alignment_and_control']),
                "t2": observed_flag(company['t2_strategic_intent_and_mcf_posture']),
                "t3": observed_flag(company['t3_operational_capability_and_technical_maturity']),
                "t4": observed_flag(company['t4_behavioral_and_historical_indicators']),
            },
            "V": {
                "v1": observed_flag(company['v1_dependency_depth']),
                "v2": observed_flag(company['v2_proximity_and_access']),
                "v3": observed_flag(company['v3_opacity_and_assurance_deficit']),
                "v4": observed_flag(company['v4_interoperability_hooks']),
            },
        }

        # Quality defaults (for now: assume all evidence is high quality = 1.0)
        # FIXME: later we can replace these with per-submetric quality fields (i1_quality, etc.), based on 'ANALYST NOTE' field, maybe?
        ## until then, this isn't the best implementation, but I assume we used all the official/government sources, so fair baseline, I think
        quality = {
            "I": {k: 1.0 for k in ["i1", "i2", "i3", "i4"]},
            "T": {k: 1.0 for k in ["t1", "t2", "t3", "t4"]},
            "V": {k: 1.0 for k in ["v1", "v2", "v3", "v4"]},
        }

        coverage, quality_val = compute_coverage_quality(observed, quality, weights)
        C = compute_certainty(coverage, quality_val)
        C_band = classify_certainty(C)

        # I-beam around SPACE
        ibeam = compute_ibeam(SPACE, C, u=0.3)

        # Finally, we can return the SPACE score and classification (and C, C_band, and ibeam - ADDED)
        return SPACE, classification, vector_string, C, C_band, ibeam
        #return SPACE, classification, vector_string


def get_weight_stats(company_name):
    # Find the total number of Critical, High, Medium, Low, and None for the the given company
    increment_server_api_calls()
    company = get_company_by_name(company_name)
    if not company:
        return None
    weight_stats = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "None": 0
    }

    company_data = [
        company['i1_sectoral_criticality'],
        company['i2_systemic_dependancy'],
        company['i3_replacement_cost_and_time'],
        company['i4_spillover_and_escalation_potential'],
        company['t1_state_alignment_and_control'],
        company['t2_strategic_intent_and_mcf_posture'],
        company['t3_operational_capability_and_technical_maturity'],
        company['t4_behavioral_and_historical_indicators'],
        company['v1_dependency_depth'],
        company['v2_proximity_and_access'],
        company['v3_opacity_and_assurance_deficit'],
        company['v4_interoperability_hooks']
    ]

    for value in company_data:
        if value in weight_stats:
            weight_stats[value] += 1
        
    return weight_stats

def generate_vector_string(ITVES_data, space_score):
    increment_server_api_calls()  # NOTE: do you need this call? I left generate_vector_string() as a wrapper
    # NOTE: if you don't need this API call, scrap this function and call the other one directly (the one from vector.py)

    return vector_stringify(space_score, ITVES_data)
    # NOTE: if you don't need the API call, just call vector_stringify(space_score, ITVES_data) above instead of this function


def set_space_score(company_name, space_score):
    increment_server_api_calls()
    companies = get_companies_csv()

    for company in companies:
        if company['company_name'] == company_name:
            company['space_score'] = space_score
            break


# NOTE: we don't implement this yet, but it's my idea for the final all companies report (thoughts? we'll call it in a loop for each company)
## also, I'll call this in the route, but I wanted to make sure the upper and lower bounds appeared where they should first, if things break,
## the logic to score this is in add_space_score_to_company(), so this MUST be run at least once per company to populate the csv
## I have the logic to generate and add .png files to the per-company report and all-company reports already written, make sure this works, 
## and then I'll drop it in. 
## given this code below, implementation is all front-end (new /edited routes + <img> tag in html to include png + latex implementation)
def plot_ibeam_for_company(company: dict, output_path: str):
    """
    Render a horizontal I-beam visualization for a single company's SPACE score.

    Horizontal axis: 0-10 (SPACE scale)
    One point at center (SPACE score)
    Line extends to lower/upper certainty bounds WITHOUT endpoint caps.

    Parameters
    ----------
    company : dict
        Company row from companies.csv (must contain 'english_translation',
        'space_score', 'ibeam_lower', 'ibeam_upper', 'ibeam_center').
    output_path : str
        File path to save PNG.
    """
    name = company['english_translation']

    try:
        center = float(company.get("ibeam_center", company["space_score"]))
        lower = float(company.get("ibeam_lower", center))
        upper = float(company.get("ibeam_upper", center))
    except (KeyError, ValueError):
        return  # silently skip

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(8, 1.8))

    # Plot horizontal I-beam (no caps, no endpoints)
    plt.hlines(
        y=0, xmin=lower, xmax=upper, linewidth=6
    )
    plt.plot(center, 0, "o", markersize=10)  # center dot

    plt.xlim(0, 10)
    plt.yticks([])

    plt.title(f"SPACE Score Confidence Interval — {name}", fontsize=10)
    plt.xlabel("SPACE Score")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


# NOTE: here's the logic for plotting all I-beams
def plot_all_ibeams(output_path: str = "figures/space_ibeams_all.png"):
    """
    Create a horizontal I-beam plot of SPACE scores for all companies.

    Each company is plotted as a point (SPACE) with an I-beam showing
    [lower, upper] based on certainty.

    Parameters
    ----------
    output_path : str
        Where to save the PNG. Use a path consistent with our LaTeX workflow
        (e.g., 'figures/space_ibeams_all.png').
    """
    companies = get_companies_csv()

    xs = []
    centers = []
    yerr_lower = []
    yerr_upper = []
    labels = []

    for idx, c in enumerate(companies):
        space_str = c.get("space_score", "")
        if not space_str:
            continue  # skip companies without a SPACE score (incomplete data)

        try:
            center = float(c.get("ibeam_center", space_str))
            lower = float(c.get("ibeam_lower", center))
            upper = float(c.get("ibeam_upper", center))
        except ValueError:
            continue  # malformed row, skip

        xs.append(idx)
        centers.append(center)
        yerr_lower.append(center - lower)
        yerr_upper.append(upper - center)
        labels.append(c["english_translation"])

    if not xs:
        return  # nothing to plot

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(max(6, len(xs) * 0.6), 6))
    plt.errorbar(
        xs,
        centers,
        yerr=[yerr_lower, yerr_upper],
        fmt="o",
        capsize=6,
    )

    plt.ylabel("SPACE Score")
    plt.xlabel("Company")
    plt.ylim(0, 10)

    plt.xticks(xs, labels, rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


# NOTE: okay, this will be a pain in the ass but, calling the script locally, ex:
## python -c "from flaskapp import database as db; db.plot_all_ibeams('figures/space_ibeams_all.png')"
## will generate the png file, we just need to copy/paste it somewhere for the final report (and hook it into the latex)
## you're right, including images in latex reports is easy (call per-company for one, and the final report we'll add later)
## I can automate this later if it's good, needs testing first (let me know) - I have 99% of the code written already
## to implement this, but I wanted to make sure the lower, upper bounds appeared first (confirms logic for generation is correct)