import streamlit as st
import pandas as pd
import altair as alt
import datetime
import utils.state_management as state
from utils.data_utils import load_json_data, load_local_image

# Load campaigns and donations
MOCK_CAMPAIGNS = load_json_data('campaigns.json')
MOCK_DONATIONS = load_json_data('donations.json')

def show():
    # Check if user is logged in and is a charity
    if not state.is_logged_in() or state.get_user_type() != "charity":
        st.warning("Please log in with a charity account to access this page.")
        return
    
    # Display charity management dashboard
    st.title("Charity Management Dashboard")
    
    # Get current charity info
    charity = state.get_user_info()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics from mock data
    total_raised = sum(campaign["raised"] for campaign in MOCK_CAMPAIGNS)
    active_campaigns = sum(1 for campaign in MOCK_CAMPAIGNS if campaign["status"] == "active")
    total_donors = len(set(donation["donor"] for donation in MOCK_DONATIONS))
    avg_donation = sum(donation["amount"] for donation in MOCK_DONATIONS) / len(MOCK_DONATIONS)
    
    with col1:
        st.metric("Total Raised", f"${total_raised:,}")
    with col2:
        st.metric("Active Campaigns", active_campaigns)
    with col3:
        st.metric("Total Donors", total_donors)
    with col4:
        st.metric("Avg. Donation", f"${avg_donation:.2f}")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Campaigns", "Donations", "Milestone Proofs", "New Campaign"])
    
    with tab1:
        st.subheader("Campaign Management")
        
        # Convert campaigns to DataFrame for easier display
        df_campaigns = pd.DataFrame(MOCK_CAMPAIGNS)
        
        # Progress bars for active campaigns
        active_df = df_campaigns[df_campaigns['status'] == 'active']
        if not active_df.empty:
            st.subheader("Active Campaign Progress")
            for _, campaign in active_df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    progress = campaign['raised'] / campaign['goal']
                    st.progress(progress)
                with col2:
                    st.write(f"{campaign['name']}: ${campaign['raised']:,} / ${campaign['goal']:,}")
        
        # Campaign details and actions
        st.subheader("All Campaigns")
        for campaign in MOCK_CAMPAIGNS:
            with st.expander(f"{campaign['name']} - {campaign['status'].title()}"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(load_local_image(campaign['image']), width=200)

                with col2:
                    st.write(f"**Goal:** ${campaign['goal']:,}")
                    st.write(f"**Raised:** ${campaign['raised']:,}")
                    st.write(f"**Period:** {campaign['start_date']} to {campaign['end_date']}")
                    st.write(f"**Beneficiaries:** {campaign.get('beneficiaries', 0):,}")
                    st.write(f"**Category:** {campaign['category']}")
                
                st.write(f"**Description:** {campaign['description']}")
                
                # Milestones
                st.subheader("Milestones")
                for milestone in campaign['milestones']:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{milestone['name']}**")
                    with col2:
                        st.write(f"${milestone['funds_required']:,}")
                    with col3:
                        st.write(f"Status: {milestone['status'].replace('_', ' ').title()}")
                    
                    if milestone['status'] == 'in_progress':
                        for i, milestone in enumerate(campaign.get("milestones", [])):
                            if st.button(f"Submit Proof for {milestone['name']}", key=f"proof_{campaign['id']}_{i}"):
                                # Simulate Hedera integration - would open a file uploader in a real app
                                st.session_state['show_proof_upload'] = True
                                st.session_state['current_milestone'] = (campaign['id'], milestone['id'])
                
                # Edit campaign button
                if st.button("Edit Campaign", key=f"edit_{campaign['id']}"):
                    st.session_state['edit_campaign'] = campaign['id']
    
    with tab2:
        st.subheader("Donation History")
        
        # Filter donations by date
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", datetime.datetime.now() - datetime.timedelta(days=30))
        with col2:
            end_date = st.date_input("To", datetime.datetime.now())
        
        # Convert to DataFrame for filtering and display
        df_donations = pd.DataFrame(MOCK_DONATIONS)
        df_donations['date'] = pd.to_datetime(df_donations['date'])
        filtered_donations = df_donations[(df_donations['date'] >= pd.Timestamp(start_date)) & 
                                         (df_donations['date'] <= pd.Timestamp(end_date))]
        
        # Join with campaign names
        campaign_names = {campaign['id']: campaign['name'] for campaign in MOCK_CAMPAIGNS}
        filtered_donations['campaign_name'] = filtered_donations['campaign_id'].map(campaign_names)
        
        # Display filtered donations
        if not filtered_donations.empty:
            # Donation metrics
            total_filtered = filtered_donations['amount'].sum()
            avg_filtered = filtered_donations['amount'].mean()
            count_filtered = len(filtered_donations)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Donations", f"${total_filtered:,}")
            with col2:
                st.metric("Average Amount", f"${avg_filtered:.2f}")
            with col3:
                st.metric("Number of Donations", count_filtered)
            
            # Display table
            st.dataframe(filtered_donations[['date', 'donor', 'amount', 'campaign_name', 'transaction_id']])
            
            # Create chart
            chart_data = filtered_donations.groupby('campaign_name')['amount'].sum().reset_index()
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('campaign_name:N', title='Campaign'),
                y=alt.Y('amount:Q', title='Amount ($)'),
                color='campaign_name:N'
            ).properties(
                title='Donations by Campaign'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No donations found for the selected date range.")
    
    with tab3:
        st.subheader("Milestone Proof Submission")
        
        # Display milestones that need proof
        proofs_needed = []
        for campaign in MOCK_CAMPAIGNS:
            for milestone in campaign['milestones']:
                if milestone['status'] == 'in_progress' and milestone['proof'] is None:
                    proofs_needed.append({
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'milestone_id': milestone['id'],
                        'milestone_name': milestone['name'],
                        'funds_required': milestone['funds_required']
                    })
        
        if proofs_needed:
            st.write("The following milestones require proof of completion:")
            for proof in proofs_needed:
                with st.expander(f"{proof['campaign_name']} - {proof['milestone_name']}"):
                    st.write(f"**Funds Required:** ${proof['funds_required']:,}")
                    
                    # Proof upload form
                    with st.form(key=f"proof_form_{proof['campaign_id']}_{proof['milestone_id']}"):
                        st.write("Upload proof of milestone completion")
                        file_upload = st.file_uploader("Upload documentation", type=["pdf", "png", "jpg"])
                        description = st.text_area("Description of completion")
                        
                        # Hedera integration for proof submission
                        submit_proof = st.form_submit_button("Submit Proof to Hedera")
                        if submit_proof and file_upload is not None:
                            # This would interact with Hedera in a real app
                            st.success(f"Proof submitted to Hedera for milestone {proof['milestone_name']}!")
                            
                            # Simulate Hedera transaction ID
                            transaction_id = f"0.0.{1000000 + proof['campaign_id']*1000 + proof['milestone_id']}"
                            st.code(f"Transaction ID: {transaction_id}")
        else:
            st.info("No milestones currently require proof submission.")
        
        # Display previously submitted proofs
        st.subheader("Previously Submitted Proofs")
        proofs_submitted = []
        for campaign in MOCK_CAMPAIGNS:
            for milestone in campaign['milestones']:
                if milestone['status'] == 'completed' and milestone['proof'] is not None:
                    proofs_submitted.append({
                        'campaign_name': campaign['name'],
                        'milestone_name': milestone['name'],
                        'proof': milestone['proof'],
                        'release_date': milestone.get('release_date', 'N/A')
                    })
        
        if proofs_submitted:
            proof_df = pd.DataFrame(proofs_submitted)
            st.dataframe(proof_df)
        else:
            st.info("No proofs have been submitted yet.")
    
    with tab4:
        st.subheader("Create New Campaign")
        
        # Campaign creation form
        with st.form("new_campaign_form"):
            campaign_name = st.text_input("Campaign Name")
            description = st.text_area("Description")
            goal = st.number_input("Fundraising Goal ($)", min_value=1000, step=1000)
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
            
            category = st.selectbox("Category", ["Education", "Healthcare", "Environment", "Disaster Relief", "Poverty", "Other"])
            beneficiaries = st.number_input("Estimated Beneficiaries", min_value=1, step=100)
            
            # Milestone creation
            st.subheader("Milestones")
            milestone_count = st.number_input("Number of Milestones", min_value=1, max_value=5, value=3)
            
            milestones = []
            for i in range(int(milestone_count)):
                with st.expander(f"Milestone {i+1}", expanded=True):
                    m_name = st.text_input(f"Milestone {i+1} Name", key=f"m_name_{i}")
                    m_funds = st.number_input(f"Funds Required", min_value=100, step=1000, key=f"m_funds_{i}")
                    milestones.append({"name": m_name, "funds_required": m_funds})
            
            # Would include Hedera account setup in a real app
            st.subheader("Hedera Account")
            hedera_id = st.text_input("Hedera Account ID", placeholder="0.0.XXXXX")
            
            # Submit campaign button
            submit_campaign = st.form_submit_button("Create Campaign")
            if submit_campaign:
                # Validate inputs
                if not campaign_name or not description:
                    st.error("Please fill out all required fields.")
                elif end_date <= start_date:
                    st.error("End date must be after start date.")
                elif sum(m["funds_required"] for m in milestones) != goal:
                    st.error("The sum of milestone funds must equal the campaign goal.")
                else:
                    # Create a mock account if needed
                    if not hedera_id:
                        account = create_mock_account()
                        hedera_id = account["accountId"]
        
                        # Generate a mock transaction ID
                        transaction_id = f"0.0.{2000000 + len(MOCK_CAMPAIGNS) + 1}"
        
                        # This would create the campaign in a real app
                        st.success(f"Campaign '{campaign_name}' created successfully!")
                        st.code(f"Campaign created with mock transaction ID: {transaction_id}")
        
                        # Show how it would be stored
                        mock_campaign_data = {
                            "id": len(MOCK_CAMPAIGNS) + 1,
                            "name": campaign_name,
                            "description": description,
                            "goal": goal,
                            "raised": 0,
                            "start_date": start_date.strftime("%Y-%m-%d"),
                            "end_date": end_date.strftime("%Y-%m-%d"),
                            "status": "active",
                            "image": "https://placekitten.com/404/225",
                            "milestones": [
                                {
                                    "id": i+1,
                                    "name": m["name"],
                                    "funds_required": m["funds_required"],
                                    "status": "pending",
                                    "proof": None,
                                    "release_date": None
                                } for i, m in enumerate(milestones)
                            ],
                            "transaction_id": transaction_id,
                            "beneficiaries": beneficiaries,
                            "category": category
                        }
                    
                    st.json(mock_campaign_data)

# Function to process donations using mock data instead of Hedera
def process_hedera_donation(donor_name, charity_name, amount, campaign_id):
    """
    Process a donation using mock data instead of Hedera
    """
    # Generate a mock transaction ID
    transaction_id = f"0.0.{9000000 + int(campaign_id)*1000 + len(MOCK_DONATIONS) + 1}"
    
    # In a real app, we would add this to a database
    # For now, just return the transaction ID
    return {
        "success": True,
        "transaction_id": transaction_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "amount": amount,
        "donor": donor_name,
        "campaign_id": campaign_id
    }

# Function to verify a transaction using mock data
def verify_hedera_transaction(transaction_id):
    """
    Verify a transaction using mock data instead of Hedera
    """
    # Check if transaction exists in mock donations
    # In a real app, we would check against the blockchain
    transaction_exists = any(d["transaction_id"] == transaction_id for d in MOCK_DONATIONS)
    
    # Parse the campaign ID from the transaction ID (just for mock data)
    try:
        campaign_id = int(transaction_id.split('.')[-1][0])
    except:
        campaign_id = 1
        
    return {
        "isValid": transaction_exists or transaction_id.startswith("0.0."),
        "memo": f"Donation to campaign {campaign_id}",
        "timestamp": datetime.datetime.now().isoformat()
    }

# Helper function to create a new Hedera account (would be used during signup)
def create_hedera_account():
    """
    Create a mock account instead of a Hedera account
    """
    # Generate a mock account ID
    account_id = f"0.0.{3000000 + int(datetime.datetime.now().timestamp() % 1000000)}"
    
    return {
        "accountId": account_id,
        "privateKey": "mock-private-key-xxxxxxxxxxxxx",
        "publicKey": "mock-public-key-xxxxxxxxxxxxx"
    }

if __name__ == "__main__":
    show()