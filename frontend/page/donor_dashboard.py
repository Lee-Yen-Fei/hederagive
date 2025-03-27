import streamlit as st
import pandas as pd
import altair as alt
import utils.state_management as state
import datetime
import emoji
from utils.data_utils import load_json_data, load_local_image

MOCK_CAMPAIGNS = load_json_data('campaigns.json')
MOCK_DONATIONS = load_json_data('donations.json')
MOCK_SUPPORTERS = load_json_data('supporters.json')

def process_donation(donor_account, campaign_account, amount, campaign_id):
    """Process donation (mock function that would call backend API)"""
    # This would call the backend API that handles Hedera transactions
    # For now, just generate a mock transaction ID
    import uuid
    transaction_id = f"0.0.{uuid.uuid4().hex[:8]}"
    
    # In a real app, you would update the database through an API call
    # Here we'll simulate by updating the JSON file directly
    update_campaign_data(campaign_id, amount)
    record_donation(donor_account, amount, campaign_id, transaction_id)
    
    return transaction_id


def update_campaign_data(campaign_id, amount):
    """Update campaign data with new donation amount"""
    campaign_file = "data/campaigns.json"
    
    # Load current data
    with open(campaign_file, 'r') as f:
        campaigns = json.load(f)
    
    # Find and update the campaign
    for campaign in campaigns:
        if campaign["id"] == campaign_id:
            campaign["raised"] += amount
            break
    
    # Save updated data
    with open(campaign_file, 'w') as f:
        json.dump(campaigns, f, indent=2)

def record_donation(donor_name, amount, campaign_id, transaction_id):
    """Record a new donation"""
    donations_file = "data/donations.json"
    
    # Load current donations
    with open(donations_file, 'r') as f:
        donations = json.load(f)
    
    # Create new donation record
    new_donation = {
        "id": len(donations) + 1,
        "donor": donor_name,
        "amount": amount,
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "campaign_id": campaign_id,
        "transaction_id": transaction_id
    }
    
    # Add to donations and save
    donations.append(new_donation)
    
    with open(donations_file, 'w') as f:
        json.dump(donations, f, indent=2)
    
    return new_donation

def verify_transaction(transaction_id):
    """Verify transaction (mock function that would call backend API)"""
    # This would call a backend API that verifies Hedera transactions
    # For now, just return mock data
    if transaction_id and len(transaction_id) > 10:
        return {
            "verified": True,
            "details": {
                "transaction_id": transaction_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "SUCCESS",
                "from": "0.0.12345678",
                "to": "0.0.87654321",
                "amount": "$25.00",
                "fee": "0.0001 HBAR"
            }
        }
    else:
        return {
            "verified": False,
            "error": "Invalid transaction ID format"
        }


