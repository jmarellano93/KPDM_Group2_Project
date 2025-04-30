% Prolog Knowledge Base for Risk Assessment

% Margin Scoring
margin_score(M, 30) :- M < 10.
margin_score(M, 15) :- M >= 10, M =< 15.
margin_score(M, 0)  :- M > 15.

% Project Type
project_score(execution_only, 20).
project_score(planning_and_execution, 10).
project_score(planning_only, 0).

% SIA Complexity
complexity_score(5, 15).
complexity_score(4, 12).
complexity_score(3, 9).
complexity_score(2, 6).
complexity_score(1, 0).

% Contract Type
contract_score(fixed_price, 15).
contract_score(hourly, 0).

% Client Relationship
clientrel_score(new, 10).
clientrel_score(established, 0).

% Client Type
clienttype_score(private, 10).
clienttype_score(government, 0).

% High risk conditions
high_risk_condition(M, _, _, fixed_price, _, _) :- M < 10.
high_risk_condition(_, execution_only, S, _, new, _) :- S >= 4.
high_risk_condition(M, _, _, _, new, private) :- M < 15.

% Risk classification
risk_classification(S, high) :- S > 70.
risk_classification(S, medium) :- S >= 40, S =< 70.
risk_classification(S, low) :- S < 40.

% Mitigations
mitigations(low, []).
mitigations(medium, ["Increase client communication."]).
mitigations(high, [
    "Reassign critical tasks to senior staff.",
    "Extend project timeline to avoid overtime.",
    "Simplify scope to reduce risk."
]).

% Main predicate
assess_risk(M, P, S, C, R, T, Risk, Suggestions) :-
    margin_score(M, SM),
    project_score(P, SP),
    complexity_score(S, SS),
    contract_score(C, SC),
    clientrel_score(R, SR),
    clienttype_score(T, ST),
    Total is SM + SP + SS + SC + SR + ST,
    ( high_risk_condition(M, P, S, C, R, T) -> Risk = high ; risk_classification(Total, Risk) ),
    mitigations(Risk, Suggestions).