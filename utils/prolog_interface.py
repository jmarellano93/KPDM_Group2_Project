import os
from pyswip import Prolog

prolog = Prolog()

# Get absolute path to the Prolog file and fix slashes
prolog_file = os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
prolog_file = os.path.abspath(prolog_file).replace("\\", "/")  # forward slashes

# Now directly consult the file path (no extra quoting)
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
