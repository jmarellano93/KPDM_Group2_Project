% --- Risk Level Downgrade Hierarchy ---
downgrade(high, medium).
downgrade(medium, low).
downgrade(low, low).

% --- Core Risk Classification Rules ---
% Determines initial risk level based on project parameters
risk_classification(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, RiskLevel) :-
    % HIGH RISK CONDITIONS (ANY of these must be true)
    (
        (Margin < 0.1, (ContractType = fixed_price ; SIA >= 4)) ;
        (ProjectType = execution_only, (SIA >= 4 ; ClientRel = new)) ;
        (ClientType = private, ClientRel = new, Margin < 0.15)
    )
    -> RiskLevel = high ; % If any high risk condition met, classify as high

    % MEDIUM RISK CONDITIONS (ALL must be true + EITHER clause)
    (
        (Margin >= 0.1, Margin =< 0.15,
            (
                (ProjectType \= execution_only, SIA = 3) ;
                ContractType = fixed_price
            )
        )
    )
    -> RiskLevel = medium ; % If medium conditions met, classify as medium

    % LOW RISK CONDITIONS (Check for the *exclusion* first)
    % If a project meets the specific exclusion criteria, it should NOT be low,
    % but if it wasn't caught by High/Medium, it might need re-evaluation.
    % However, the High risk rules *should* catch `(ProjectType = execution_only, SIA >= 4, ClientRel = new)`.
    % Therefore, if it's not High and not Medium, we will classify it as Low.
    % We ensure the original Low Risk 'negation' rule is respected because
    % if that negation IS true, it *should* have been caught by 'High'.
    RiskLevel = low. % Default to low if not high or medium

% --- Profit-Based Override Rules ---
override_risk(RiskLevel, Profit, Margin, FinalRisk) :-
    (Profit >= 2000000 ; Margin >= 0.20),
    downgrade(RiskLevel, FinalRisk), !. % Use cut (!) to prevent backtracking to the default case
override_risk(RiskLevel, _, _, RiskLevel).

% --- Main Risk Assessment Predicate ---
assess_risk(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, Profit, FinalRisk) :-
    risk_classification(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, InitialRiskLevel),
    override_risk(InitialRiskLevel, Profit, Margin, FinalRisk).