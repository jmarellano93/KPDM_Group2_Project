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

    % LOW RISK CONDITIONS
    RiskLevel = low. % Default to low if not high or medium

% --- Margin-Based Override Rules ---
override_risk(RiskLevel, Margin, FinalRisk) :-
    Margin >= 0.20,
    downgrade(RiskLevel, FinalRisk), !. % Use cut (!) to prevent backtracking
override_risk(RiskLevel, _, RiskLevel).

% --- Main Risk Assessment Predicate ---
assess_risk(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, FinalRisk) :-
    risk_classification(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, InitialRiskLevel),
    override_risk(InitialRiskLevel, Margin, FinalRisk).