import os
from pyswip import Prolog

# Initialize the Prolog engine
prolog = Prolog()

# Construct the absolute path to the Prolog rules file
try:
    prolog_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
    )
    prolog_file_path_prolog = prolog_file_path.replace("\\", "/")

    print(f"Attempting to consult Prolog file: {prolog_file_path_prolog}")
    consult_query = f"consult('{prolog_file_path_prolog}')"
    list(prolog.query(consult_query))  # Execute consultation
    print(f"Successfully consulted: {prolog_file_path_prolog}")

except Exception as e:
    print(f"CRITICAL ERROR during Prolog initialization or consultation: {e}")
    # In a real application, you might want to make the app unusable if Prolog doesn't load.


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
             'undefined_risk_profile', 'error_in_assessment', or 'error_in_assessment_format').
    """
    margin_float = margin_percentage / 100.0
    query = (f"assess_risk({margin_float}, {project_type}, {sia_complexity}, {contract_type}, "
             f"{client_relationship}, {client_type}, {expected_profit_chf}, RiskLevel)")

    print(f"Executing Prolog query: {query}")

    try:
        results = list(prolog.query(query))
        print(f"Prolog query results: {results}")

        if results:  # Check if the list of solutions is not empty
            solution_dict = results  # Get the first (and typically only) solution dictionary
            if isinstance(solution_dict, dict) and 'RiskLevel' in solution_dict:
                risk_value = solution_dict
                # PySWIP usually returns Prolog atoms as Python strings.
                # If it were to return bytes, decoding would be necessary.
                if isinstance(risk_value, bytes):
                    risk_value_str = risk_value.decode()
                    print(f"Decoded RiskLevel from bytes: {risk_value_str}")
                    return risk_value_str

                risk_value_str = str(risk_value)  # Ensure it's a string
                print(f"Successfully extracted RiskLevel: {risk_value_str}")
                return risk_value_str
            else:
                # This case means results was not a dict or didn't have 'RiskLevel'
                print(
                    "Prolog query returned a solution, but 'RiskLevel' key was missing or result format was unexpected.")
                return "error_in_assessment_format"
        else:
            # This means the Prolog query failed to find any solution (results list is empty).
            # This can happen if assess_risk/8 itself fails in Prolog for the given inputs.
            # Your Prolog code's assess_risk calls risk_classification, which has a default
            # 'undefined_risk_profile', so this branch should ideally not be hit if Prolog logic is complete.
            # However, if assess_risk itself had an issue, this would be the path.
            print(
                "Prolog query failed to find any solution (results list is empty). This might indicate an issue in Prolog predicate assess_risk/8 not succeeding.")
            return "undefined_risk_profile"  # Defaulting to this, as Prolog couldn't define it.

    except Exception as e:
        print(f"An error occurred during Prolog query execution: {e}")
        return "error_in_assessment"


if __name__ == '__main__':
    # Example usage for testing this module directly
    print("\nTesting prolog_interface.py directly...")

    # Test Case 1: Expected High Risk (Low margin, fixed price) - Matches screenshot
    # Margin: 5.00 % (0.05), Project Type: Planning & Execution (planning_and_execution)
    # SIA: Level 1 (1), Contract Type: Fixed Price (fixed_price)
    # Historical Client: Established (established), Client Type: Private (private)
    # Expected Abs Profit: 10000.00
    risk = assess_risk(5.0, 'planning_and_execution', 1, 'fixed_price', 'established', 'private', 10000.0)
    print(f"Test Case 1 (Screenshot) Risk: {risk} (Expected: high)")

    # Test Case 2: Expected 'undefined_risk_profile' from your logs
    risk = assess_risk(15.0, 'planning_and_execution', 1, 'hourly', 'established', 'private', 100000.0)
    print(f"Test Case 2 (Undefined from logs) Risk: {risk} (Expected: undefined_risk_profile)")

    # Test Case 3: Expected 'medium' from your logs
    risk = assess_risk(15.0, 'planning_only', 1, 'fixed_price', 'established', 'private', 10000.0)
    print(f"Test Case 3 (Medium from logs) Risk: {risk} (Expected: medium)")

    # Test Case 4: Expected Low Risk (High margin > 15%, Government client, override not met)
    risk = assess_risk(18.0, 'planning_and_execution', 2, 'hourly', 'established', 'government', 100000.0)
    print(f"Test Case 4 (Low Risk Example) Risk: {risk} (Expected: low)")

    # Test Case 5: Expected Medium Risk, then Low due to profit override > 2M
    risk = assess_risk(12.0, 'planning_and_execution', 2, 'fixed_price', 'established', 'private', 2500000.0)
    print(f"Test Case 5 (Medium -> Low by Profit Override) Risk: {risk} (Expected: low)")

    # Test Case 6: Expected High Risk, then Medium due to margin override > 20%
    risk = assess_risk(25.0, 'execution_only', 4, 'hourly', 'new', 'private', 100000.0)
    print(f"Test Case 6 (High -> Medium by Margin Override) Risk: {risk} (Expected: medium)")