def show_leaderboard():
    st.header("Donor Leaderboard")
    
    # Use the already-loaded MOCK_SUPPORTERS from your global variable
    supporters = MOCK_SUPPORTERS.get("supporters", [])
    
    if not supporters:
        st.info("No supporters found.")
        return

    # Sorting option
    sort_option = st.selectbox("Sort by", ["Total Donated", "Donations Count"], index=0)
    if sort_option == "Total Donated":
        supporters = sorted(supporters, key=lambda s: s.get("total_donated", 0), reverse=True)
    else:
        supporters = sorted(supporters, key=lambda s: s.get("donations_count", 0), reverse=True)
    
    # Build records with separate columns for badge emojis and names
    records = []
    for supporter in supporters:
        badges = supporter.get("badges", [])
        # Use emoji.emojize to ensure proper rendering (assuming badge["emoji"] is stored as a literal string)
        badge_emojis = ", ".join(emoji.emojize(badge.get("emoji", ""), language="alias") for badge in badges) if badges else ""
        badge_names = ", ".join(badge.get("name", "") for badge in badges) if badges else ""
        record = {
            "Donor": supporter.get("donor", "N/A"),
            "Total Donated": supporter.get("total_donated", 0),
            "Donations Count": supporter.get("donations_count", 0),
            "Badge Emojis": badge_emojis,
            "Badge Names": badge_names
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    st.dataframe(df)

def show():
    # Check if user is logged in as a donor
    if not state.is_logged_in() or state.get_user_type() != "donor":
        st.warning("Please log in with a donor account to access this page.")
        return
    
    # Get current user info
    donor = state.get_user_info()
    
    st.title("Donate to Charity Campaigns")
    
    # Display active campaigns
    active_campaigns = [c for c in MOCK_CAMPAIGNS if c["status"] == "active"]
    
    # Filter options
    st.sidebar.header("Filter Campaigns")
    categories = ["All"] + list(set(c["category"] for c in MOCK_CAMPAIGNS))
    selected_category = st.sidebar.selectbox("Category", categories)
    
    min_goal, max_goal = min(c["goal"] for c in MOCK_CAMPAIGNS), max(c["goal"] for c in MOCK_CAMPAIGNS)
    goal_range = st.sidebar.slider("Goal Range", min_goal, max_goal, (min_goal, max_goal))
    
    # Apply filters
    filtered_campaigns = active_campaigns
    if selected_category != "All":
        filtered_campaigns = [c for c in filtered_campaigns if c["category"] == selected_category]
    
    filtered_campaigns = [c for c in filtered_campaigns if goal_range[0] <= c["goal"] <= goal_range[1]]
    
    # Display campaigns
    if not filtered_campaigns:
        st.info("No campaigns match your filters. Please adjust your criteria.")
    else:
        st.write(f"Showing {len(filtered_campaigns)} campaigns")
        
        # Campaigns cards
        for campaign in filtered_campaigns:
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(load_local_image(campaign['image']), width=200)
                
                with col2:
                    st.subheader(campaign["name"])
                    st.write(f"**Category:** {campaign['category']}")
                    st.write(f"**Goal:** :green[${campaign['raised']:,}] / ${campaign['goal']:,}")
                    
                    # Progress bar
                    progress = campaign['raised'] / campaign['goal']
                    st.progress(progress)
                    
                    # Calculate days left
                    end_date = datetime.datetime.strptime(campaign['end_date'], "%Y-%m-%d")
                    days_left = (end_date - datetime.datetime.now()).days
                    st.write(f":red[**{days_left} days left**] (Ends {campaign['end_date']})")
                
                st.write(campaign["description"])
                
                # Donation form
                with st.expander("Donate to this campaign"):
                    with st.form(key=f"donate_form_{campaign['id']}"):
                        donation_amount = st.number_input("Donation Amount ($)", min_value=5, step=5)
                        anonymous = st.checkbox("Donate Anonymously")
                        
                        # Show donor info
                        st.write(f"Donating as: {'' if anonymous else donor.get('name', 'User')}")
                        
                        submitted = st.form_submit_button(":orange[Complete Donation]")
                        if submitted:
                            # Process donation through backend API
                            donor_name = "Anonymous" if anonymous else donor.get('name', 'User')
                            
                            # Call function to process the donation
                            transaction_id = process_donation(
                                donor_account=donor_name,
                                campaign_account=campaign.get('id'),
                                amount=donation_amount,
                                campaign_id=campaign['id']
                            )
                            
                            # Show success message
                            st.success(f"Thank you for your donation of ${donation_amount}!")
                            st.code(f"Transaction ID: {transaction_id}")
                
                # Show milestones
                with st.expander("View Campaign Milestones"):
                    for milestone in campaign['milestones']:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{milestone['name']}**")
                        with col2:
                            st.write(f"${milestone['funds_required']:,}")
                        with col3:
                            status_color = "green" if milestone['status'] == "completed" else "orange" if milestone['status'] == "in_progress" else "gray"
                            st.markdown(f"<span style='color:{status_color}'>{milestone['status'].replace('_', ' ').title()}</span>", unsafe_allow_html=True)
                        
                        # Show proof if available
                        if milestone['proof']:
                            st.write(f"Proof of completion: [{milestone['proof']}](https://example.com/verification/{milestone['proof']})")
                
                st.markdown("---")
    
    # User's donation history
    st.header("Your Donation History")
    
    # Filter donations for this user
    user_donations = [d for d in MOCK_DONATIONS if d["donor"] == donor.get('name', 'User') or 
                     (d["donor"] == "Anonymous" and donor.get('donor_id') == donor.get('id'))]
    
    if user_donations:
        # Calculate total donation amount
        total_donated = sum(d["amount"] for d in user_donations)
        st.write(f"Total amount donated: **${total_donated:,.2f}**")
        
        # Display donation history
        donations_df = pd.DataFrame(user_donations)
        
        # Add campaign name to donations
        campaign_names = {c["id"]: c["name"] for c in MOCK_CAMPAIGNS}
        donations_df["campaign"] = donations_df["campaign_id"].map(campaign_names)
        
        # Format the table
        st.dataframe(
            donations_df[["date", "campaign", "amount", "transaction_id"]].rename(
                columns={
                    "date": "Date",
                    "campaign": "Campaign",
                    "amount": "Amount ($)",
                    "transaction_id": "Transaction ID"
                }
            ).sort_values("Date", ascending=False)
        )
        
        # Visualization
        st.subheader("Your Donation Trends")
        
        # Prepare data for chart
        chart_data = donations_df.copy()
        chart_data["date"] = pd.to_datetime(chart_data["date"])
        chart_data["month"] = chart_data["date"].dt.strftime("%Y-%m")
        
        # Group by month for time series
        monthly_donations = chart_data.groupby("month")["amount"].sum().reset_index()
        
        # Create time series chart
        time_chart = alt.Chart(monthly_donations).mark_line(point=True).encode(
            x=alt.X("month:T", title="Month"),
            y=alt.Y("amount:Q", title="Total Donations ($)"),
            tooltip=["month", "amount"]
        ).properties(
            title="Monthly Donation Amounts",
            width=600,
            height=300
        )
        
        # Create campaign breakdown chart
        campaign_totals = chart_data.groupby("campaign")["amount"].sum().reset_index()
        
        campaign_chart = alt.Chart(campaign_totals).mark_bar().encode(
            x=alt.X("campaign:N", title="campaign", sort="-y"),
            y=alt.Y("amount:Q", title="Total Donations ($)"),
            color="campaign:N",
            tooltip=["campaign", "amount"]
        ).properties(
            title="Donations by Campaign",
            width=600,
            height=300
        )
        
        st.altair_chart(time_chart)
        st.altair_chart(campaign_chart)
    else:
        st.info("You haven't made any donations yet. Support a campaign above to get started!")
    
    # Verify transactions
    st.header("Verify a Transaction")
    with st.expander("Transaction Verification Tool"):
        transaction_id = st.text_input("Enter Transaction ID to verify")
        if st.button(":orange[Verify Transaction]"):
            if transaction_id:
                # Call verification function
                result = verify_transaction(transaction_id)
                
                if result["verified"]:
                    st.success("Transaction Verified!")
                    st.json(result["details"])
                else:
                    st.error("Unable to verify transaction")
                    st.write(result["error"])
            else:
                st.warning("Please enter a valid transaction ID")

    with st.expander("Show Leaderboard"):
        show_leaderboard()

if __name__ == "__main__":
    show()