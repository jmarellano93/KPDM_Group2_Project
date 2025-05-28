% --- Risk Level Downgrade Hierarchy ---
% Defines how risk levels can be downgraded (High->Medium->Low)
downgrade(high, medium).   % High risk can be downgraded to medium
downgrade(medium, low).    % Medium risk can be downgraded to low
downgrade(low, low).       % Low risk cannot be downgraded further

% --- Core Risk Classification Rules ---
% Determines initial risk level based on project parameters
% Parameters: Margin (float, e.g., 0.1 for 10%), ProjectType (atom), SIA (integer 1-5),
%             ContractType (atom), ClientRel (atom), ClientType (atom), RiskLevel (atom)
risk_classification(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, RiskLevel) :-
    % HIGH RISK CONDITIONS (ANY of these must be true)
    (
        (Margin < 0.1, (ContractType = fixed_price ; SIA >= 4)) ;   % Low margin + fixed-price or high complexity
        (ProjectType = execution_only, (SIA >= 4 ; ClientRel = new)) ;   % Execution-only with complexity or new client
        (ClientType = private, ClientRel = new, Margin < 0.15)   % New private client with low margin
    )
    -> RiskLevel = high ;

    % MEDIUM RISK CONDITIONS (ALL must be true + EITHER clause)
    (
        (Margin >= 0.1, Margin =< 0.15,   % Margin in moderate range
            (
                (ProjectType \= execution_only, SIA = 3) ;   % Not execution-only with medium complexity
                ContractType = fixed_price % OR fixed-price contract
            )
        )
    )
    -> RiskLevel = medium ;

    % LOW RISK CONDITIONS (ALL must be true + EITHER clause + NEGATION)
    (
        (Margin > 0.15,   % Healthy margin
            (
                ClientType = government ;   % Government client
                (ClientRel = established, ProjectType \= execution_only) % OR established relationship + not execution-only
            ),
            % NEGATION RULE: Exclude execution-only projects with high complexity and new clients
            \+ (ProjectType = execution_only, SIA >= 4, ClientRel = new)
        )
    )
    -> RiskLevel = low ;

    % Default catch-all if no other rule matches.
    RiskLevel = undefined_risk_profile.

% --- Profit-Based Override Rules ---
% Applies risk downgrades based on profitability
% Parameters: InitialRiskLevel (atom), Profit (float/integer), Margin (float), FinalRisk (atom)

% Rule A/B: Downgrade risk if profit > 2,000,000 CHF OR margin > 20% (0.20)
override_risk(InitialRiskLevel, Profit, Margin, FinalRisk) :-
    (InitialRiskLevel \= undefined_risk_profile), % Only override if initial risk is defined
    (Profit >= 2000000 ; Margin >= 0.20),   % Either condition met
    downgrade(InitialRiskLevel, FinalRisk),!. % Apply one-level downgrade and cut

% Default case: No override applied, or initial risk was undefined
override_risk(InitialRiskLevel, _, _, InitialRiskLevel).   % Keep original risk level

% --- Main Risk Assessment Predicate ---
% Combines classification and override rules for final risk determination
% Parameters: Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, Profit (Expected Absolute Profit CHF), FinalRisk
assess_risk(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, Profit, FinalRisk) :-
    % Step 1: Determine initial risk classification
    risk_classification(Margin, ProjectType, SIA, ContractType, ClientRel, ClientType, InitialRiskLevel),
    % Step 2: Apply profitability overrides if applicable
    override_risk(InitialRiskLevel, Profit, Margin, FinalRisk).

% Enum-like atoms for clarity (used in rules above):
% ProjectType: execution_only, planning_only, planning_and_execution
% ContractType: fixed_price, hourly
% ClientRel: new, established
% ClientType: private, government
% RiskLevel: high, medium, low, undefined_risk_profile