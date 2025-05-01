# Project Risk Assessment Tool – Implementation

## Introduction
This document outlines the implementation of a Streamlit-based Project Risk Assessment Tool. The tool assesses project risk (Low, Medium, High) and provides mitigation suggestions using a knowledge-based approach. The solution is implemented with a Streamlit front-end and a SWI-Prolog knowledge base for risk logic, connected via the PySWIP Python-Prolog interface. All risk computations are performed by Prolog rules; there is no fallback Python logic for scoring. The following sections describe the code structure, data flow, and integration details, reflecting the actual code (module names, functions, and variables) in the project.

## Project Structure and Components
The codebase is organized into the following files and modules:

    •	app.py– Streamlit application script providing the user interface. It collects user inputs (project parameters and optional weight adjustments), calls the risk assessment logic, and displays results.
    •	utils/prolog_interface.py– Python module that initializes a PySWIP Prolog engine, loads the Prolog knowledge base, and defines a helper function assess_risk(...) to query the Prolog engine with given inputs.
    •	prolog/risk_rules.pl– SWI-Prolog knowledge base containing the risk scoring rules, risk classification thresholds, and mitigation advice. This file defines the predicate assess_risk/7 that encapsulates the risk evaluation logic.
    •	utils/__init__.py– An initializer (may be empty) to make the utils directory a Python package. No significant logic is defined here.
    •	requirements.txt– Lists project dependencies, for example: streamlit for the UI and pyswip for Prolog integration (along with the need for SWI-Prolog installation). Ensuring these are installed is necessary to run the application.

Below, we delve into each component and describe how they work together to implement the risk assessment functionality.

## Streamlit Frontend Application (app.py)
The ### app.py ### module is the entry point that defines the web interface using Streamlit. It is responsible for gathering user input, handling form interactions (including dynamic weight overrides), and presenting the risk assessment results. Key aspects of the front-end implementation include:

### Form Inputs for Project Parameters
Using a Streamlit form (st.form("risk_form")), the app collects all necessary project attributes from the user. The form fields correspond to the factors considered in risk evaluation:

    •	Expected Margin (%) – Numeric input (st.number_input) for the project's expected profit margin as a percentage. (Default value: 0.0; range 0.0–100.0; step 0.1).
    •	Project Type – Categorical selection (st.selectbox) with options:
        o	"Execution Only"
        o	"Planning Only"
        o	"Execution & Planning"
    •	SIA Complexity Level – An integer slider (st.slider) for project complexity on a scale of 1 to 5 (according to Swiss SIA levels). (Default value: 3).
    •	Contract Type – Categorical option (st.radio) with choices:
        o	"Fixed Price"
        o	"Hourly"
    •	**Historical Client Relationship** – Categorical option (st.radio) indicating the prior relationship with the client:
    o	"New" (first-time client)
    o	"Established" (repeat client)
    •	Client Type – Categorical option (st.radio) for client sector:
        o	"Private"
        o	"Government"

Each of these inputs maps to a parameter used in the risk assessment logic. The form is encapsulated with a submit button labeled **"Evaluate Risk"**. Users enter all fields and then click this button to run the analysis.

### Dynamic Weight Adjustment Controls
Within the form, the app provides an expandable section (st.expander("Adjust Attribute Weights")) that allows the user to override the default importance weights of each attribute. This is useful for what-if analysis or to tune the model. Six numeric inputs (st.number_input) are presented, one for each attribute:

    •	Weight: Margin – default **0.30** (30% weight)
    •	Weight: Project Type – default **0.20** (20%)
    •	Weight: SIA Level – default **0.15** (15%)
    •	Weight: Contract Type – default **0.15** (15%)
    •	Weight: Client Relationship – default **0.10** (10%)
    •	Weight: Client Type – default **0.10** (10%)

