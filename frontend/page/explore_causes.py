import streamlit as st
import pandas as pd
import altair as alt
import utils.state_management as state
from utils.data_utils import load_json_data, load_local_image

# Load campaigns and donations
MOCK_CAMPAIGNS = load_json_data('campaigns.json')
MOCK_DONATIONS = load_json_data('donations.json')
MOCK_SUPPORTERS = load_json_data('supporters.json')

def show_cause_card(cause):
    """Render a single cause card with standardized layout"""
    st.image(load_local_image(cause['image']), use_container_width=True)
    st.markdown(f"### {cause['name']}")
    st.markdown(f"**{cause['category']}** | {cause['name']}")
    
    # Truncated description
    short_desc = cause["description"][:100] + "..." if len(cause["description"]) > 100 else cause["description"]
    st.markdown(short_desc)
    
    # Progress bar
    progress = cause["raised"] / cause["goal"]
    st.progress(progress)
    st.markdown(f":green[${cause['raised']:,}] / ${cause['goal']:,}")
    
    # Action buttons
    if st.button("Donate", key=f"donate_{cause['id']}", use_container_width=True):
        st.session_state["selected_cause"] = cause
        show_donation_modal()
    
    if st.button("Details", key=f"details_{cause['id']}", use_container_width=True):
        st.session_state["selected_cause"] = cause
        show_details_modal()

def show_featured_cause(featured):
    st.subheader("Featured Cause")
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.image(load_local_image(featured['image']), use_container_width=True)
    
    with col2:
        st.markdown(f"## {featured['name']}")
        st.markdown(f"**{featured['name']}** | {featured['location']}")
        st.markdown(featured["description"])
        
        # Progress bar
        progress = featured["raised"] / featured["goal"]
        st.progress(progress)
        st.markdown(f":red[**${featured['raised']:,}**] / **${featured['goal']:,}** goal")
        
        # Metrics
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("Supporters", featured["supporters"])
        with metrics_col2:
            days_left = 30  # Mock data
            st.metric("Days Left", days_left)
        with metrics_col3:
            st.metric("% Complete", f"{progress*100:.1f}%")
        
        # Action buttons
        if st.button("Donate Now", key="featured_donate", use_container_width=True, type="primary"):
            st.session_state["selected_cause"] = featured
            show_donation_modal()
        
        if st.button("View Details", key="featured_details", use_container_width=True):
            st.session_state["selected_cause"] = featured
            show_details_modal()

def show():
    st.title("Explore Causes")
    
    # Filters sidebar
    st.sidebar.subheader("Filter Causes")
    
    # Get unique categories
    categories = list(set(cause["category"] for cause in MOCK_CAMPAIGNS))
    selected_categories = st.sidebar.multiselect("Categories", categories, default=categories)
    
    # Progress filter
    progress_options = ["All", "Recently Started", "Near Goal", "Urgent Need"]
    selected_progress = st.sidebar.selectbox("Progress Status", progress_options)
    
    # Sort options
    sort_options = ["Most Popular", "Most Recent", "Most Funded", "Least Funded"]
    sort_by = st.sidebar.selectbox("Sort By", sort_options)
    
    # Filter causes based on selection (for demo, we'll just filter by category)
    filtered_causes = [cause for cause in MOCK_CAMPAIGNS if cause["category"] in selected_categories]
    
    # Search
    search_text = st.text_input("Search Causes", placeholder="Enter keywords...")
    
    if search_text:
        filtered_causes = [cause for cause in filtered_causes 
                          if search_text.lower() in cause["name"].lower() 
                          or search_text.lower() in cause["description"].lower()]
    
    # Display filtered causes
    if not filtered_causes:
        st.info("No causes match your filters. Try adjusting your criteria.")
    else:
        featured = filtered_causes[0]
        show_featured_cause(featured)

    # Remaining causes in a grid
    st.divider()
    st.subheader("All Causes")
    
    # Create rows of 3 causes each
    remaining_causes = filtered_causes[1:]
    for i in range(0, len(remaining_causes), 3):
        row_causes = remaining_causes[i:i+3]
        
        # Use full-width columns for each cause
        if len(row_causes) == 3:
            col1, col2, col3 = st.columns(3)
            columns = [col1, col2, col3]
        elif len(row_causes) == 2:
            col1, col2 = st.columns(2)
            columns = [col1, col2]
        else:
            columns = [st.columns(1)[0]]
        
        for j, (cause, col) in enumerate(zip(row_causes, columns)):
            with col:
                st.image(load_local_image(cause['image']), use_container_width=True)
                st.markdown(f"### {cause['name']}")
                st.markdown(f"**{cause['category']}** | {cause['name']}")
                
                # Truncated description
                short_desc = cause["description"][:100] + "..." if len(cause["description"]) > 100 else cause["description"]
                st.markdown(short_desc)
                
                # Progress bar
                progress = cause["raised"] / cause["goal"]
                st.progress(progress)
                st.markdown(f":green[${cause['raised']:,}] / ${cause['goal']:,}")
                
                # Donation and details buttons
                if st.button("Donate", key=f"donate_{cause['id']}", use_container_width=True):
                    st.session_state["selected_cause"] = cause
                    show_donation_modal()
                
                if st.button("Details", key=f"details_{cause['id']}", use_container_width=True):
                    st.session_state["selected_cause"] = cause
                    show_details_modal()

