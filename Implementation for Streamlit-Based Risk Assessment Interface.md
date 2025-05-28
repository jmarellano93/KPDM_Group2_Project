Implementation for Streamlit-Based Risk Assessment Interface

1. Overview
This document describes the implementation of a Streamlit-based user interface for C2M's Project Risk and Profitability Assessment system. The system leverages a Prolog backend for its core decision logic, which evaluates project risk based on a set of predefined rules and input parameters. This interface allows users at C2M to easily input project details and receive an immediate risk classification (Low, Medium, or High), along with mitigation suggestions for high-risk projects.

The primary goal is to provide an accessible and user-friendly front-end to the sophisticated risk assessment model, ensuring that C2M can efficiently evaluate project viability in line with Swiss architectural industry standards and the firm's financial objectives.

2. System Architecture
The system comprises three main components:

prolog/risk_rules.pl: The Prolog knowledge base containing all the decision logic, risk classification rules, and override mechanisms.
utils/prolog_interface.py: A Python module that uses PySWIP to bridge the gap between the Python application and the Prolog engine. It handles querying the Prolog knowledge base.
app.py: The Streamlit application script that provides the web-based user interface, collects user inputs, calls the risk assessment logic via prolog_interface.py, and displays the results.
3. Input Parameters
The system requires the following input parameters, which are collected via the Streamlit interface:

Expected Margin (%):

Type: Float (e.g., 15.5 for 15.5%)
Description: The predicted profitability percentage for the project, based on estimated revenues and costs. This is a critical factor in the risk assessment.
Prolog Data Type: float (e.g., 0.155)
Project Type:

Type: Enum (Dropdown selection)
Options:
"Planning & Execution" (maps to Prolog atom: planning_and_execution)
"Planning Only" (maps to Prolog atom: planning_only)
"Execution Only" (maps to Prolog atom: execution_only)
Description: Defines the scope of C2M's involvement in the project. "Execution Only" projects can carry higher intrinsic risks.
Prolog Data Type: atom
SIA Complexity Level:

Type: Enum (Dropdown selection)
Options:
"Level 1 (Lowest Complexity)" (maps to Prolog integer: 1)
"Level 2" (maps to Prolog integer: 2)
"Level 3" (maps to Prolog integer: 3)
"Level 4" (maps to Prolog integer: 4)
"Level 5 (Highest Complexity)" (maps to Prolog integer: 5)
Description: Project complexity based on SIA (Swiss Society of Engineers and Architects) regulations, ranging from 1 (lowest) to 5 (highest). Higher complexity generally implies more effort, uncertainty, and risk.
Prolog Data Type: integer
Contract Type:

Type: Enum (Dropdown selection)
Options:
"Hourly" (maps to Prolog atom: hourly)
"Fixed Price" (maps to Prolog atom: fixed_price)
Description: The type of contract for the project. Fixed-price contracts can introduce more financial rigidity and risk if unforeseen issues arise, especially with lower margins.
Prolog Data Type: atom
Historical Client Relationship:

Type: Enum (Dropdown selection)
Options:
"Established" (maps to Prolog atom: established)
"New" (maps to Prolog atom: new)
Description: Reflects C2M's previous experience with the client. Established relationships with a good history are generally less risky than new ones.
Prolog Data Type: atom
Client Type:

Type: Enum (Dropdown selection)
Options:
"Private" (maps to Prolog atom: private)
"Government" (maps to Prolog atom: government)
Description: Indicates whether the client is a private entity or a government body. Government projects may have more regulations but can offer greater financial stability.
Prolog Data Type: atom
Expected Absolute Profit (CHF):

Type: Float (e.g., 250000.00)
Description: The total expected absolute profit from the project in Swiss Francs. This parameter is crucial for the risk override logic. If the expected absolute profit exceeds CHF 2,000,000, the system may downgrade an initially assessed risk level by one step.
Prolog Data Type: float or integer
4. Risk Assessment Logic
The project risk is calculated using a sophisticated rule-based system implemented in prolog/risk_rules.pl. This logic moves beyond simple scoring and emulates expert decision-making. The assessment involves two main steps:

