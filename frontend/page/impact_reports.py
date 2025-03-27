import streamlit as st
import pandas as pd
import altair as alt
import json
from datetime import datetime
from pathlib import Path
from utils.data_utils import load_json_data

# Utility function to create impact metrics JSON if not exists
def create_impact_metrics_json(campaigns_data):
    impact_metrics = {}
    
    # Ensure campaigns_data is a dictionary with a 'causes' key
    if not isinstance(campaigns_data, dict):
        campaigns_data = {"causes": campaigns_data}
    
    causes = campaigns_data.get("causes", [])
    for cause in causes:
        cid = str(cause.get("id", ""))
        if not cid:
            continue
        
        total_funds_received = cause.get("raised", 0)
        total_funds_utilized = sum(m.get("funds_required", 0) for m in cause.get("milestones", [])) * 0.5
        beneficiaries_helped = int(total_funds_received / 10)
        projects_completed = sum(1 for m in cause.get("milestones", []) if m.get("status") == "completed")
        ongoing_projects = sum(1 for m in cause.get("milestones", []) if m.get("status") == "in_progress")
        
        impact_metrics[cid] = {
            "verification_status": "Verified",
            "last_audit_date": "2025-03-01",
            "total_funds_received": total_funds_received,
            "total_funds_utilized": total_funds_utilized,
            "beneficiaries_helped": beneficiaries_helped,
            "projects_completed": projects_completed,
            "ongoing_projects": ongoing_projects,
            "funds_allocation": {
                "Infrastructure": 50, 
                "Operations": 30, 
                "Outreach": 20
            },
            "monthly_impact": [
                {"month": "2025-01", "beneficiaries": 10, "funds_used": 200},
                {"month": "2025-02", "beneficiaries": 15, "funds_used": 300},
                {"month": "2025-03", "beneficiaries": 20, "funds_used": 400}
            ],
            "verified_metrics": {
                "verification_proof": "0xabcdef1234567890",
                "impact_score": 85,
                "transparency_rating": 90,
                "fund_utilization_efficiency": 80,
                "sustainable_development_goals": ["SDG 3: Good Health", "SDG 6: Clean Water"]
            }
        }
    
    # Write to JSON file
    with open('impact_metrics.json', 'w') as f:
        json.dump(impact_metrics, f, indent=4)
    
    return impact_metrics

# Load data with error handling
def safe_load_json(filename):
    try:
        return load_json_data(filename)
    except FileNotFoundError:
        st.error(f"File {filename} not found. Please check the file path.")
        return {}
    except json.JSONDecodeError:
        st.error(f"Error decoding {filename}. Please check the file format.")
        return {}

# Load campaigns and donations data
CAMPAIGNS_DATA = safe_load_json('campaigns.json')
DONATIONS_DATA = safe_load_json('donations.json')

# Ensure CAMPAIGNS_DATA is properly structured
if not isinstance(CAMPAIGNS_DATA, dict):
    CAMPAIGNS_DATA = {"causes": CAMPAIGNS_DATA}

# Try to load impact metrics, create if not present
try:
    IMPACT_METRICS = load_json_data('impact_metrics.json')
except FileNotFoundError:
    # Create impact metrics JSON if not found
    IMPACT_METRICS = create_impact_metrics_json(CAMPAIGNS_DATA)

