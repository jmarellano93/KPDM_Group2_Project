import os
from pyswip import Prolog

prolog = Prolog()

# Absolute path with forward slashes, passed as raw string
prolog_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
).replace("\\", "/")

# Print for verification
print("CONSULTING:", prolog_path)

# Now consult using the forward-slash path
prolog.consult(prolog_path)

def assess_risk(margin, proj, sia, contract, rel, client):
    query = (
        f"assess_risk({margin}, "
        f"'{proj}', {sia}, '{contract}', '{rel}', '{client}', Risk, Suggestions)"
    )
    results = list(prolog.query(query))
    if not results:
        return "unknown", []
    return results[0]["Risk"], results[0]["Suggestions"]
