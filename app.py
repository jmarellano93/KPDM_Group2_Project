import streamlit as st
from utils.prolog_interface import assess_risk

st.set_page_config(layout="wide")

st.title("C2M Project Risk and Profitability Assessment")
st.write("""
This tool helps assess project risk based on C2M's internal financial expertise and project parameters. Please input the project details below to receive a risk classification.
""")
st.caption("C2M Project Risk Assessment Tool | Version 1.0 | Based on specifications dated 02.06.2025")

st.sidebar.header("Project Input Parameters")

with st.sidebar.form("risk_form"):
    margin_perc = st.number_input("Expected Margin (%)", min_value=-50.0, max_value=100.0, value=15.0, step=0.1, help="Predicted profitability percentage.")
    proj_type_ui = st.selectbox("Project Type", ["Planning & Execution", "Planning Only", "Execution Only"], help="Full project vs. Partial vs Execution only.")
    sia_level_ui = st.selectbox("SIA Complexity Level", ["Level 1 (Lowest Complexity)", "Level 2", "Level 3", "Level 4", "Level 5 (Highest Complexity)"], help="Project complexity from 1 to 5 based on SIA regulations.")
    contract_ui = st.selectbox("Contract Type", ["Hourly", "Fixed Price"], help="Fixed-price or hourly-based contract.")
    rel_ui = st.selectbox("Historical Client Relationship", ["Established", "New"], help="Previous experience with the client.")
    client_ui = st.selectbox("Client Type", ["Private", "Government"], help="Private individual or government project.")

    submitted = st.form_submit_button("Assess Project Risk", use_container_width=True)

# --- Input Mapping ---
pt_map = {
    "Execution Only": "execution_only",
    "Planning Only": "planning_only",
    "Planning & Execution": "planning_and_execution"
}
sia_map = {
    "Level 1 (Lowest Complexity)": 1, "Level 2": 2, "Level 3": 3, "Level 4": 4, "Level 5 (Highest Complexity)": 5
}
contract_map = {"Fixed Price": "fixed_price", "Hourly": "hourly"}
rel_map = {"New": "new", "Established": "established"}
client_map = {"Private": "private", "Government": "government"}


st.subheader("Risk Assessment Results")

if submitted:
    # Get mapped values
    proj_type_prolog = pt_map[proj_type_ui]
    sia_level_prolog = sia_map[sia_level_ui]
    contract_prolog = contract_map[contract_ui]
    rel_prolog = rel_map[rel_ui]
    client_prolog = client_map[client_ui]

    # Call the updated assess_risk function
    risk_level = assess_risk(
        margin_perc,
        proj_type_prolog,
        sia_level_prolog,
        contract_prolog,
        rel_prolog,
        client_prolog
    )

    # Display results
    if risk_level == "high":
        st.error(f"**Final Assessed Risk: High**")
        st.write("This project meets the criteria for High Risk. A senior project manager review is required before proceeding.")
    elif risk_level == "medium":
        st.warning(f"**Final Assessed Risk: Medium**")
        st.write("This project falls into the Medium Risk category. Consider a review before proceeding.")
    elif risk_level == "low":
        st.success(f"**Final Assessed Risk: Low**")
        st.write("This project is classified as Low Risk and seems financially sound based on the input parameters.")
    elif risk_level == "undefined_risk_profile":
         st.error("**Error: The project parameters did not match a defined risk profile.**")
         st.write("This should no longer occur with the updated logic, but if it does, please review inputs or check the Prolog rules.")
    elif risk_level == "error_in_assessment":
         st.error("**Final Assessed Risk: Error in assessment format**")
         st.write("There was an issue retrieving or formatting the risk assessment. Please check the console output for details.")
    else:
         st.error(f"**An unexpected result was returned: {risk_level}**")

else:
    st.info("Please enter your project parameters on the left and click 'Assess Project Risk'.")