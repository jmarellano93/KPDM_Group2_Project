import streamlit as st
from utils.prolog_interface import assess_risk

st.title("Project Risk Assessment Tool")

with st.form("risk_form"):
    margin = st.number_input("Expected Margin (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    proj_type = st.selectbox("Project Type", ["Execution Only", "Planning Only", "Execution & Planning"])
    sia_level = st.slider("SIA Complexity Level", 1, 5, 3)
    contract = st.radio("Contract Type", ["Fixed Price", "Hourly"])
    rel = st.radio("Historical Client Relationship", ["New", "Established"])
    client = st.radio("Client Type", ["Private", "Government"])

    with st.expander("Adjust Attribute Weights"):
        w_margin = st.number_input("Weight: Margin", value=0.30)
        w_proj   = st.number_input("Weight: Project Type", value=0.20)
        w_sia    = st.number_input("Weight: SIA Level", value=0.15)
        w_con    = st.number_input("Weight: Contract Type", value=0.15)
        w_rel    = st.number_input("Weight: Client Relationship", value=0.10)
        w_cli    = st.number_input("Weight: Client Type", value=0.10)

    submitted = st.form_submit_button("Evaluate Risk")

if submitted:
    total_weight = sum([w_margin, w_proj, w_sia, w_con, w_rel, w_cli])
    if abs(total_weight - 1.0) > 1e-6:
        st.error(f"Weights must sum to 1.0 (Current: {total_weight:.2f})")
    else:
        pt_map = {
            "Execution Only": "execution_only",
            "Planning Only": "planning_only",
            "Execution & Planning": "planning_and_execution"
        }
        contract_map = {"Fixed Price": "fixed_price", "Hourly": "hourly"}
        rel_map = {"New": "new", "Established": "established"}
        client_map = {"Private": "private", "Government": "government"}

        risk, suggestions = assess_risk(
            margin,
            pt_map[proj_type],
            sia_level,
            contract_map[contract],
            rel_map[rel],
            client_map[client]
        )

        if risk == "high":
            st.error("High Risk")
        elif risk == "medium":
            st.warning("Medium Risk")
        else:
            st.success("Low Risk")

        if suggestions:
            st.subheader("Mitigation Suggestions")
            for item in suggestions:
                st.write("-", item)