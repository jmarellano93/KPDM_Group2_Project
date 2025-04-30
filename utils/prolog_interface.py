import os
from pyswip import Prolog

prolog = Prolog()

# Convert path to an absolute, Prolog-safe format
prolog_file = os.path.join(os.path.dirname(__file__), "..", "prolog", "risk_rules.pl")
prolog_file = os.path.abspath(prolog_file).replace("\\", "/")  # forward slashes

# Wrap in double quotes for Prolog: consult("C:/path/to/file.pl")
consult_command = f'consult("{prolog_file}")'
prolog.consult(consult_command)

def assess_risk(margin, proj, sia, contract, rel, client):
    query = (
        f"assess_risk({margin}, "
        f"'{proj}', {sia}, '{contract}', '{rel}', '{client}', Risk, Suggestions)"
    )
    results = list(prolog.query(query))
    if not results:
        return "unknown", []
    return results[0]["Risk"], results[0]["Suggestions"]
