# Implementation for Streamlit-Based Risk Assessment Interface

## 1.0 - Overview:
This document describes the implementation of a Streamlit-based user interface for C2M's Project Risk and Profitability Assessment system. The system leverages a Prolog backend for its core decision logic, which evaluates project risk based on a set of predefined rules and input parameters derived from C2M's internal financial expertise and project specifications. This interface allows users at C2M to easily input project details and receive an immediate risk classification (Low, Medium, or High), along with mitigation suggestions for high-risk projects.
The primary goal is to provide an accessible and user-friendly front-end to the sophisticated, rule-based risk assessment model, ensuring that C2M can efficiently evaluate project viability in line with Swiss architectural industry standards and the firm's financial objectives.

## 2.0 - System Architecture
The system comprises three main components:

    • prolog/risk_rules.pl: The SWI-Prolog knowledge base containing all the decision logic. It defines the assess_risk/8 predicate, which implements the risk classification rules (High, Medium, Low), profit-based override mechanisms, and the risk downgrade hierarchy.
    • utils/prolog_interface.py: A Python module using PySWIP to bridge the gap between the Python application and the Prolog engine. It handles loading the risk_rules.pl file and provides the assess_risk(...) Python function to query the Prolog knowledge base.
    • app.py: The Streamlit application script that provides the web-based user interface. It collects user inputs via a sidebar form, calls the risk assessment logic through prolog_interface.py, and displays the results, including mitigation suggestions for high-risk projects.

## 3.0 - Input Parameters
The system requires the following input parameters, which are collected via the Streamlit interface's sidebar form (st.sidebar.form):

    Expected Margin (%):
        • Type: Float (st.number_input, e.g., 15.0 for 15.0%)
        • Description: The predicted profitability percentage. A critical factor, used in core classification and overrides.
        • Prolog Data Type: float (converted to 0.xx, e.g., 0.15)

    Project Type:
        • Type: Enum (st.selectbox)
        • Options: "Planning & Execution", "Planning Only", "Execution Only"
        • Description: Defines C2M's scope. "Execution Only" carries specific risks.
        • Prolog Data Type: atom (planning_and_execution, planning_only, execution_only)

    SIA Complexity Level:
        • Type: Enum (st.selectbox)
        • Options: "Level 1 (Lowest Complexity)" to "Level 5 (Highest Complexity)"
        • Description: Project complexity based on SIA regulations (1-5). Higher levels imply more risk.
        • Prolog Data Type: integer

    Contract Type:
        • Type: Enum (st.selectbox)
        • Options: "Hourly", "Fixed Price"
        • Description: "Fixed Price" can be riskier, especially with low margins.
        • Prolog Data Type: atom (hourly, fixed_price)

    Historical Client Relationship:
        • Type: Enum (st.selectbox)
        • Options: "Established", "New"
        • Description: Established relationships are generally less risky.
        • Prolog Data Type: atom (established, new)

    Client Type:
        • Type: Enum (st.selectbox)
        • Options: "Private", "Government"
        • Description: Government projects may offer stability but have more regulations.
        • Prolog Data Type: atom (private, government)

    Expected Absolute Profit (CHF):
        • Type: Float (st.number_input, e.g., 100000.0)
        • Description: Total expected profit in CHF. Used for the risk override rule (if > CHF 2,000,000).
        • Prolog Data Type: float or integer

## 4.0 - Risk Assessment Logic (prolog/risk_rules.pl)
The project risk is determined by the assess_risk/8 predicate in prolog/risk_rules.pl, following a two-step, rule-based approach:

### 4.1 - Initial Risk Classification (risk_classification/7)
This predicate sets an initial risk based on specific combinations of inputs, prioritizing High, then Medium, and defaulting to Low:

    1) High Risk Conditions: A project is 'high' if any apply: 
        • Margin < 10% AND (Fixed Price OR SIA ≥ 4)
        • Execution Only AND (SIA ≥ 4 OR New Client)
        • Private Client AND New Client AND Margin < 15% 

    2) Medium Risk Conditions: If not High, a project is 'medium' if all apply: 
        • 10% ≤ Margin ≤ 15% AND
        • ( (Not Execution Only AND SIA = 3) OR Fixed Price ) 

    3) Low Risk (Default): If a project is neither High nor Medium, it is classified as 'low'. This ensures all projects receive a classification. The original specific 'Low Risk' conditions  are implicitly covered, as any project not meeting High or Medium criteria (including the Low Risk exclusion ) will fall into this category.

