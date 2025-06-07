import os
from pyswip import Prolog

prolog = Prolog()

# Create a forward-slash path for Prolog
prolog_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
).replace("\\", "/")

print("Attempting to consult Prolog file:", prolog_file)

# Use .query() instead of .consult() and check result
try:
    list(prolog.query(f"consult('{prolog_file}')"))
    print("Successfully consulted:", prolog_file)
except Exception as e:
    print(f"ERROR: Failed to consult Prolog file: {e}")

def assess_risk(margin_percentage, project_type, sia_complexity, contract_type, client_relationship, client_type):
    """
    Queries the Prolog knowledge base to assess project risk.
    Args:
        margin_percentage (float): Expected margin as a percentage (e.g., 12.5 for 12.5%).
        project_type (str): e.g., 'execution_only'.
        sia_complexity (int): e.g., 1, 2, 3, 4, 5.
        contract_type (str): e.g., 'fixed_price'.
        client_relationship (str): e.g., 'new'.
        client_type (str): e.g., 'private'.
    Returns:
        str: The final assessed risk level ('high', 'medium', 'low') or an error string.
    """
    # Convert margin percentage to float (e.g., 12.5% -> 0.125) for Prolog
    margin_float = margin_percentage / 100.0

    # Ensure project_type and other atoms are passed as Prolog atoms (lowercase strings)
    query = f"assess_risk({margin_float}, {project_type}, {sia_complexity}, {contract_type}, {client_relationship}, {client_type}, RiskLevel)"

    print(f"Executing Prolog query: {query}")

    try:
        results = list(prolog.query(query))
        print(f"Prolog query results: {results}")

        if results:
            result_dict = results[0]
            risk_value = None

            # Check for 'RiskLevel' as string or bytes
            if 'RiskLevel' in result_dict:
                risk_value = result_dict['RiskLevel']
            elif b'RiskLevel' in result_dict:
                risk_value = result_dict[b'RiskLevel']

            if risk_value:
                # Decode if it's bytes
                if isinstance(risk_value, bytes):
                    risk_value = risk_value.decode('utf-8')
                return risk_value # Return the actual risk level
            else:
                print("Prolog query returned a solution, but 'RiskLevel' key was missing or result format was unexpected.")
                return "error_in_assessment" # Return error string
        else:
            print("Prolog query did not return any solution.")
            # This case *should* now be handled by the updated Prolog, but keep as fallback
            return "undefined_risk_profile"

    except Exception as e:
        print(f"An error occurred during Prolog query: {e}")
        return "error_in_assessment" # Return error string