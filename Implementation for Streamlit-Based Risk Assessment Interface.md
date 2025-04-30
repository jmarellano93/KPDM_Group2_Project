# Implementation Plan for Streamlit-Based Project Risk Assessment Interface

## Part I: User Interface and UX Structure

The Streamlit app will be organized as a single-page form that collects all required inputs and displays the results clearly. The UI will include a title and instructions, an input form with fields for the six attributes, an optional section for weight overrides, and an output area for the risk assessment results. Key elements of the UI design are:

•	Title and Description: At the top of the app, we will use st.title() and st.write() (or st.markdown()) to introduce the tool (e.g., "Project Risk Assessment Tool") and provide brief instructions. This can explain that the user should enter project parameters and that the tool will classify the project risk as Low, Medium, or High. We will mention that default weighting is applied to factors, with an option to adjust these weights if needed.

•	Input Form for Project Attributes: The six input fields will be laid out in a logical order. We will group related fields and use appropriate input widgets for each:
    •	Expected Margin (%): A numeric input (using st.number_input) for the expected profit margin percentage. This will accept a float or integer value (e.g. 12.5 for 12.5% margin). We will set a reasonable range (0 to 100) and perhaps a step (0.1) for precision. A help tooltip will clarify this is the predicted profitability percentage. By default, no specific value is pre-filled (or we may use a neutral default like 0.0 to indicate it needs input).
    •	Project Type: A dropdown or radio selection (st.selectbox or st.radio) listing the allowed types: "Execution Only", "Planning Only", "Execution & Planning". These correspond to whether the project includes only the execution phase, only planning phase, or both phases. We’ll provide these as user-friendly strings. A help text can note that execution-only projects tend to carry higher risk. The default selection can be the combined "Execution & Planning" (as a common scenario).
    •	SIA Complexity Level: An integer slider (st.slider) or selectbox for values 1 through 5. This represents the complexity rating per Swiss SIA standards (1 = least complex, 5 = most complex). We will label it clearly (e.g., "SIA Complexity (Level 1–5)") and possibly include help text (e.g., "Level 5 is highest complexity with more effort/uncertainty).
    •	Contract Type: A radio button with two options: "Fixed Price" and "Hourly". Default can be "Fixed Price" (since it’s listed first). A help note can mention that fixed-price contracts add rigidity and can be riskier if unforeseen issues arise.
    •	Historical Client Relationship: A radio button for "New" vs "Established" client. Default to "New" (or whichever is more common). Help text might explain that an established client (ongoing relationship) is generally less risky than a new client.
    •	Client Type: A radio for "Private" vs "Government". Default to "Private". Help text can note differences (e.g., government projects involve more regulation but usually stable funding).

All these inputs will be placed inside a form using st.form for better control. For example, we can do with st.form("risk_form"): and create the above fields, ending with a submission button. This ensures the app waits for the user to fill all fields and press "Submit" instead of reacting immediately to each input.

•	Advanced Weight Override Section: Below the main inputs, we will provide an expandable section (using st.expander("Adjust Attribute Weights")) that allows the user to override the default weights for the six attributes. By default, the weights are Expected Margin 0.30, Project Type 0.20, SIA Level 0.15, Contract Type 0.15, Client Relationship 0.10, Client Type 0.10, which sum to 1.0. Inside the expander, we will list each attribute with a numeric input for its weight:
    •	Expected Margin Weight (default 0.30)
    •	Project Type Weight (default 0.20)
    •	Complexity Level Weight (default 0.15)
    •	Contract Type Weight (default 0.15)
    •	Client Relationship Weight (default 0.10)
    •	Client Type Weight (default 0.10)

We will ensure these are labeled clearly (e.g., "Weight for Expected Margin") and perhaps display a note that weights must sum to 1. The expander will be closed by default (so novice users can ignore it and use defaults easily), but power users can open it to tweak the weight distribution if their scenario demands different emphasis. We might also include a "Reset to Defaults" button inside the expander to quickly revert to the 0.30/0.20/... defaults, for convenience.

•	Submit Button: Inside the form, at the bottom, we’ll place a st.form_submit_button("Evaluate Risk"). When clicked, it will trigger the risk evaluation process. The form ensures that all inputs are captured at once. We will only process the inputs and query Prolog when this button is pressed, not on every field change.

•	Results Display: After submission, the app will display the results on the same page below the form. The output will include:
    •	Risk Classification: This will be shown prominently (e.g., as a header or using Streamlit’s status elements). For example, if the result is High risk, we might use st.error("High Risk") to show it in a red highlight; for Medium risk maybe st.warning("Medium Risk") (yellow), and for Low risk st.success("Low Risk") (green). This gives a quick visual cue. Alternatively, we can simply use a bold text like st.markdown("**Risk Level:** High") with some coloring via Markdown/HTML. The exact phrasing can be "Low Risk", "Medium Risk", or "High Risk" as obtained from the Prolog logic.
    •	Mitigation Suggestions: If the Prolog returns mitigation strategies (especially for high-risk projects), we will list them below the risk level. We can precede them with a subheader like st.subheader("Recommended Mitigations") and then use a bullet list. For example, we might display something like:
        •	Reassign critical tasks to senior staff
        •	Extend project timeline to avoid overtime
        •	Simplify project scope to reduce complexity (These are examples drawn from the knowledge base; if risk is High, multiple suggestions may be listed. For Medium risk, perhaps a couple of moderate precautions; for Low risk, we might simply state "No significant mitigation needed" or not show this section at all.)
    •	The interface will ensure the results are distinct from the input form, perhaps separated by a horizontal line or spacing for clarity. Each time the user submits, the result area will update accordingly.

This UI/UX structure focuses on clarity and ease of use: short explanatory text, logically grouped inputs (with helpful descriptions), and an obvious action button leading to a clearly highlighted result. The use of an expander for advanced options keeps the interface clean for most users while still allowing customization of weights.

## Part II: Input Handling, Validation, and Formatting

Robust input validation will be implemented to ensure the data passed to the Prolog engine is correctly formatted and within expected ranges:
•	Expected Margin (%): We will validate that this input is a numeric value (Streamlit’s number_input inherently ensures this by providing a float). The range will be restricted to 0–100% (since margin is a percentage of revenue). If the user somehow inputs a value outside this range (or a negative margin indicating an expected loss), we will handle it gracefully. For example, if a negative margin is entered, we might treat it as <10% category (since any margin below 10% is the highest risk bracket). However, typically we will inform the user if they enter an unrealistic value. We can set min_value=0.0 in st.number_input to disallow negative values, and max_value=100.0 to disallow >100%. If the user leaves it at 0.0 (default), we might interpret that as 0% margin (which is indeed in the lowest bracket <10%). We will ensure the value is read as a float (e.g., 15 -> 15.0) because the Prolog rules expect a numerical comparison on it.
•	Enumerated Fields: For Project Type, SIA Level, Contract Type, Client Relationship, and Client Type, the Streamlit widgets will only allow valid options, so we don’t have to worry about invalid values. We will, however, map the human-readable selections to the corresponding Prolog atom or value:
•	Project Type: "Execution Only", "Planning Only", "Execution & Planning" will be mapped to Prolog atoms execution_only, planning_only, and planning_and_execution respectively (all lowercase and underscores, which are valid Prolog atom names). This mapping handles spaces and ampersands by converting to underscore notation.
•	SIA Complexity Level: The slider yields an integer 1–5. We will pass this as an integer to Prolog (since Prolog can treat it as a number for comparisons). We might also allow Prolog to treat it as an atom like level_1 etc., but using an integer is simpler for range comparisons (e.g., >= 4 in a rule).
•	Contract Type: "Fixed Price" -> fixed_price, "Hourly" -> hourly.
•	Historical Client Relationship: "New" -> new, "Established" -> established (the documentation referred to established clients as "constant", but we'll use the term established for clarity).
•	Client Type: "Private" -> private, "Government" -> government.

These mappings will be done in Python after the user submits the form. For example, we might have a dictionary like proj_type_map = {"Execution Only": "execution_only", "Planning Only": "planning_only", "Execution & Planning": "planning_and_execution"} to convert the selected string into the Prolog atom name. This ensures the query we build is properly formatted (Prolog atoms must be lowercase and start with a letter).

•	Weight Overrides: Each weight input will be constrained between 0.0 and 1.0 (using min_value=0.0, max_value=1.0 in st.number_input). We will validate the weights collectively upon submission:
•	We calculate the sum of the six weight inputs. If the sum is not exactly 1.0, we will not proceed to Prolog query immediately. Instead, we handle this in one of two ways:
1.	Display an Error: The app can show a st.error("Weights must sum to 1.0. Please adjust the values.") and stop the process. The user can then fix the weights and resubmit. We may calculate the current sum and inform the user of the discrepancy (e.g., "Current sum is 0.95" or "1.07, adjust to 1.0").
2.	Auto-Normalize: Alternatively, we could automatically normalize the weights by dividing each by the total sum. However, this might be non-intuitive for the user. It's clearer to enforce manual correction so the user is aware of the final weights. Our plan is to require the manual fix (with an error message), as it’s straightforward and keeps the user in control.
•	If the sum is extremely close to 1.0 (floating-point rounding issues, e.g., 0.999), we can consider it valid by using a tolerance (like within 0.001). But ideally, the user will input simple decimals that sum exactly (the defaults do).
•	If the user never opened the weight expander, the values will remain at defaults summing to 1.0, so this check will pass. If they did adjust, this validation ensures logical consistency of their inputs.
•	Form Submission Flow: When the user hits "Evaluate Risk", our code (under if form_submitted: block) will run the validation and then proceed. Pseudocode for handling inputs might look like:

---------------------------------------------------
margin = st.number_input(..., value=0.0)
proj_type_str = st.selectbox(..., options=list(proj_type_map.keys()))

(similarly for other fields)###

w_margin = st.number_input(..., value=0.30)
w_proj  = st.number_input(..., value=0.20)

(other weights)###

submit = st.form_submit_button("Evaluate Risk")
if submit:
    # Validate weights sum
    total_w = w_margin + w_proj + ... + w_client
    if abs(total_w - 1.0) > 1e-6:
        st.error(f"Attribute weights must sum to 1.0 (current sum = {total_w:.2f}). Please adjust.")
    else:
        # proceed to build Prolog query
        # ...
---------------------------------------------------

This ensures no Prolog call is made until inputs are sane. If validation fails, we simply don’t execute the risk evaluation and instead prompt the user.

•	Formatting the Prolog Query Inputs: After validation, we translate the inputs for the Prolog query:
•	The numeric inputs (margin and complexity level) will be formatted as numbers (e.g., 15.0 or 12.5 for margin, 3 for complexity). We will ensure the margin is represented as a fraction (e.g., 12.5 stays 12.5, not 0.125) because the Prolog rules in our knowledge base expect percentage values directly (e.g., compare margin to 10, 15, etc., which represent 10% and 15%).
•	The categorical inputs will be formatted as lowercase atoms (as mapped above). For example, if the user chose "Execution & Planning", after mapping we get planning_and_execution. In the Prolog query string, this will appear without quotes (since it's a symbolic atom, not a string).
•	We will construct a Prolog query predicate call like:
assess_risk(Margin, ProjectType, Complexity, ContractType, ClientRel, ClientType, RiskLevel, Mitigations)
Filling in the user values, an example query might look like:
assess_risk(12.5, planning_and_execution, 3, hourly, established, government, RiskLevel, Suggestions).
Here RiskLevel and Suggestions are variables that Prolog will unify with the results.
•	It’s important that we match the exact predicate name and arity defined in the Prolog program (we will define assess_risk/8 or similar in the Prolog code as described later).

By rigorously validating and formatting inputs, we ensure that the data passed to Prolog is clean and that the Prolog engine will receive input in the exact form it expects. This reduces the chance of runtime errors (like unknown atoms or type mismatches) and ensures the logic is applied correctly. Any invalid input scenario will be caught and handled with a clear message to the user, maintaining a smooth UX.

## Part III: Prolog Knowledge Base: Encoding Scoring and Rules
We will create a Prolog knowledge base (e.g., a file risk_rules.pl) that encodes the core scoring tables and decision logic from the provided documentation. The Prolog program will contain facts and rules to calculate the total risk score from attributes and then classify the risk level, possibly also generating mitigation suggestions. The implementation approach is as follows:
•	Representing Attribute Scores (Weighted Rules): For each attribute, we will encode the scoring table (Table 4–9 from the document) as Prolog facts or rules. Each attribute’s contribution will be determined by the user input value for that attribute:
•	Expected Margin (%): According to Table 4, if margin is < 10%, that yields a risk score of 30 (the highest risk contribution for margin); if 10–15%, score 15; if > 15%, score 0. We will implement this as a set of rules:

---------------------------------------------------
margin_score(Margin, Score) :-
    Margin < 10, Score is 30.
margin_score(Margin, Score) :-
    Margin >= 10, Margin =< 15, Score is 15.
margin_score(Margin, Score) :-
    Margin > 15, Score is 0.
---------------------------------------------------

This uses Prolog's arithmetic and comparison to assign the appropriate score. (We assume Margin will be provided as a numeric value, so these comparisons are valid.)
•	Project Type: Table 5 defines: Execution-only = 20, Planning & Execution = 10, Planning-only = 0. We can implement this as simple facts since it's a direct mapping from an enum to a score:

---------------------------------------------------
project_score(execution_only, 20).
project_score(planning_and_execution, 10).
project_score(planning_only, 0).
---------------------------------------------------

•	SIA Complexity Level: Table 6: Level 5 = 15, Level 4 = 12, Level 3 = 9, Level 2 = 6, Level 1 = 0. We can either enumerate this as facts:

---------------------------------------------------
complexity_score(5, 15).
complexity_score(4, 12).
complexity_score(3, 9).
complexity_score(2, 6).
complexity_score(1, 0).
---------------------------------------------------

or as a formula (since the pattern is linear). But facts are straightforward.
•	Contract Type: Table 7: Fixed-price = 15, Hourly = 0. As facts:

---------------------------------------------------
contract_score(fixed_price, 15).
contract_score(hourly, 0).
---------------------------------------------------

•	Historical Client Relationship: Table 8: New = 10, Established = 0. As facts:

---------------------------------------------------
clientrel_score(new, 10).
clientrel_score(established, 0).
---------------------------------------------------

(The doc used the term "Constant" for established, but we will use established for clarity and ensure consistency with the input mapping.)
•	Client Type: Table 9: Private = 10, Government = 0. As facts:

---------------------------------------------------
clienttype_score(private, 10).
clienttype_score(government, 0).
---------------------------------------------------

These scores as defined (30, 20, 15, 10, etc.) already have the attribute weight factored in. They were derived from an assumption of weights (e.g., margin’s weight 0.30 corresponds to 30 points maximum). In our Prolog code, these values correspond to the default weight settings.

•	Incorporating Weight Overrides: If we want the Prolog logic to honor custom weights (when the user overrides them), we have a couple of design options:

    1.	Adjust the score facts on the fly: We could recalculate the numeric scores passed to Prolog based on the new weights in the Python layer and then call Prolog with those adjusted scores. However, since our Prolog rules are set up to calculate scores internally, a better approach is to pass the weights into Prolog and use them in the calculation.

    2.	Compute scores using weight fractions in Prolog: We can modify the Prolog rules to use the weight values as multipliers. For example, instead of hardcoding 30 for margin <10%, we use a formula: Score is WeightMargin * 100 * 1.0 for the worst category. One approach is to define unweighted risk factors (0 to 1 scale) for each condition and then multiply by weight:

---------------------------------------------------
margin_factor(Margin, Factor) :-
    Margin < 10, Factor is 1.0.
margin_factor(Margin, Factor) :-
    Margin >= 10, Margin =< 15, Factor is 0.5.
margin_factor(Margin, Factor) :-
    Margin > 15, Factor is 0.0.
---------------------------------------------------

Then the score could be computed as Score is Factor * Wmargin * 100. Similarly:

---------------------------------------------------
project_factor(execution_only, 1.0).
project_factor(planning_and_execution, 0.5).
project_factor(planning_only, 0.0).
---------------------------------------------------

and Score is Factor * Wproject * 100. The complexity factors would be 1.0 for level 5, 0.8 for level 4, 0.6 for level 3, etc., reflecting the proportion of the maximum weight.
 
Using this method, we could define our main predicate to accept weight parameters and use them in computing each Score. For instance:

---------------------------------------------------
total_score(Margin, ProjType, SiaLevel, Contract, Rel, Client,
            Wm, Wp, Ws, Wc, Wr, Wt, Total) :-
    margin_factor(Margin, Fm), Sm is Fm * Wm * 100,
    project_factor(ProjType, Fp), Sp is Fp * Wp * 100,
    complexity_factor(SiaLevel, Fs), Sc is Fs * Ws * 100,
    contract_factor(Contract, Fc), So is Fc * Wc * 100,
    clientrel_factor(Rel, Fr), Sr is Fr * Wr * 100,
    clienttype_factor(Client, Ft), St is Ft * Wt * 100,
    Total is Sm + Sp + Sc + So + Sr + St.
---------------------------------------------------

(Here I used Wc for Contract weight, Wr for Relationship weight, Wt for client Type weight, etc., to differentiate). This total_score predicate calculates the weighted sum dynamically. We would call it with the user-provided weights.
 
However, to keep things simpler in the first iteration, we might choose to assume default weights within Prolog and handle weight adjustments outside or via a simpler mechanism. A pragmatic approach is:
    •	Implement the Prolog knowledge base with the default weighting (as in the fixed scores above).
    •	If the user overrides weights, we can scale the final total score in Python or adjust threshold logic accordingly. But adjusting in Python could get complicated and undermine using Prolog for the logic.
Ideally, we implement the full dynamic approach as shown with factors. For this plan, we will aim to pass the weights to Prolog. That means our query will become assess_risk(Margin, ProjType, Sia, Contract, Rel, Client, Wm, Wp, Ws, Wc, Wr, Wt, Risk, Suggestions) including the six weight values as parameters. This is a bit lengthy but ensures the Prolog rules use the exact weights.

•	Calculating the Total Score: Once individual attribute scores are determined, Prolog will sum them up to get a Total Risk Score. This corresponds to the “Variable1coefficient1 + var2coef2 + ...” calculation described in the document. In our static-weight approach, this is just adding the six scores (since each already reflects its weight). For example:

---------------------------------------------------
total_score(Margin, ProjType, SiaLevel, Contract, Rel, Client, TotalScore) :-
    margin_score(Margin, S1),
    project_score(ProjType, S2),
    complexity_score(SiaLevel, S3),
    contract_score(Contract, S4),
    clientrel_score(Rel, S5),
    clienttype_score(Client, S6),
    TotalScore is S1 + S2 + S3 + S4 + S5 + S6.
---------------------------------------------------

This rule uses the previously defined facts/rules to retrieve each partial score and then sums them. With default weights, TotalScore will range from 0 to 100 (since in the worst-case scenario each category contributes its max, totaling 100). If using dynamic weights via factor method, the sum would similarly be scaled to 100 * (sum of weights), which is also 100 if weights sum to 1. So either way, 0–100 scale is maintained.

•	Risk Classification Logic: After computing the total score, the Prolog program will classify the project as Low, Medium, or High risk. We have two sets of criteria from the experts:
    
    1. Threshold-based classification: The documentation suggests using the total score with cut-off values:
        •	Low Risk if Total Score < 40
        •	Medium Risk if 40 ≤ Total Score ≤ 70
        •	High Risk if Total Score > 70 
        We will implement this directly in Prolog. For example:

---------------------------------------------------
risk_classification(TotalScore, low) :- TotalScore < 40.
risk_classification(TotalScore, medium) :- TotalScore >= 40, TotalScore =< 70.
risk_classification(TotalScore, high) :- TotalScore > 70.
---------------------------------------------------

These rules cover all possible scores 0–100 and assign a risk category accordingly. (We ensure the boundaries 40 and 70 are handled in the Medium clause.)

    2.	Rule-based classification (logical conditions): The document also provides specific logical rules (in natural language) for identifying High, Medium, and Low risk beyond just numeric thresholds. For instance, a project is considered High Risk if any of the following hold:
        •	Expected Margin < 10% AND (Contract Type is fixed-price OR SIA Complexity ≥ 4).
        •	Project Type = Execution-only AND (SIA Complexity ≥ 4 OR Client Relationship = New).
        •	Client Type = Private AND Client Relationship = New AND Expected Margin < 15%.

These are explicit conditions that trigger a High risk classification. Similarly, Medium Risk was described with a combination of margin in 10–15% and either non-execution project with complexity 3 or a fixed-price contract, and Low Risk described by margin >15% and either government client or established client with no execution-only.
 
We can encode these as Prolog rules as well:

---------------------------------------------------
high_risk_condition(Margin, ProjType, Sia, Contract, Rel, Client) :-
    Margin < 10,
    (Contract = fixed_price; Sia >= 4).
high_risk_condition(Margin, ProjType, Sia, Contract, Rel, Client) :-
    ProjType = execution_only,
    (Sia >= 4; Rel = new).
high_risk_condition(Margin, ProjType, Sia, Contract, Rel, Client) :-
    Client = private,
    Rel = new,
    Margin < 15.
---------------------------------------------------

(And similarly one could write medium_risk_condition(...) and low_risk_condition(...) rules for the other criteria.)
The Prolog classification can then use these as overrides or checks. One strategy is to prioritize the logical rules for High risk: if any high_risk_condition is true, we classify as high regardless of the numeric score. For example:

---------------------------------------------------
determine_risk(Margin, ProjType, Sia, Contract, Rel, Client, Score, high) :-
    high_risk_condition(Margin, ProjType, Sia, Contract, Rel, Client).
determine_risk(_, _, _, _, _, _, Score, medium) :-
    Score >= 40, Score =< 70.
determine_risk(_, _, _, _, _, _, Score, low) :-
    Score < 40.
---------------------------------------------------

Here, the first rule will succeed if any high-risk pattern is met (we don't even care what the numeric Score is in that case). If that fails, we fall through to checking the numeric range for medium or low. We might also encode the Medium and Low logical conditions similarly and cross-verify. However, since the threshold method already covers typical medium/low, we can keep it simple: apply explicit High risk triggers, otherwise use the score thresholds for Medium vs Low. This ensures we don't miss scenarios where the numeric score might underestimate risk.
 
It’s worth noting that if the user heavily changes weights, the numeric thresholds might shift in meaning (but since we always normalize weights to sum 1, the 0–100 scale remains, so thresholds 40/70 still apply). The explicit conditions are independent of weights (they look at the raw inputs), which is fine as they represent domain expert rules.
 
In summary, the Prolog assess_risk logic will likely do:

    1. Calculate TotalScore using attribute scores.
    2. Check for high_risk_condition(s). If true, classify as high.
    3. Else, if TotalScore > 70 then high, else if >=40 then medium, else low (this double covers high, but our high_risk_condition might catch some cases even if score <= 70).
    4. (Optionally, check medium and low conditions explicitly, but those mostly align with numeric criteria we set.)

We will test to ensure no contradictions arise (in case a scenario meets a high-risk rule but has a low numeric score – our logic as written would classify high due to the condition rule, which is what we want).

•	Mitigation Suggestions Generation: The Prolog knowledge base can also hold suggestions corresponding to each risk level. The document suggests tailored strategies for high-risk projects. We will implement a simple mapping, for example:

---------------------------------------------------
mitigations(low, []).
mitigations(medium, ["Ensure regular monitoring and communication."]).
mitigations(high, [
    "Reassign critical tasks to senior staff&#8203;:contentReference[oaicite:41]{index=41}",
    "Reduce workload on less critical tasks to free resources&#8203;:contentReference[oaicite:42]{index=42}",
    "Extend project timeline to avoid overtime costs&#8203;:contentReference[oaicite:43]{index=43}",
    "Simplify project scope to eliminate non-essential features&#8203;:contentReference[oaicite:44]{index=44}"
]).
---------------------------------------------------

In the above, Low risk has no suggested actions (empty list or maybe a note that no major mitigation is needed), Medium might have a generic suggestion or two (since the document focused mostly on high risk mitigations), and High risk has a list of concrete actions. The examples included (cited from the document) cover resource reassignment, reallocation, timeline adjustment, scope reduction, etc., which directly address high-risk factors. We have included a few as an illustration – in implementation we might include all relevant suggestions from the table (team composition changes, outsourcing, etc.). These suggestions will be returned as a list of strings.
 
Alternatively, we could generate suggestions conditionally (e.g., if the project is high risk because of low margin, then include a suggestion about adjusting pricing). However, that level of granular tailoring may be beyond scope initially. Instead, we provide a fixed set of best-practice mitigations for any high risk project, which is simpler and still useful.

•	Main Predicate: We will write a main predicate assess_risk that ties everything together. This predicate will take all six inputs (and possibly the weights), compute the total score, determine the risk classification, and fetch the suggestions. For example:

---------------------------------------------------
assess_risk(Margin, ProjType, Sia, Contract, Rel, Client, Risk, Suggestions) :-
    % calculate total score
    total_score(Margin, ProjType, Sia, Contract, Rel, Client, Score),
    % determine risk level
    (  high_risk_condition(Margin, ProjType, Sia, Contract, Rel, Client)
    -> Risk = high
    ;  (Score > 70 -> Risk = high;
         Score >= 40 -> Risk = medium;
         Risk = low)
    ),
    % get suggestions for that risk
    mitigations(Risk, SuggestionsList),
    Suggestions = SuggestionsList.
---------------------------------------------------

If we include weights as parameters, assess_risk would have six extra params and call total_score with weights accordingly. But assuming default weights are embedded, the above is the logic. We use Prolog’s if-then (->) and semicolon for else to handle the priority of high risk condition. This ensures that any high-risk pattern results in Risk = high immediately. Otherwise, we fall through to use the numeric threshold classification. We then retrieve the corresponding SuggestionsList and unify it with Suggestions to return it. The Suggestions could be a list or a single string; in our design, we’ll treat it as a list of strings for flexibility. (When converting to display, the Python side will iterate the list.)

    •	Prolog Enumerations and Data Types: The Prolog code will treat ProjType, Contract, etc., as atoms as given (we'll ensure to use the same atoms from the input mapping). SIA complexity will be treated as an integer (which is fine for numeric comparison in Prolog). The margin is a float, and SWI-Prolog can handle comparisons with floats as used above. We must be careful to include the is operator when doing arithmetic (Score is ...) and use comparison operators for numeric comparisons (<, =<, >, >=) as in the examples.

    •	Knowledge Base Initialization: We will include all the above facts and rules in the Prolog source file. Additionally, we might include some documentation or :- use_module(library(clpfd)). if needed for constraints (though simple arithmetic comparisons don’t need it). We will test the Prolog knowledge base independently with some queries to ensure it behaves as expected (for example, querying assess_risk(5, execution_only, 5, fixed_price, new, private, Risk, Sug) should yield Risk = high with a list of suggestions, given that 5% margin, execution-only, etc., is a worst-case scenario).

By encoding the scoring tables and logical rules in Prolog, we leverage the knowledge-based approach to determine risk. The structure mirrors the expert rules and weights given in the document: each attribute’s impact is quantified and the final decision is derived through a combination of numeric scoring and logical conditions. This Prolog knowledge base serves as the “brain” of our application, which the Streamlit front-end will query.

Integration with Prolog Backend (PySWIP or Subprocess)
To connect the Streamlit app with the Prolog logic, we will use one of two approaches:
 
1. PySWIP (SWI-Prolog Python Integration): PySWIP is a library that allows embedding SWI-Prolog into Python. Using PySWIP, we can load the Prolog knowledge base and query it directly from within the Streamlit app:
•	We will install PySWIP in the project environment (e.g., via pip). We must also ensure SWI-Prolog is installed on the server where the Streamlit app runs, as PySWIP interfaces with it.
•	At the top of our Streamlit app script (or in a cached function), we will initialize the Prolog engine:

---------------------------------------------------
from pyswip import Prolog
prolog = Prolog()
prolog.consult("risk_rules.pl")  # load our Prolog knowledge base
---------------------------------------------------

We will do this once (perhaps using @st.cache_resource to avoid reloading on each run). If risk_rules.pl is in the app directory, this will load all our facts and rules.

•	When the user submits the form, and after input validation, we will construct the query string. For example:

---------------------------------------------------

query_str = f"assess_risk({margin}, {proj_atom}, {complexity}, {contract_atom}, {rel_atom}, {client_atom}, Risk, Suggestions)"

---------------------------------------------------

If we included weights as parameters, we would append the six weight values in order as well. For now, assume default weights inside Prolog, so we don't pass them.

•	We will then invoke the query:

---------------------------------------------------

results = list(prolog.query(query_str))

---------------------------------------------------

The result will be a list of solution dictionaries (PySWIP returns Prolog variable bindings as Python dicts). We expect one solution, e.g., results[0] might be {'Risk': 'high', 'Suggestions': ['Reassign critical tasks...', 'Extend project timeline...', ...]}. (PySWIP will likely return atoms as Python strings, and lists as Python lists of strings.)

•	We parse the result: extract risk_level = results[0]["Risk"] and suggestions = results[0]["Suggestions"]. If the Prolog code returns the suggestions as a list of atoms or a list of strings, PySWIP should convert them to Python list of strings. We will confirm this with testing. If it's a single string or a complex term, we adjust accordingly (possibly modifying Prolog to ensure it's a straightforward list).
•	Finally, we use risk_level and suggestions to display output as described in the UI section. We might want to capitalize the risk level for display (e.g., "High" instead of "high"). We can do risk_level.capitalize() in Python.

Using PySWIP keeps everything in one process and avoids parsing raw text output. It gives us structured data directly.

2. Subprocess calling SWI-Prolog: If PySWIP proves difficult (sometimes installation or environment issues can occur), an alternative is to run the Prolog engine as an external process. This approach would involve:
•	Ensuring the SWI-Prolog executable (swipl) is available on the system.
•	Using Python’s subprocess module to call a command that loads the Prolog file and executes the query. For example:

---------------------------------------------------
import subprocess
cmd = [
    "swipl", 
    "-q",  # quiet mode (no informational output)
    "-s", "risk_rules.pl",  # consult our knowledge base
    "-g", query_str,        # execute the query goal
    "-t", "halt"            # halt after query finishes
]
result = subprocess.run(cmd, capture_output=True, text=True)
output = result.stdout
---------------------------------------------------

Here, query_str would need to be something like "assess_risk(12.5, planning_and_execution, 3, hourly, established, government, Risk, Suggestions), write(Risk), write(','), write(Suggestions)". We include write statements to output the variables to stdout in a parseable way (separating risk and suggestions by a comma or special delimiter). The output might look like high,[Reassign critical tasks..., Extend project timeline,...] as a raw text.

•	We would then parse the text. For example, split at the comma to get risk part and suggestions part. We might need to do some string cleaning (remove brackets and quotes, etc., to reconstruct a Python list of suggestions).

•	This method is more error-prone in parsing and somewhat slower (it starts a new Prolog process for each query), but it's a viable fallback if embedding fails. For a single query at a time, performance is not a big concern, but we would prefer PySWIP for elegance and speed.

In either case, we will implement error handling (described in the next section) around the Prolog call. For development and testing, PySWIP is convenient. We will make sure to properly handle the case where no solution is found or an error occurs (though ideally, our assess_risk predicate should always succeed with one solution given valid inputs).
 
Session Management: Streamlit runs the script top-to-bottom on each interaction, which means if we naively consult the Prolog file inside the submit handler, it might reload it each time. To avoid reloading the knowledge base on every form submission, we will initialize the Prolog environment exactly once. We can do this with Streamlit’s session state or caching:
•	Use st.session_state: e.g., do if 'prolog' not in st.session_state: st.session_state.prolog = Prolog(); st.session_state.prolog.consult("risk_rules.pl"). Then use st.session_state.prolog.query(query_str). This keeps the Prolog engine alive across runs.
•	Or use @st.cache_resource on a function that returns an initialized Prolog instance. Cached resources persist across reruns unless the file changes.

This ensures efficiency. It also means any dynamic changes to rules (unlikely in this app) would not be picked up unless we clear cache, but since rules are static (except weight parameters which we pass in), that's fine.
 
Testing the Prolog Query: We will test queries with known inputs to ensure the integration works:
•	For example, call assess_risk(5, execution_only, 5, fixed_price, new, private, Risk, Suggestions) via PySWIP and see if we get Risk = high. We will do this during development in a separate environment or within the app with test inputs.
•	Ensure that the data types come through correctly (e.g., Margin as float, Sia as int, atoms as atoms). If something is off (like Prolog expecting an atom and getting a Prolog string), we might adjust by quoting the atom in the query string or using PySWIP Atom class. Since we plan to supply atoms as raw lowercase strings in the query text, it should be fine.

By integrating via PySWIP, the Streamlit app can directly leverage the Prolog engine. The user experience will be clicking "Evaluate Risk" and, under the hood, the app does Prolog.query to get results in milliseconds. This feels instantaneous to the user. The complexity of the Prolog inference is hidden behind a simple Python call, making our interface responsive and interactive.

## Part IV: Error Handling and Fallback Strategies
Robust error handling is crucial to ensure the app doesn’t crash and provides useful feedback if something goes wrong. We will implement the following safeguards and fallbacks:

•	Prolog Engine Availability: If the Prolog backend is not set up or fails to load, the app should detect this and respond gracefully:
    •	When consulting the Prolog file, we will wrap the call in a try-except. For example:

---------------------------------------------------
try:
    prolog.consult("risk_rules.pl")
except Exception as e:
    prolog_available = False
    st.error("Knowledge base could not be loaded. Risk assessment is unavailable.")
else:
    prolog_available = True
---------------------------------------------------

If the Prolog file is missing or has syntax errors, this will catch it. We’ll set a flag prolog_available. If false, our submit handler can either skip calling Prolog or use a fallback logic (see below).
    •	Similarly, if using subprocess, check the return code. If result.returncode != 0, that means Prolog encountered an error. We would then log result.stderr (possibly print to console or show a brief message to user like "Internal error in risk evaluation").

•	Query Execution Errors: Even if the KB loads fine, something could go wrong during query (though our rules are straightforward). We will still guard the query call:

---------------------------------------------------
try:
    results = list(prolog.query(query_str))
except Exception as e:
    st.error("An error occurred while evaluating risk. Please try again.")
    # Optionally log e for debugging.
    return
---------------------------------------------------

If a query times out or returns no results (which would be unusual here), we handle that. In case of no result, results list would be empty. We can check:

---------------------------------------------------
if len(results) == 0:
    st.error("Unable to determine risk with the given inputs.")
    return
---------------------------------------------------

This scenario might occur if inputs somehow don't match any rule (which shouldn't happen, since our risk rules cover all cases, but it's a safety net).

•	Input Validation Errors: As described, if weights sum is wrong, we show an error and do not call Prolog. The user can fix and resubmit. Similarly, if any required field is missing (Streamlit forms typically ensure something is selected for selectboxes/radios by default, so missing data is unlikely), we would handle that before query. We might mark fields as required in the UI text.

•	Fallback without Prolog: If prolog_available is False (e.g., during early development or if deployed somewhere without SWI-Prolog), we will use a Python fallback to compute the risk. This ensures the app still functions (perhaps with a note that it’s in "demo mode"). The fallback could simply mimic the Prolog logic:
    •	We will implement a Python function compute_risk_python(margin, proj_type, sia, contract, rel, client, weights) that uses the same rules. For example, it would:
        •	Determine each attribute score (using the same thresholds: margin <10 -> 30, etc.).
        •	Sum to get total_score.
        •	Apply the 40/70 thresholds for risk classification.
        •	(Optionally apply the high-risk override rules as well).
        •	Return risk and suggestions list.
    •	If Prolog is not available, our submit handler will call this Python function instead of prolog.query. The user should ideally not notice any difference in output.
    •	We will clearly comment this in code and possibly log a warning. If this app is intended for production use, we’d want the Prolog backend set up; the Python fallback is mainly for testing and ensuring continuity.

•	Synchronizing Fallback with Prolog: We must keep the Python logic consistent with the Prolog logic. Whenever we update rules in Prolog, we should update the Python fallback. This duplication is acceptable for a small rule set and aids testing. In fact, this provides a way to unit-test the intended logic without Prolog.

•	User Feedback and Logging: For any error that we catch and handle, we’ll provide user feedback via st.error or st.warning as appropriate. But we will avoid exposing technical details to the user in the UI (to not confuse them). Instead, we may log technical errors in the server logs for debugging. For instance, if prolog.consult fails due to a syntax error in the Prolog file, we might log the exception message. If the Prolog query fails due to a missing SWI installation, the exception might indicate that, and we could log it as well.

•	Edge-case Handling:
    •	If by some chance the user inputs extremely unusual values (like margin = 100 or complexity outside 1-5 via some bug), our fallback and Prolog might not have rules. The Prolog margin_score rules, for example, don’t explicitly handle margin = 100, but the < 10 / >= 10, =<15 / >15 covers it (100 > 15 -> score 0, which is fine). Complexity outside 1-5 wouldn’t match any fact; in Python fallback we could clamp it to 5 if >5 or to 1 if <1. But the UI already restricts complexity slider to [1,5]. So we are safe.
    •	If suggestions list is empty (for low risk), we will simply not display the suggestions section or show a message "No mitigations required." Our code will handle both cases (if Suggestions list is empty vs non-empty).

•	Parallel Queries or State: The app is single-user interactive, but if deployed and multiple users use it concurrently, each click triggers a separate run. PySWIP’s Prolog engine might be shared; however, since our queries have no side effects (we’re not asserting/retracting facts per query), it should handle concurrent queries fine. If needed, we can instantiate a new Prolog for each query, but that’s heavier. PySWIP doesn’t inherently support multi-threaded queries; since Streamlit runs each session separately (each user in a separate session state), we might be okay. It’s something to be aware of if scaling up. As a fallback, using subprocess would avoid any state conflict because each query is isolated.

By implementing these error handling measures, we ensure the application is robust. In the worst case scenario (no Prolog engine), the app still produces a result using the encoded logic in Python, thereby demonstrating the functionality. In the best case (Prolog running), any issues will be caught and reported without causing the app to crash or hang indefinitely.

## Part V: Testing and Development Plan (Without Full Prolog Implementation)

During development, we will take a phased approach to test the interface and logic even before the Prolog backend is fully implemented:
•	UI Component Testing: First, we will run the Streamlit app with just the UI form (no Prolog calls) to ensure all widgets display correctly and the expander for weights works. We will manually verify:
    •	The default values are correctly set (e.g., the weight fields show 0.30, 0.20, etc., summing to 1.0).
    •	Changing values in the form does nothing until hitting submit (with st.form, this is the case).
    •	The help texts on inputs (if implemented) appear when hovering the info icon.
    •	The layout is visually clean (e.g., maybe adjust using st.columns if needed to align some fields, though likely fine vertically).

•	Validation Testing: Next, test the validation logic:
    •	Try an incorrect weight combination (e.g., set weights summing to 0.8) and hit "Evaluate Risk". Expect an error message and no further output. Adjust weights to fix sum and resubmit, now it should proceed.
    •	Leave all weights at default (sum=1) and submit to ensure it passes validation.
    •	Test boundary cases for margin input: 0%, 10%, 15%, >15%. We will print or log what category our Python fallback puts these in (to verify the thresholds are applied as intended: <10 should be considered high risk factor, 10 exactly should fall in medium category range 10–15, 15 exactly medium, 16 as >15 should be low risk factor for margin).
    •	If negative margin were allowed, test -5 (should likely be treated as <10, and thus high risk factor for margin). But if we disallow negatives in the input, this is moot.

•	Python Logic Simulation: Before the Prolog rules are ready, we implement compute_risk_python that mirrors the Prolog logic:

---------------------------------------------------
def compute_risk_python(margin, proj_type, sia, contract, rel, client, weights):
    # weights is a tuple/list of 6 weights summing to 1
    # Compute scores:
    score = 0
    # Margin score
    if margin < 10: score += 30 * (weights[0]/0.30)  # adjust if weights changed
    elif margin <= 15: score += 15 * (weights[0]/0.30)
    # else >15: score += 0
    # Project Type score
    if proj_type == "execution_only": score += 20 * (weights[1]/0.20)
    elif proj_type == "planning_and_execution": score += 10 * (weights[1]/0.20)
    # planning_only: +0
    # ... and so on for other attributes ...
    # After summing:
    risk = None
    if score > 70: risk = "High"
    elif score >= 40: risk = "Medium"
    else: risk = "Low"
    # Suggestions based on risk
    if risk == "High":
        suggestions = ["Reassign critical tasks to senior staff", "Extend project duration to avoid overtime", ...]
    elif risk == "Medium":
        suggestions = ["Maintain frequent client communication", "Allocate contingency budget"]
    else:
        suggestions = []
    return risk, suggestions
---------------------------------------------------

This function uses the same thresholds and default scores. Notice we included a factor (weights[i]/default_weight) to adjust the score if weights changed. For example, if the margin weight is increased to 0.40, (weights[0]/0.30) would be 1.333, so a <10% margin would score 30*1.333 = 40, effectively reflecting the new weight. This approach ensures the Python simulation aligns with what the Prolog dynamic weighting would do. We will test this function with various weight sets:
    •	Default weights (should replicate Table 4–9 exactly).
    •	Custom weights (e.g., all equal ~0.167 each, or one attribute weighted very high and others low) to see if the risk classification shifts intuitively.

•	Manual Test Cases: We will run a series of test cases through the Streamlit app using the Python fallback to verify correctness:
    1.	High Risk Scenario (expected): e.g. Margin = 5%, Project Type = Execution Only, Complexity = 5, Contract = Fixed, Client Rel = New, Client Type = Private. We predict this is High risk by both rule (it triggers multiple high-risk conditions) and score (likely near 100). The app should output "High Risk" and list mitigations. We verify the suggestions appear.
    2.	Low Risk Scenario: e.g. Margin = 20%, Project Type = Planning Only, Complexity = 1, Contract = Hourly, Client Rel = Established, Client Type = Government. This should be Low risk (good margin, minimal complexity, etc., matches the low-risk conditions). The app should output "Low Risk" and either no suggestions or a message like "No major risks identified." We verify the formatting (maybe it just shows "Low Risk" in green and no suggestions section).
    3.	Medium Risk Scenario: e.g. Margin = 12%, Project Type = Planning & Execution, Complexity = 3, Contract = Fixed, Client Rel = Established, Client Type = Private. This is a mixed case: margin is mid-range, contract is riskier type, complexity moderate. Numerically, margin 12% gives 15 points, fixed contract 15 points, complexity 3 gives 9, project type 10, relationship 0, client 10 → total ~59 points. That falls in Medium range (40–70). Also check rule: margin in 10–15 and contract fixed triggers the Medium rule condition from doc. So it should classify as Medium. The app should show "Medium Risk" (perhaps in amber). We also verify if any suggestions are given for Medium (we might have one generic suggestion).
    4.	Edge of Boundary: Margin = 10% exactly, with other factors neutral. According to numeric rules, 10% is within 10–15, which yields 15 points, so one might be borderline. We can test margin = 10, others such that total = 40 exactly (say project type planning only 0, complexity 1 ->0, contract hourly 0, rel established 0, client government 0, total 15 actually). Actually to get exactly 40, we might do margin 10% (15 pts) and client private (10) and rel new (10) and something that gives 5 more, but none gives 5, complexity level2 gives 6, that would total 41. Alternatively margin slightly under 10 can yield 30, plus something 10 = 40. For example, margin 9.5% (30) + client private (10) = 40. That should classify as Medium (since 40 is the lower bound of medium range). Meanwhile 39 would be Low. We test such boundary to ensure our inequality signs are correct (we used Score >= 40 as medium, so 40 counts as Medium as intended).
    We will compare the output of the Python simulation to the expected outcomes from the document rules for each case, ensuring they match the expert criteria given.

•	Integrating Prolog Backend: Once the Python logic is verified, we will integrate the actual Prolog. Initially, we can run the Prolog file in SWI-Prolog REPL with test queries to ensure it yields correct answers:
    •	Query some known cases as above in the Prolog interpreter. Check that the risk outcome and any suggestions unify as expected. This will catch any mistakes in Prolog syntax or logic (for instance, if our high_risk_condition rules need tweaking).
    •	After that, switch the Streamlit code to use PySWIP. Then test the same scenarios through the Streamlit UI but now with Prolog answering. If we've done everything right, the outputs should be identical to the Python fallback's outputs. We will verify they are.
    •	We should also test a scenario where the high-risk logical rule overrides the numeric. For example, margin 18% (which by itself is 0 points) but Project = Execution-only, Complexity = 5, New client. Numerically: 0 + 20 + 15 + (contract say hourly 0) + 10 + (client private 10) = 55 (Medium by score). But logically, execution-only with complexity ≥4 and new client meets a high-risk condition. Our system should classify that as High (due to the rule override). We test this with Prolog to ensure high_risk_condition triggers. This validates that our combined logic is working (and is an example where expert rules augment the numeric method).

•	Performance Test: The dataset (6 inputs) is very small, so performance isn’t a big issue. But we will ensure that repeated submissions don’t lead to resource leaks or slowdown:
    •	With PySWIP, ensure that each query doesn’t accumulate facts or leave choicepoints. Since our queries are deterministic (especially after adding cut or making conditions mutually exclusive), they should not leave open choice points. We might consider adding a cut (!) in the assess_risk predicate after determining risk, to prevent backtracking into alternative rules, but given our structure that might not be necessary. We’ll monitor if PySWIP returns more than one result when it shouldn’t.
    •	With subprocess method (if used), each call is independent but slower. We’d test that even that completes within, say, <1 second, which it should for a single query.

•	User Acceptance Testing: Finally, we can have a domain expert or a stakeholder try the app with various scenarios to see if the results align with expectations. They might try edge cases like "What if complexity is 5 and everything else looks good, does it show Medium or Low?" etc. We’ll collect feedback and adjust the rules if needed.

Overall, by first using a Python simulation of the logic, we de-risk the development process: we can refine the logic quickly in Python, validate it against the documented criteria, and then confidently implement the same logic in Prolog. This way, when we switch to the Prolog backend, we already know the expected outcomes and can catch any integration issues. Additionally, this approach means the interface (Streamlit) can be fully tested without waiting for the Prolog component, providing a faster development cycle.

## Part VI: Mapping of Scoring Tables and Rules to Prolog Code

(Summary for clarity:) The scoring tables (Tables 4–9) have been directly translated into Prolog facts/rules under margin_score, project_score, complexity_score, etc., using the exact values from the tables. The normalized weights (Table 3) are inherently reflected in those scores (e.g., 30 points for margin corresponds to the 30% weight). The logical risk classification rules from the document have been captured in the Prolog high_risk_condition and similar predicates, while the numeric threshold criteria are implemented in risk_classification rules using the 40 and 70 cutoffs. Finally, the mitigation strategies outlined (such as reassigning staff, adjusting timeline, simplifying scope are stored in the Prolog knowledge base via the mitigations predicate, so that the Prolog query returns not just a risk level but also a tailored list of suggestions for high or medium risk cases.
 
By following this implementation plan, we will build a Streamlit web interface that is user-friendly and backed by a Prolog expert system. The plan covers all aspects from input UI design to Prolog integration, with careful attention to validation, error handling, and testability. This ensures that even before the Prolog component is fully ready, we can verify the behavior and provide a reliable tool for assessing project risk and profitability. The end result will be a seamless interface where users input project parameters and instantly receive a risk classification and guidance, powered by the encoded knowledge of domain experts.

