import os
from pyswip import Prolog

prolog = Prolog()

# Dynamically compute absolute path and convert it to Prolog-friendly form
prolog_file = os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
prolog_file = os.path.abspath(prolog_file).replace("\\", "/")  # ensure forward slashes

prolog.consult(prolog_file)

def assess_risk(margin, proj, sia, contract, rel, client):
    # Wrap all atom arguments in single quotes to avoid syntax errors
    query = (
        f"assess_risk({margin}, "
        f"'{proj}', {sia}, '{contract}', '{rel}', '{client}', Risk, Suggestions)"
    )
    results = list(prolog.query(query))
    if not results:
        return "unknown", []
    return results[0]["Risk"], results[0]["Suggestions"]