def show_donation_modal():
    """Display donation modal for the selected cause"""
    cause = st.session_state["selected_cause"]
    
    with st.expander("Make a Donation", expanded=True):
        st.markdown(f"## Donate to {cause['name']}")
        st.markdown(f"**{cause['name']}** | Transaction ID: {cause['transaction_id']}")
        
        # Donation amount options
        col1, col2 = st.columns(2)
        with col1:
            donation_amount = st.radio(
                "Select Amount",
                ["$10", "$25", "$50", "$100", "Custom"],
                index=2
            )
        
        with col2:
            if donation_amount == "Custom":
                custom_amount = st.number_input("Enter Amount", min_value=1.0, value=75.0, step=5.0)
                amount = custom_amount
            else:
                amount = float(donation_amount.replace("$", ""))
                st.markdown(f"""
                #### ${amount:.2f}
                Your generous donation will help fund:
                - {cause['milestones'][0]['name'] if len(cause['milestones']) > 0 else 'Project goals'}
                """)
        
        # Payment method
        st.markdown("### Select Payment Method")
        
        payment_tabs = st.tabs(["Hedera Wallet", "Credit Card", "PayPal"])
        
        with payment_tabs[0]:
            wallet_id = st.text_input("Wallet ID", value=st.session_state.get("current_user", {}).get("wallet_id", ""))
            wallet_pw = st.text_input("Wallet Key", type="password")
            st.checkbox("Save wallet for future donations")
            
        with payment_tabs[1]:
            cc_number = st.text_input("Card Number", value="4242 **** **** 4242")
            cc_col1, cc_col2 = st.columns(2)
            with cc_col1:
                cc_exp = st.text_input("Expiration Date", value="12/25")
            with cc_col2:
                cc_cvc = st.text_input("CVC", value="***")
                
        with payment_tabs[2]:
            st.text_input("PayPal Email", value=st.session_state.get("current_user", {}).get("email", "user@example.com"))
        
        # Recurring donation option
        st.checkbox("Make this a monthly donation")
        
        # Submit button
        if st.button("Complete Donation", type="primary", use_container_width=True):
            st.success(f"Thank you for your donation of ${amount:.2f} to {cause['name']}!")
            st.balloons()
            
            # Display hashgraph confirmation
            st.markdown("### Hashgraph Transaction Confirmed")
            st.code(f"""
                Transaction ID: 0.0.{12345678 + int(amount)}
                Status: SUCCESS
                Timestamp: {pd.Timestamp.now()}
                Amount: ${amount:.2f}
                Recipient: {cause['name']}
                Network Fee: $0.001
            """)
            
            # Display badge earned
            st.markdown("### Achievement Unlocked! 🏆")
            if amount >= 100:
                badge = "Generous Supporter"
                emoji = "🌟"
            elif amount >= 50:
                badge = "Dedicated Giver"
                emoji = "🎖️"
            else:
                badge = "Compassionate Heart"
                emoji = "💖"
                
            st.markdown(f"## {emoji} {badge}")
            st.markdown("This achievement has been recorded on the hashgraph and added to your profile.")
            
            # Update user stats (in a real app, this would update the database)
            if st.session_state.get("logged_in", False):
                current_total = st.session_state.get("current_user", {}).get("total_donated", 0)
                state.update_user_data("total_donated", current_total + amount)
                
                # Add badge if not already present
                user_badges = st.session_state.get("current_user", {}).get("badges", [])
                badge_exists = any(b["name"] == badge for b in user_badges)
                
                if not badge_exists:
                    state.update_user_data("badges", user_badges + [{"name": badge, "emoji": emoji}])

