import streamlit as st
from utils.prolog_interface import assess_risk  # Make sure this import path is correct

# Page Configuration
st.set_page_config(layout="wide", page_title="C2M Project Risk Assessment")

# Application Title
st.title("C2M Project Risk and Profitability Assessment")
st.markdown("""
This tool helps assess project risk based on C2M's internal financial expertise and project parameters.
Please input the project details below to receive a risk classification.
""")

# --- Input Parameters ---
st.sidebar.header("Project Input Parameters")

# 1. Expected Margin (%)
margin_percentage = st.sidebar.number_input(
    "Expected Margin (%)",
    min_value=0.0,
    max_value=100.0,
    value=15.0,
    step=0.5,
    help="Predicted profitability percentage (e.g., 15.5 for 15.5%)."
)

# 2. Project Type
project_type_options_map = {
    "Planning & Execution": "planning_and_execution",
    "Planning Only": "planning_only",
    "Execution Only": "execution_only"
}
project_type_display = st.sidebar.selectbox(
    "Project Type",
    options=list(project_type_options_map.keys()),
    help="Select the scope of the project."
)
prolog_project_type = project_type_options_map[project_type_display]

# 3. SIA Complexity Level
sia_level_options_map = {
    "Level 1 (Lowest Complexity)": 1,
    "Level 2": 2,
    "Level 3": 3,
    "Level 4": 4,
    "Level 5 (Highest Complexity)": 5
}
sia_level_display = st.sidebar.selectbox(
    "SIA Complexity Level",
    options=list(sia_level_options_map.keys()),
    help="Complexity based on SIA regulations (1-5)."
)
prolog_sia_level = sia_level_options_map[sia_level_display]

# 4. Contract Type
contract_type_options_map = {
    "Hourly": "hourly",
    "Fixed Price": "fixed_price"
}
contract_type_display = st.sidebar.selectbox(
    "Contract Type",
    options=list(contract_type_options_map.keys()),
    help="Select the contract type."
)
prolog_contract_type = contract_type_options_map[contract_type_display]

# 5. Historical Client Relationship
client_relationship_options_map = {
    "Established": "established",
    "New": "new"
}
client_relationship_display = st.sidebar.selectbox(
    "Historical Client Relationship",
    options=list(client_relationship_options_map.keys()),
    help="Relationship with the client."
)
prolog_client_relationship = client_relationship_options_map[client_relationship_display]

# 6. Client Type
client_type_options_map = {
    "Private": "private",
    "Government": "government"
}
client_type_display = st.sidebar.selectbox(
    "Client Type",
    options=list(client_type_options_map.keys()),
    help="Type of the client."
)
prolog_client_type = client_type_options_map[client_type_display]

# 7. Expected Absolute Profit (CHF)
expected_profit_chf = st.sidebar.number_input(
    "Expected Absolute Profit (CHF)",
    min_value=0.0,
    value=100000.0,
    step=10000.0,
    format="%.2f",
    help="Total expected absolute profit in Swiss Francs."
)

# --- Risk Assessment Button and Results ---
if st.sidebar.button("Assess Project Risk", type="primary"):
    st.subheader("Risk Assessment Results")

    final_risk = assess_risk(
        margin_percentage,
        prolog_project_type,
        prolog_sia_level,
        prolog_contract_type,
        prolog_client_relationship,
        prolog_client_type,
        expected_profit_chf
    )

    if final_risk and final_risk not in ["error_in_assessment", "undefined_risk_profile"]:
        risk_color = "green"
        if final_risk == "medium":
            risk_color = "orange"
        elif final_risk == "high":
            risk_color = "red"

        st.markdown(
            f"### Final Assessed Risk: <span style='color:{risk_color};'>{final_risk.replace('_', ' ').capitalize()}</span>",
            unsafe_allow_html=True)

        if final_risk == "high":
            st.markdown("---")
            st.subheader("Mitigation Suggestions for High-Risk Project")
            st.info(
                "The following are general mitigation strategies. Please review and tailor them to the specific context of the project.")

            # Mitigation suggestions based on Table 4 from the specification document [1]
            st.markdown("""
            **Team Composition:**
            *   Reassign to senior staff for critical tasks.
            *   Replace expensive employees with lower-cost staff.
            *(Purpose: Optimize skill-to-cost ratio; maintain quality while reducing salary costs.)*

            **Resource Allocation:**
            *   Reduce work hours on less critical tasks.
            *   Increase allocation on bottleneck phases.
            *(Purpose: Improve efficiency by reallocating effort where most impactful.)*

            **Timeline Adjustments:**
            *   Extend project duration to avoid overtime.
            *   Redistribute deadlines across employees.
            *(Purpose: Prevent costly delays and penalties due to rushed work.)*

            **Scope Simplification:**
            *   Eliminate non-essential design features.
            *   Simplify façade geometry or interior detailing.
            *(Purpose: Reduce time-intensive and costly design complexity.)*

            **Outsourcing:**
            *   Outsource structural analysis or 3D visualization.
            *   Hire external consultants only for specialized input.
            *(Purpose: Reduce fixed employee workload and gain access to niche expertise at a fixed contract price.)*

            **Material Substitution:**
            *   Replace custom or imported materials with standard local options.
            *(Purpose: Cut procurement costs and reduce construction risk.)*

            **Contract Type Change:**
            *   Propose switching from fixed-price to hourly billing for parts of the work.
            *(Purpose: Transfer some financial risk to the client; increase billing flexibility.)*

            **Client Coordination:**
            *   Limit scope creep via fixed design rounds.
            *   Set client deadlines for feedback.
            *(Purpose: Reduce rework cycles and keep schedule stable.)*

            **Alternative Design Options:**
            *   Offer two design variants: one standard (cost-effective), one premium.
            *(Purpose: Let client choose based on budget and risk tolerance.)*

            **Parallel Task Planning:**
            *   Reorganize phases to run concurrently (e.g., technical detailing while approvals pending).
            *(Purpose: Reduce total project time and resource idle time.)*

            **Phase Splitting:**
            *   Break large project into smaller contracts (e.g., planning → execution as separate projects).
            *(Purpose: Reduce commitment; evaluate feasibility step-by-step.)*
            """)
    elif final_risk == "undefined_risk_profile":
        st.error(
            "The project parameters did not match a defined risk profile. Please review inputs or check the Prolog rules.")
    else:  # error_in_assessment or other unexpected value
        st.error("An error occurred during the risk assessment. Please check the application logs or contact support.")
else:
    st.info("Please input all project parameters in the sidebar and click 'Assess Project Risk'.")

st.markdown("---")
st.caption("C2M Project Risk Assessment Tool | Version 1.0 | Based on specifications dated 02.06.2025")