These default values sum to 1.00 (100%), reflecting the initial weight distribution used in the Prolog rules. The user can adjust these sliders/numbers to redistribute the weights as long as the total remains 1.0.
After the user fills in the form and presses **"Evaluate Risk"**, the app performs a validation on the weights:

    •	It calculates total_weight = w_margin + w_proj + w_sia + w_con + w_rel + w_cli.
    •	If the sum is not approximately 1.0 (a tolerance of 1e-6 is used for floating-point safety), the app will display an error message using st.error, indicating the weights must sum to 1.0 and showing the current sum. In this case, the risk assessment is **not executed** until the weights are corrected.
    •	If the weights sum correctly to 1.0, the input is considered valid, and the app proceeds with the risk computation.

**How the weight overrides are used**: The weight inputs do not directly alter the logic in the code – instead, they are meant to ensure consistency with the underlying model. The Prolog knowledge base uses fixed score contributions that correspond to the default weights (as percentages of a total score of 100). By allowing the user to adjust and normalize weights, the tool ensures the user’s perspective on attribute importance is captured. Currently, the implementation **does not dynamically rewrite the Prolog rules** based on these inputs; rather, it assumes the default weight distribution. In effect, the weight sliders serve as a transparency and validation mechanism. (In future iterations, these weights could be passed into Prolog or used to scale the scoring, as discussed later in improvements.)

###  Input Mapping and Query Preparation
Once inputs are validated, app.py prepares the data for the Prolog query:

    1.	Categorical Value Mapping – The UI selections (strings) are mapped to Prolog-friendly atoms. The code uses Python dictionaries to translate human-readable options into the identifiers expected by risk_rules.pl:
        o	pt_map for Project Type:
            	"Execution Only" → "execution_only"
            	"Planning Only" → "planning_only"
            	"Execution & Planning" → "planning_and_execution"
        o	contract_map for Contract Type:
            	"Fixed Price" → "fixed_price"
            	"Hourly" → "hourly"
        o	rel_map for Client Relationship:
            	"New" → "new"
            	"Established" → "established"
        o	client_map for Client Type:
            	"Private" → "private"
            	"Government" → "government"

These mappings ensure the values will match exactly the atoms used in the Prolog rules (for example, the Prolog knowledge base expects execution_only or fixed_price as atoms, not the raw UI strings).

    2.	Function Call to Risk Logic – After mapping, the app calls the function assess_risk(...) from the utils.prolog_interface module. This call passes the user inputs in the following order:


---------------code-block---------------

    risk, suggestions = assess_risk(
        margin_value,
        pt_map[proj_type],
        sia_level_value,
        contract_map[contract],
        rel_map[rel],
        client_map[client]
    )

---------------code-block-end---------------

For example, if the user entered Margin 8.0, Project Type "Execution Only", SIA 5, Contract "Fixed Price", Relationship "New", Client "Private", the call becomes:

---------------code-block---------------

    risk, suggestions = assess_risk(8.0, "execution_only", 5, "fixed_price", "new", "private")

---------------code-block-end---------------

This function will execute the Prolog query to determine the risk category and suggestions (explained in the next section). The application expects risk to be a string ("low", "medium", or "high") and suggestions to be a list of suggestion strings.

### Displaying Results to the User
Once the assess_risk function returns, app.py handles displaying the outcome:

•	Risk Level Output: The risk level string (risk) is checked, and a colored message is shown:
        
    o	If risk == "high", st.error("High Risk") is used to display a red alert box indicating high risk.
    o	If risk == "medium", st.warning("Medium Risk") is used for a yellow warning box.
    o	If risk == "low", st.success("Low Risk") is used for a green success box.
    o	(If for some reason an unexpected value like "unknown" were returned, it could be handled as a generic info or error, but in normal operation the outputs are one of the three known categories.)

•	Mitigation Suggestions: If the suggestions list is not empty, the app presents a section with additional guidance:

    o	A subheader st.subheader("Mitigation Suggestions") is shown to label the section.
    o	Each suggestion string in the list is printed as a bullet point (st.write("-", item) for each item). For example, if suggestions = ["Reassign critical tasks to senior staff.", "Extend project timeline to avoid overtime."], the app will list:
        	Reassign critical tasks to senior staff.
        	Extend project timeline to avoid overtime.

