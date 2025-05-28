import os
from pyswip import Prolog

# Initialize the Prolog engine
prolog = Prolog()

# Construct the absolute path to the Prolog rules file
# This assumes 'prolog_interface.py' is in 'utils' and 'risk_rules.pl' is in 'prolog' at the same level as 'utils'
try:
    prolog_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
    )
    # Ensure forward slashes for Prolog, especially on Windows
    prolog_file_path_prolog = prolog_file_path.replace("\\", "/")

    print(f"Attempting to consult Prolog file: {prolog_file_path_prolog}")

    # Consult the Prolog file using a query to handle paths robustly
    # The consult query needs to have the path quoted for Prolog
    consult_query = f"consult('{prolog_file_path_prolog}')"
    list(prolog.query(consult_query))
    print(f"Successfully consulted: {prolog_file_path_prolog}")

except Exception as e:
    print(f"Error during Prolog initialization or consultation: {e}")
    # Depending on the application structure, you might want to raise this error
    # or handle it in a way that the Streamlit app can inform the user.
    # For now, we'll let it proceed, and assess_risk will likely fail.

def assess_risk(margin_percentage, project_type, sia_complexity, contract_type, client_relationship, client_type,
                expected_profit_chf):
    """
    Queries the Prolog knowledge base to assess project risk.

    Args:
        margin_percentage (float): Expected margin as a percentage (e.g., 12.5 for 12.5%).
        project_type (str): Prolog atom for project type (e.g., 'execution_only').
        sia_complexity (int): SIA complexity level (e.g., 1, 2, 3, 4, 5).
        contract_type (str): Prolog atom for contract type (e.g., 'fixed_price').
        client_relationship (str): Prolog atom for client relationship (e.g., 'new').
        client_type (str): Prolog atom for client type (e.g., 'private').
        expected_profit_chf (float): Expected absolute profit in CHF.

    Returns:
        str: The final assessed risk level (e.g., 'high', 'medium', 'low',
             'undefined_risk_profile', or 'error_in_assessment').
    """
    # Convert margin percentage to float (e.g., 12.5% -> 0.125) for Prolog
    margin_float = margin_percentage / 100.0

    # Construct the Prolog query
    # Prolog atoms (project_type, contract_type, etc.) are passed as unquoted strings
    # if they are valid Prolog atoms (e.g., lowercase, no spaces).
    # Numerical values are passed directly.
    query = (f"assess_risk({margin_float}, {project_type}, {sia_complexity}, {contract_type}, "
             f"{client_relationship}, {client_type}, {expected_profit_chf}, RiskLevel)")

    print(f"Executing Prolog query: {query}")

    try:
        results = list(prolog.query(query))
        print(f"Prolog query results: {results}")

        if results and isinstance(results, list) and len(results) > 0 and 'RiskLevel' in results:
            risk_value = results
            # PySWIP usually returns Prolog atoms as Python strings.
            # If there's a chance it returns bytes (e.g., b'high'), decode it.
            if isinstance(risk_value, bytes):
                return risk_value.decode()
            return str(risk_value) # Ensure it's a string
        else:
            # This case handles when Prolog finds no solution or the result format is unexpected
            print("Prolog query did not return the expected RiskLevel binding or failed.")
            return "undefined_risk_profile"
    except Exception as e:
        print(f"An error occurred during Prolog query execution: {e}")
        return "error_in_assessment"

if __name__ == '__main__':
    # Example usage for testing this module directly
    # Ensure risk_rules.pl is in the correct relative path for this test to work
    print("Testing prolog_interface.py directly...")

    # Test Case 1: Expected High Risk (Low margin, fixed price)
    risk = assess_risk(5.0, 'planning_and_execution', 3, 'fixed_price', 'established', 'private', 50000.0)
    print(f"Test Case 1 Risk: {risk}") # Expected: high

    # Test Case 2: Expected Low Risk (High margin, government client, override not met)
    risk = assess_risk(18.0, 'planning_and_execution', 2, 'hourly', 'established', 'government', 100000.0)
    print(f"Test Case 2 Risk: {risk}") # Expected: low

    # Test Case 3: Expected Medium Risk, then Low due to margin override
    risk = assess_risk(25.0, 'execution_only', 4, 'hourly', 'new', 'private', 100000.0) # Initially high, then medium by margin
    # The above would be: execution_only and SIA >=4 -> high. Margin > 0.2 -> downgrade to medium.
    # Let's try a case that would be medium then low.
    # Medium: Margin 12%, fixed_price
    risk = assess_risk(12.0, 'planning_and_execution', 2, 'fixed_price', 'established', 'private', 2500000.0) # Initially medium, then low by profit
    print(f"Test Case 3 Risk (Medium -> Low by Profit Override): {risk}") # Expected: low

    # Test Case 4: High risk that gets downgraded to medium by profit override
    risk = assess_risk(5.0, 'execution_only', 4, 'fixed_price', 'new', 'private', 2500000.0)
    print(f"Test Case 4 Risk (High -> Medium by Profit Override): {risk}") # Expected: medium