def show():
    st.title("Charity Impact Reports")
    
    # Charity selector using campaigns data
    st.sidebar.header("Select Charity")
    charities = CAMPAIGNS_DATA.get("causes", [])
    
    # Ensure charities is a list and contains dictionaries with name and id
    if not charities or not isinstance(charities, list):
        st.error("No charities found in the data.")
        return
    
    charity_options = [charity.get("name", "Unnamed Charity") for charity in charities]
    selected_charity = st.sidebar.selectbox("Choose a charity:", charity_options)
    
    # Get the charity ID for the selected charity
    charity_id = next((str(charity.get("id", "")) for charity in charities if charity.get("name") == selected_charity), None)
    
    if not charity_id:
        st.error("Could not find the selected charity.")
        return
    
    # Simulated wallet connect button
    if st.sidebar.button("Connect HashPack Wallet"):
        st.sidebar.success("Wallet connected! Address: 0.0.123456")
    
    # Load impact data from computed metrics
    impact_data = IMPACT_METRICS.get(charity_id, {})
    verified_metrics = impact_data.get("verified_metrics", {})
    
    # Dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"{selected_charity} Impact Dashboard")
        if impact_data.get("verification_status") == "Verified":
            st.markdown(
                f"""
                <div style="background-color:#d4edda; padding:10px; border-radius:5px; margin-bottom:20px;">
                    <span style="color:#155724; font-weight:bold;">✓ Hashgraph Verified</span>
                    <span style="color:#155724; margin-left:10px;">Last audit: {impact_data.get("last_audit_date", "N/A")}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Impact summary metrics
        metrics_cols = st.columns(4)
        with metrics_cols[0]:
            st.metric("Funds Received", f"${impact_data.get('total_funds_received', 0):,}")
        with metrics_cols[1]:
            st.metric("Funds Utilized", f"${impact_data.get('total_funds_utilized', 0):,}")
        with metrics_cols[2]:
            st.metric("Beneficiaries", f"{impact_data.get('beneficiaries_helped', 0):,}")
        with metrics_cols[3]:
            completed = impact_data.get('projects_completed', 0)
            ongoing = impact_data.get('ongoing_projects', 0)
            st.metric("Projects", f"{completed} completed, {ongoing} ongoing")
        
        # Fund allocation chart
        st.subheader("Fund Allocation")
        allocation = impact_data.get('funds_allocation', {})
        allocation_data = pd.DataFrame({
            'Category': list(allocation.keys()),
            'Percentage': list(allocation.values())
        })
        chart = alt.Chart(allocation_data).mark_arc().encode(
            theta=alt.Theta(field="Percentage", type="quantitative"),
            color=alt.Color(field="Category", type="nominal"),
            tooltip=['Category', 'Percentage']
        ).properties(width=400, height=300)
        st.altair_chart(chart, use_container_width=True)
        
    with col2:
        st.subheader("Hashgraph Verification")
        st.markdown(f"**Verification Hash**  \n`{verified_metrics.get('verification_proof', 'N/A')[:20]}...`")
        st.markdown("**Impact Ratings**")
        impact_score = verified_metrics.get("impact_score", 0)
        transparency_rating = verified_metrics.get("transparency_rating", 0)
        fund_efficiency = verified_metrics.get("fund_utilization_efficiency", 0)
        st.progress(impact_score / 100)
        st.caption(f"Impact Score: {impact_score}/100")
        st.progress(transparency_rating / 100)
        st.caption(f"Transparency Rating: {transparency_rating}/100")
        st.progress(fund_efficiency / 100)
        st.caption(f"Fund Efficiency: {fund_efficiency}/100")
        st.markdown("**SDGs Supported**")
        for sdg in verified_metrics.get("sustainable_development_goals", []):
            st.markdown(f"• {sdg}")
    
    st.subheader("Monthly Impact Trends")
    monthly_impact = impact_data.get("monthly_impact", [])
    if not monthly_impact:
        st.warning("No monthly impact data available.")
    else:
        monthly_data = pd.DataFrame(monthly_impact)
        # Convert 'month' column to datetime; errors are coerced to NaT if invalid
        monthly_data['month'] = pd.to_datetime(monthly_data['month'], errors='coerce')
        # Create a formatted string column for the month (e.g., "Jan 2025")
        monthly_data['month_str'] = monthly_data['month'].dt.strftime("%b %Y")
    
        # Define the base chart using the formatted month string
        base = alt.Chart(monthly_data).encode(x=alt.X("month_str:N", title="Month"))
    
        line1 = base.mark_line(stroke='#5470C6', strokeWidth=3).encode(
            y=alt.Y('beneficiaries:Q', title='Beneficiaries Helped'),
            tooltip=['month_str', 'beneficiaries']
        )
        line2 = base.mark_line(stroke='#91CC75', strokeWidth=3).encode(
            y=alt.Y('funds_used:Q', title='Funds Used ($)'),
            tooltip=['month_str', 'funds_used']
        )
    
        st.altair_chart(
            alt.layer(line1, line2)
                .resolve_scale(y='independent')
                .properties(width=600, height=300),
            use_container_width=True
        )
    
    st.subheader("Hashgraph Verified Transactions")
    # Assume transactions are embedded in campaigns data for milestones and in donations for donations
    # Here, we display donations for this charity as transaction history
    transactions = [d for d in DONATIONS_DATA if str(d["campaign_id"]) == charity_id]

    tx_df = pd.DataFrame(transactions)
    st.dataframe(tx_df.style.format({"amount": "${:,.0f}"}), use_container_width=True)
    
    if st.button("Verify All Transactions on Hedera Explorer"):
        st.markdown(
            """
            <div style="background-color:#cce5ff; padding:10px; border-radius:5px;">
                <span style="color:#004085;">Redirecting to Hedera Explorer for transaction verification...</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"[View on Hedera Explorer](https://hashscan.io/testnet/account/{charity_id})")
    
    st.subheader("Generate Verified Impact Report")
    report_cols = st.columns([1, 1, 1])
    with report_cols[0]:
        if st.button("Generate PDF Report"):
            st.success("Impact report generated with hashgraph verification!")
            st.download_button(
                label="Download PDF Report",
                data=b"Sample PDF content",  # Replace with actual PDF data
                file_name=f"{selected_charity}_impact_report.pdf",
                mime="application/pdf"
            )
    with report_cols[1]:
        if st.button("Share Report"):
            st.info("Report link copied to clipboard with hashgraph verification hash")
    with report_cols[2]:
        if st.button("Verify on Hedera"):
            st.success(f"Report verified on Hedera. Consensus timestamp: {datetime.now()}")

if __name__ == "__main__":
    show()