### 4.2 - Profit-Based Override Rules (override_risk/4)
After the initial classification, override rules can downgrade the risk:

    • Conditions: If (Expected Margin > 20%) OR (Expected Absolute Profit > 2,000,000 CHF).
    • Action: The risk level is downgraded by one step using the downgrade/2 predicate (High → Medium, Medium → Low, Low → Low).
    • A cut (!) is used to ensure only one override (or the default) applies.

The assess_risk/8 predicate calls risk_classification/7 and then override_risk/4 to produce the FinalRisk.

## 5.0 - Python-Prolog Interface (utils/prolog_interface.py)
This module manages the interaction:

    1) Initialization: It starts a Prolog() instance and consults the risk_rules.pl file, handling path conversions and ensuring the rules are loaded.
    2) assess_risk(...) Function:
        2.1) Accepts the 7 input parameters from app.py.
        2.2) Converts the margin percentage to a float (e.g., 15.0 -> 0.15).
        2.3) Constructs the Prolog query string assess_risk(0.15, ..., 100000.0, RiskLevel).
        2.4) Executes the query using list(prolog.query(query)).
        2.5) Robustly parses the result list, checking for the RiskLevel key as either a string or bytes, and decoding bytes if necessary.
        2.6) Returns the RiskLevel string (e.g., 'low') or an error string ('error_in_assessment', 'undefined_risk_profile') if issues occur.

## 6.0 - Streamlit User Interface (app.py)
The app.py script creates the user experience:

    • Layout: Uses st.set_page_config(layout="wide") and displays titles and introductory text.
    • Input Form: Uses st.sidebar.form to group all input widgets on the left.
    • Mapping: Employs Python dictionaries (pt_map, sia_map, etc.) to translate user-friendly UI selections into Prolog-compatible atoms and integers.
    • Function Call: When the form is submitted, it calls utils.prolog_interface.assess_risk with the mapped inputs.
    • Results Display:
    • Shows the final risk level using st.success, st.warning, or st.error based on the returned value ('low', 'medium', 'high').
    • Displays specific error messages if 'error_in_assessment' or 'undefined_risk_profile' is returned. If the risk is 'high', it displays the mitigation suggestions from mitigation_suggestions_dict using st.expander for each category, providing actionable advice.

## 7.0 - Mitigation Suggestions (app.py)
For projects classified as "High Risk", the UI presents a list of potential mitigation strategies. These are currently stored in a Python dictionary (mitigation_suggestions_dict) within app.py, based on Table 4 of the specification document. They are grouped by category (e.g., Team Composition, Scope Simplification) and displayed using st.expander elements to keep the interface clean while providing detailed information when needed.

## 8.0 Running the Application
To run the Streamlit application:

    1) Ensure you have Python and SWI-Prolog installed.
    2) Navigate to the project's root directory in your terminal (e.g., cd "C:\Users\your_username\PycharmProjects\KPDM_Group2_Project")
    3) Set up a virtual environment (optional but recommended) and activate it.
    4) Install the required Python packages:
        Bash
        pip install -r requirements.txt
    5) Run the Streamlit application:
        Bash
        streamlit run app.py
    6) The application will open in your default web browser.

![C2M Profittability Screenshot (Low Risk).png](sample_images/C2M%20Profittability%20Screenshot%20%28Low%20Risk%29.png)
C2M Assessmemt Tool User Interface (Low Risk Assessment) 

![C2M Profittability Screenshot (High Risk).png](sample_images/C2M%20Profittability%20Screenshot%20%28High%20Risk%29.png)
C2M Assessmemt Tool User Interface (High Risk Assessment)

## 9.0 - Project File Descriptions
    • app.py: Main Streamlit script for the UI.
    • utils/prolog_interface.py: Python-Prolog bridge using PySWIP.
    • prolog/risk_rules.pl: Core Prolog knowledge base.
    • utils/__init__.py: Makes utils a Python package.
    • requirements.txt: Lists Python dependencies (streamlit, pyswip).
    • Implementation for Streamlit-Based Risk Assessment Interface.md: This documentation file.