If the project risk is Low (typically suggestions would be an empty list in that case), no suggestions are displayed, and the section is skipped entirely.

The Streamlit app thus provides an interactive form, immediate validation of weight consistency, calls the Prolog-based logic, and cleanly displays the classified risk level along with any recommended mitigations.

## SWI-Prolog Knowledge Base (risk_rules.pl)
The core risk assessment logic resides in the Prolog knowledge base file risk_rules.pl. This file encodes domain knowledge as rules and facts, determining how input parameters translate to a risk score, how that score is classified, and what suggestions to provide. Below is an overview of the structure and logic defined in this Prolog module:

### Attribute Scoring Rules
Each risk factor (attribute) has an associated scoring rule that contributes a certain number of points to an overall risk score. These points reflect the relative weight (importance) of that factor in the risk assessment. All scores are scaled such that the maximum total score is 100 (when all risk-contributing factors are at their most extreme). The rules are defined as Prolog predicates that map an input value to a score:

    •	Margin Score (margin_score(M, Score)): Determines points based on the expected profit margin M:
        o	If M < 10 (very low margin), assign 30 points (highest risk contribution for margin).
        o	If 10 <= M <= 15, assign 15 points (moderate risk).
        o	If M > 15, assign 0 points (margin is healthy, so no risk points from this factor).
    •	Project Type Score (project_score(Type, Score)): Points based on project scope:
        o	execution_only projects → 20 points (higher risk due to single-phase focus),
        o	planning_and_execution → 10 points (medium risk, balanced),
        o	planning_only → 0 points (lower risk scenario).
    •	SIA Complexity Score (complexity_score(Level, Score)): Points by SIA complexity level:
        o	Level 5 (highest complexity) → 15 points,
        o	Level 4 → 12 points,
        o	Level 3 → 9 points,
        o	Level 2 → 6 points,
        o	Level 1 (lowest complexity) → 0 points.
    •	Contract Type Score (contract_score(Type, Score)):
        o	fixed_price contracts → 15 points (higher risk, since the provider bears cost overruns),
        o	hourly contracts → 0 points (lower risk, as effort is paid as it goes).
    •	Client Relationship Score (clientrel_score(Rel, Score)):
        o	new client → 10 points (riskier due to unknown client reliability),
        o	established client → 0 points (trusted relationship, no added risk points).
    •	Client Type Score (clienttype_score(Type, Score)):
        o	private client → 10 points (can be riskier in payment or scope changes),
        o	government client → 0 points (public sector clients are assumed more stable in this context).

These values (30, 20, 15, 10, etc.) correlate with the default weight percentages defined in the UI. For instance, Margin can contribute up to 30 points out of 100 (which aligns with a 0.30 weight), Project Type up to 20 points (0.20 weight), and so on. By using a point system, the logic is implemented entirely in Prolog without needing to explicitly multiply by weights – the thresholds inherently carry the weight information.

### Risk Score Calculation and Classification
The overall risk score is calculated by summing all the individual attribute scores. This is done in the main predicate after obtaining each factor’s score:

•	The Prolog predicate assess_risk(M, P, S, C, R, T, Risk, Suggestions) first calls each of the six scoring predicates:

---------------code-block---------------

    margin_score(M, SM),
    project_score(P, SP),
    complexity_score(S, SS),
    contract_score(C, SC),
    clientrel_score(R, SR),
    clienttype_score(T, ST),

---------------code-block-end---------------

Each of these binds a score (SM, SP, SS, SC, SR, ST respectively).

•	It then computes Total is SM + SP + SS + SC + SR + ST. This Total represents the aggregated risk score (0 to 100).

After calculating the total score, the knowledge base determines the risk category. There are two ways a project can be classified as High risk: by meeting specific critical conditions, or by having a high total score. The logic is as follows:

•	High-Risk Conditions (Rule Overrides): Certain combinations of inputs trigger a High risk classification regardless of the total score. These are encoded as high_risk_condition(...) rules. If any such condition is true, the project is immediately categorized as high risk. The conditions implemented are:

    o	Projects with a very low margin in a Fixed Price contract: M < 10 and Contract = fixed_price ⇒ High Risk (because low profitability buffer on a fixed budget is dangerous).
    o	Projects that are **Execution Only** with high complexity and a new client: ProjectType = execution_only and SIA Level >= 4 and Client Relationship = new ⇒ High Risk (because a complex execution with an unknown client is very risky).
    o	Projects with a new private client and insufficient margin: Client Relationship = new and Client Type = private and M < 15 ⇒ High Risk (private new clients with low margin could indicate pricing risks or payment uncertainty).

These rules are checked in the assess_risk predicate using an if-then construct. In Prolog, it appears as:

---------------code-block---------------

    ( high_risk_condition(M, P, S, C, R, T) ->
          Risk = high
    ;   risk_classification(Total, Risk) ),

---------------code-block-end---------------

This means: if any high_risk_condition is true for the given inputs, set Risk = high; otherwise, fall through to the normal scoring classification.

    •	Score-Based Classification: If no high-risk override condition triggered, the tool uses the Total score to classify risk:
        o	risk_classification(S, high) if S > 70. (Scores above 70 out of 100 are considered High Risk.)
        o	risk_classification(S, medium) if 40 =< S =< 70. (Scores in 40–70 range are Medium Risk.)
        o	risk_classification(S, low) if S < 40. (Scores below 40 are Low Risk.)

These thresholds (40 and 70) are chosen according to the domain requirements to delineate risk levels.
Using this approach, every project will be labeled as **high**, **medium**, or **low** risk by the Prolog rule. The logic ensures one (and only one) category applies because either a high risk condition is met or the classification by score is used.

### Mitigation Suggestions
The knowledge base also stores predefined mitigation advice for each risk level, via the mitigations(Level, SuggestionsList) predicate:

    •	For low risk, the suggestions list is empty ([]), meaning no immediate action is required.
    •	For medium risk, there is a list with one suggestion:
        o	"Increase client communication." – indicating a need for more engagement to manage expectations and prevent issues from escalating.
    •	For high risk, a list of several suggestions is provided:
        o	"Reassign critical tasks to senior staff." (Mitigate risk by involving more experienced personnel)
        o	"Extend project timeline to avoid overtime." (Mitigate schedule risk by giving more buffer)
        o	"Simplify scope to reduce risk." (Mitigate scope creep or complexity risk by limiting project scope)

The assess_risk predicate, after determining the Risk category, calls mitigations(Risk, Suggestions) to retrieve the appropriate suggestion list for that risk level. This list (which may be empty or contain multiple string items) is then returned back through the Suggestions output variable.

### The assess_risk/7 Predicate
In summary, the Prolog knowledge base’s main entry point is assess_risk(M, P, S, C, R, T, Risk, Suggestions), which ties everything together:

    1.	It computes each attribute’s score via helper predicates.
    2.	Sums the scores to get Total.
    3.	Checks for any high-risk conditions; if found, sets Risk = high.
    4.	Otherwise, uses the total score to classify Risk as high, medium, or low.
    5.	Retrieves the corresponding Suggestions list for the determined risk level.

This predicate is defined to succeed exactly once per set of inputs (assuming inputs are within expected ranges and types), producing one risk classification and one suggestions list.

Because the logic is encapsulated in Prolog, adding or modifying rules (such as introducing new risk factors or conditions) can be done by editing the risk_rules.pl file without changing the Python code. The Python side simply queries this predicate to get results.

## Python–Prolog Integration (utils/prolog_interface.py)
The prolog_interface.py module serves as the bridge between the Streamlit app and the Prolog knowledge base. It uses the PySWIP library to embed a SWI-Prolog engine in Python. Key implementation details in this module include:

### Initializing the Prolog Engine and Loading Rules
When utils.prolog_interface is imported (for example, when app.py runs from utils.prolog_interface import assess_risk), the following happens:

    •	A Prolog instance is created: prolog = Prolog(). This initializes the SWI-Prolog engine in the background so that queries can be executed.
    •	The path to the risk_rules.pl file is constructed. The code uses os.path.abspath and os.path.join to find the risk_rules.pl file located in the prolog directory relative to the module. It also replaces backslashes with forward slashes for Windows compatibility. This results in a string path like /full/path/to/prolog/risk_rules.pl.
    •	The Prolog engine consults the knowledge base file to load all the rules. In code, this is done with:

---------------code-block---------------

    list(prolog.query(f"consult('{prolog_file}')"))

---------------code-block-end---------------

Using prolog.query to consult the file is a workaround for a known PySWIP issue with the consult method and file paths. This query executes the Prolog directive to load the file. After this step, the Prolog engine has all the predicates (like assess_risk/7) defined and ready to use.
(A debug print statement print("CONSULTING:", prolog_file) may be present to log the file being loaded, which helps in development to ensure the correct file is found. In production, this could be removed or replaced with proper logging.)

### The assess_risk Python Function
The prolog_interface.py module defines a function def assess_risk(margin, proj, sia, contract, rel, client): which the Streamlit app calls to perform the risk analysis. This function orchestrates the query to Prolog and handles the results:

1.	Query String Construction: The function builds a Prolog query string using the input parameters. Given the inputs (margin, proj, sia, contract, rel, client) which are expected to be Python primitives or strings:
    o	margin (float or int) and sia (int) are numeric, so they are inserted directly.
    o	proj, contract, rel, client are strings corresponding to Prolog atoms (e.g., "execution_only", "fixed_price"). These need to be quoted in the query so that Prolog interprets them as atoms (not variables). The code does this by wrapping each in single quotes within the f-string.
    o	The query is formatted as:

---------------code-block---------------

    query = (
        f"assess_risk({margin}, "
        f"'{proj}', {sia}, '{contract}', '{rel}', '{client}', Risk, Suggestions)"
    )

---------------code-block-end---------------

For example, if the function was called as assess_risk(8.0, "execution_only", 5, "fixed_price", "new", "private"), the resulting query string would be:
"assess_risk(8.0, 'execution_only', 5, 'fixed_price', 'new', 'private', Risk, Suggestions)".

Here, Risk and Suggestions are Prolog variables that will be unified with the output when the query runs.

2.	**Executing the Prolog Query**: The function calls the Prolog engine with results = list(prolog.query(query)). This sends the constructed query to the SWI-Prolog engine and collects all solutions. In this specific case, the assess_risk predicate is designed to yield one solution for valid inputs. The result is a list containing at most one dictionary. Each dictionary represents a solution, with keys corresponding to the Prolog variable names in the query. For instance, a typical result might be:
results == [ {"Risk": "high", "Suggestions": ["Reassign critical tasks to senior staff.", ...]} ].
If the input values were somehow outside the expected domain (for example, an unknown project type string), the query could return no results (an empty list).

3.	**Handling Query Results**: The code checks if results is empty:
       o	If no result was returned, the function returns ("unknown", []). This is a safety fallback indicating that the risk could not be assessed (perhaps due to an input issue). In normal operation with correct inputs, this path shouldn't occur because the UI restricts inputs to known values.
       o	If a result is present, the code takes the first (and only) solution dictionary: result = results[0]. It then extracts Risk = result["Risk"] and Suggestions = result["Suggestions"]. These correspond to the Prolog output:
           	Risk will be a Prolog atom 'low', 'medium', or 'high' which PySWIP converts into a Python string.
           	Suggestions will be a Prolog list of text (strings). PySWIP converts this into a Python list. If the list was empty in Prolog, it becomes an empty Python list []. If it contained strings, those appear as Python strings in the list.
       o	The function returns a tuple (Risk, Suggestions) back to the caller (app.py). For example, it might return ("high", ["Reassign critical tasks to senior staff.", "Extend project timeline to avoid overtime.", "Simplify scope to reduce risk."]).