4.1. Initial Risk Classification
The system first determines an initial risk level (High, Medium, or Low) based on a detailed set of conditions. Key margin thresholds influencing this classification are 10% and 15% (derived from C2M's internal financial expertise and historical project analysis):

High Risk Conditions: A project is classified as 'high' if any of the following are met:

Expected Margin < 10% AND (Contract Type = fixed_price OR SIA Complexity ≥ 4).
Project Type = execution_only AND (SIA Complexity ≥ 4 OR Historical Client Relationship = new).
Client Type = private AND Historical Client Relationship = new AND Expected Margin < 15%.
Medium Risk Conditions: A project is classified as 'medium' if all of the following apply:

10% ≤ Expected Margin ≤ 15% AND
EITHER:
Project Type ≠ execution_only AND SIA Complexity = 3, OR
Contract Type = fixed_price.
Low Risk Conditions: A project is classified as 'low' if all of the following apply:

Expected Margin > 15% AND
EITHER:
Client Type = government, OR
Historical Client Relationship = established AND Project Type ≠ execution_only.
AND NONE OF THE FOLLOWING APPLY: Project Type = execution_only AND SIA Complexity ≥ 4 AND Historical Client Relationship = new. (This specific exclusion ensures high-complexity execution-only projects for new clients are never initially classified as low risk, even with other favorable factors, unless an override applies).
If none of these specific conditions are met, the risk may be classified as undefined_risk_profile.

4.2. Profit-Based Override Rules
After the initial classification, the system applies override rules based on exceptional profitability. A margin of 20% is considered very healthy and can trigger a risk downgrade.

Rule A: High Profit Margin Override: If Expected Margin > 20%, the initially assessed risk is downgraded by one level (e.g., High to Medium, Medium to Low).
Rule B: Absolute Profit Override: If Expected Absolute Profit (CHF) > 2,000,000, the initially assessed risk is also downgraded by one level.
If either of these override conditions is met, the risk level is adjusted. The final risk assessment displayed to the user is the result of this two-step process.

5. Mitigation Suggestions for High-Risk Projects
If a project is ultimately classified as "High Risk" by the system, the user interface will display a list of potential mitigation strategies and adjustment procedures. These suggestions are drawn directly from Table 4 ("Proposed Adjustment Procedure") of the "Assess Project Risk and Profitability.docx" specification document.

The purpose of these suggestions is to provide C2M decision-makers with immediate, actionable ideas for managing, adjusting, or potentially restructuring high-risk projects. This can help to improve their viability or reduce the firm's exposure to potential negative outcomes. The suggestions cover areas such as:

Team Composition
Resource Allocation
Timeline Adjustments
Scope Simplification
Outsourcing
Material Substitution
Contract Type Change
Client Coordination
Alternative Design Options
Parallel Task Planning
Phase Splitting
While the system currently provides a general list for all high-risk projects, these suggestions serve as a valuable starting point for expert review and tailored action planning.

6. Running the Application
To run the Streamlit application:

Ensure you have Python and SWI-Prolog installed.
Navigate to the project's root directory in your terminal.
Install the required Python packages:bash pip install -r requirements.txt
Run the Streamlit application:

streamlit run app.py

This will typically open the application in your default web browser.
7. Project File Descriptions
app.py: Contains the Python code for the Streamlit user interface. It handles user input, calls the prolog_interface.py for assessment, and displays results.
utils/prolog_interface.py: Python module using pyswip to interact with the Prolog engine. It loads risk_rules.pl and provides a function to query the assess_risk/8 predicate.
prolog/risk_rules.pl: The SWI-Prolog file defining the knowledge base. It includes facts and rules for downgrade/2, risk_classification/7, override_risk/4, and the main assess_risk/8 predicate.
utils/__init__.py: An empty file that makes the utils directory a Python package.
requirements.txt: Lists the Python dependencies for the project (streamlit, pyswip).
Implementation for Streamlit-Based Risk Assessment Interface.md: This documentation file.
This setup ensures a modular and maintainable system where the UI, the Python-Prolog interface, and the core logic are clearly separated.