def show_details_modal():
    """Display details modal for the selected cause"""
    cause = st.session_state["selected_cause"]
    
    with st.expander("Cause Details", expanded=True):
        st.markdown(f"## {cause['name']}")
        
        tabs = st.tabs(["Overview", "Milestones", "Hashgraph Verification", "Supporters"])
        
        with tabs[0]:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(load_local_image(cause['image']), use_container_width=True)
            
            with col2:
                st.markdown(f"**Campaign**: {cause['name']}")
                st.markdown(f"**Location**: {cause['location']}")
                st.markdown(f"**Category**: {cause['category']}")
                st.markdown(f"**Goal**: ${cause['goal']:,}")
                st.markdown(f"**Raised**: :green[${cause['raised']:,}]")
                st.markdown(f"**Supporters**: {cause['supporters']}")
            
            st.markdown("### About This Cause")
            st.markdown(cause["description"])
            st.markdown("""
            ### Expected Impact
            
            This project aims to create lasting change through sustainable solutions that address root causes. By supporting this initiative, you're helping to:
            
            - Create immediate relief for affected communities
            - Build long-term infrastructure for continued support
            - Empower local leadership and self-sufficiency
            - Establish monitoring systems to track and verify results
            """)
        
        with tabs[1]:
            st.markdown("### Project Milestones")
            
            # Create milestone tracker
            for i, milestone in enumerate(cause["milestones"]):
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    if milestone["status"] == "completed":
                        st.markdown("✅")
                    elif milestone["status"] == "in_progress":
                        st.markdown("🔄")
                    else:
                        st.markdown("⏳")
                
                with col2:
                    st.markdown(f"**{milestone['name']}**")
                    st.markdown(f"Funds Required: ${milestone['funds_required']:,}")
                
                with col3:
                    if milestone["status"] == "completed":
                        st.markdown("**Completed**")
                    elif milestone["status"] == "in_progress":
                        st.markdown("**In Progress**")
                    else:
                        st.markdown("**Upcoming**")
                
                # Add a progress bar for in-progress milestones
                if milestone["status"] == "in_progress":
                    # Calculate a mock progress percentage
                    progress_pct = 0.6  # 60% complete (mock data)
                    st.progress(progress_pct)
                    st.markdown(f"{int(progress_pct * 100)}% Complete")
                
                if i < len(cause["milestones"]) - 1:
                    st.markdown("---")
            
            # Timeline visualization
            milestone_data = pd.DataFrame({
                "Milestone": [m["name"] for m in cause["milestones"]],
                "Start": ["2025-01-15", "2025-03-01", "2025-05-15"],
                "End": ["2025-03-01", "2025-05-15", "2025-07-30"],
                "Status": [m["status"] for m in cause["milestones"]]
            })
            
            # Convert dates to datetime
            milestone_data["Start"] = pd.to_datetime(milestone_data["Start"])
            milestone_data["End"] = pd.to_datetime(milestone_data["End"])
            
            # Create a Gantt chart
            chart = alt.Chart(milestone_data).mark_bar().encode(
                x='Start',
                x2='End',
                y='Milestone',
                color=alt.Color('Status', scale=alt.Scale(
                    domain=['completed', 'in_progress', 'pending'],
                    range=['green', 'blue', 'gray']
                ))
            ).properties(
                width=600,
                height=200
            )
            
            st.altair_chart(chart, use_container_width=True)
        
        with tabs[2]:
            st.markdown("### Hashgraph Verification")
            
            st.markdown("""
            Every transaction on HederaGive is recorded on the Hedera Hashgraph, 
            ensuring complete transparency and traceability. Below is the verification for this cause.
            """)
            
            st.markdown("#### Smart Contract Details")
            st.code(f"""
                Contract ID: {cause['transaction_id']}
                Creation Time: 2025-02-15T14:32:21.023Z
                Contract Type: EscrowWithMilestones
                Total Funds: :green[${cause['raised']:,}]
            """)
            
            st.markdown("#### Recent Transactions")
            
            # Mock transaction data
            transactions = [
                {"hash": "0.0.84729384", "date": "2025-03-15", "amount": 500, "type": "Donation"},
                {"hash": "0.0.84729385", "date": "2025-03-10", "amount": 1200, "type": "Donation"},
                {"hash": "0.0.84729386", "date": "2025-03-05", "amount": 3500, "type": "Milestone Release"},
                {"hash": "0.0.84729387", "date": "2025-03-01", "amount": 750, "type": "Donation"},
                {"hash": "0.0.84729388", "date": "2025-02-25", "amount": 1000, "type": "Donation"}
            ]
            
            for tx in transactions:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{tx['hash']}**")
                    st.markdown(f"Date: {tx['date']}")
                
                with col2:
                    st.markdown(f"**${tx['amount']:,}**")
                
                with col3:
                    if tx['type'] == 'Donation':
                        st.markdown("🔹 Donation")
                    else:
                        st.markdown("🔸 Fund Release")
            
            # Verification link
            st.markdown("---")
            st.markdown("[Verify on Hedera Explorer](https://hashscan.io/)")
        
        with tabs[3]:
            st.markdown("### Supporters")
            supporters = MOCK_SUPPORTERS.get("supporters", [])
    
            if supporters:
                for supporter in supporters:
                    cols = st.columns([2, 1, 1, 2])
                    with cols[0]:
                        st.markdown(f"**{supporter['donor']}**")
                    with cols[1]:
                        st.markdown(f"**${supporter['total_donated']:,}**")
                    with cols[2]:
                        st.markdown(f"{supporter['donations_count']} donations")
                    with cols[3]:
                        badges = supporter.get("badges", [])
                        if badges:
                            badge_str = " ".join(f"{badge['emoji']} {badge['name']}" for badge in badges)
                            st.markdown(badge_str)
                        else:
                            st.markdown("-")
                    st.markdown("---")
            else:
                st.info("No supporters available.")