This Python function abstracts away the Prolog interaction, so the Streamlit app doesn’t need to deal with query syntax or Prolog internals. It simply supplies Python values and gets Python-friendly results.
Because the Prolog engine was loaded at module import time, subsequent calls to assess_risk are fast – they re-use the already consulted knowledge base. This design ensures that the Prolog consulting (which can be relatively slow if done repeatedly) happens only once.

### No Python-side Risk Computation
It is important to note that **all risk scoring logic is executed in Prolog**. The Python code does not attempt to compute the risk level or suggestions on its own. There is no compute_risk_python or similar function in use. By centralizing the logic in the Prolog knowledge base, we avoid duplicating rules in Python. The Python side only handles input format conversion and output display. This simplifies maintenance and guarantees consistency (there’s a single source of truth for risk rules in Prolog).
The decision to not include a Python fallback means that the application relies on the Prolog engine being available and functioning. In this implementation, PySWIP suffices to bridge to SWI-Prolog, so no external swipl subprocess is invoked. The system assumes SWI-Prolog is properly installed and accessible to PySWIP. All queries are done in-memory through PySWIP's foreign function interface, which is efficient for an interactive app setting.

## Suggestions for Further Improvements
While the current implementation is fully functional, there are several opportunities to enhance modularity, flexibility, and testability:

•	**Dynamic Weight Integration**: Extend the system to truly use the user-adjusted weights. For example, the app could modify the Prolog knowledge base at runtime by scaling the score thresholds (e.g., if the user sets Margin weight to 0.25 instead of 0.30, adjust the margin_score points accordingly to max 25 points). This could be achieved by generating a Prolog query to update facts or by re-consulting a temporary Prolog file with adjusted values. This feature would make the weight sliders directly influence the outcome, providing a more interactive modeling tool.

•	**Modular Knowledge Base**: Refactor risk_rules.pl to separate clearly the knowledge (facts) from the logic. For instance, define all weight-based scores as facts or a structured list that can be easily updated or iterated over. This would simplify adding new criteria or changing weights. Moreover, consider loading multiple knowledge base files (one for scoring rules, one for thresholds and suggestions) for better organization.

•	**Automated Testing**: Develop a suite of unit tests for the risk logic. This could include:
    o	Prolog-side tests: Using PySWIP in a test environment to call assess_risk with various known inputs and verifying that the output risk and suggestions match expected values (e.g., a margin of 5% should yield High risk with specific suggestions).
    o	Python-side tests: Mock the prolog.query responses to test that prolog_interface.assess_risk correctly handles conversion of outputs (e.g., empty results, or various suggestion lists), and that app.py correctly interprets and displays them.

•	**Error Handling and Robustness**: Improve handling of unexpected scenarios. For instance, if Prolog returns an "unknown" risk (empty result) or if PySWIP encounters an error, the app could catch this and show a user-friendly message (instead of just "unknown"). Implement logging for the Prolog query and results to help debug any issues in production.

•	**Feature Expansion**: Consider incorporating additional factors into the risk assessment model (and updating the UI accordingly). For example, project timeline, budget size, or team experience could be added to the knowledge base. Thanks to the modular design, this would mainly involve updating risk_rules.pl and the Streamlit form, while the integration layer (assess_risk function) would remain largely unchanged.

•	**UI/UX Enhancements**: Provide more context to the user on what each factor means. For instance, tooltips or descriptions for each input field can guide the user. Additionally, after obtaining results, the app might display a breakdown of the score composition (how much each factor contributed) to increase transparency. This could be done by extending Prolog to return the component scores or by recalculating them in Python using the same rules for display purposes.

•	**Caching and Performance**: Although the data volume is small, using Streamlit’s state or caching (st.cache_data or similar) for the Prolog engine or results might further optimize performance, especially if the app will be used frequently or with repetitive queries. For example, ensure the Prolog consulting is done only once per session. PySWIP already handles this by persistent engine, but additional caching of results for identical inputs could be considered if needed.

