from pyswip import Prolog

prolog = Prolog()
prolog.consult("prolog/risk_rules.pl")

def assess_risk(margin, proj, sia, contract, rel, client):
    query = f"assess_risk({margin}, {proj}, {sia}, {contract}, {rel}, {client}, Risk, Suggestions)"
    results = list(prolog.query(query))
    if not results:
        return "unknown", []
    return results[0]["Risk"], results[0]["Suggestions"]