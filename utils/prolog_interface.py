import os
from pyswip import Prolog

prolog = Prolog()

# Fix Windows path to forward slashes
prolog_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
).replace("\\", "/")

# Pass the fixed file path directly
prolog.consult(prolog_file)

def assess_risk(margin, proj, sia, contract, rel, client):
    query = (
        f"assess_risk({margin}, "
        f"'{proj}', {sia}, '{contract}', '{rel}', '{client}', Risk, Suggestions)"
    )
    results = list(prolog.query(query))
    if not results:
        return "unknown", []
    return results[0]["Risk"], results[0]["Suggestions"]
