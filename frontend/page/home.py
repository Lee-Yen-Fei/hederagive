import streamlit as st
import pandas as pd
import altair as alt
from utils.data_utils import load_json_data, load_local_image

def show():
    st.title(":blue[Welcome to :orange-background[HederaGive]]")
    st.subheader("Transparent Giving with :blue[Web3] Technology")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### Revolutionizing Charitable Giving
        
        HederaGive leverages Hedera Hashgraph technology to bring 
        unprecedented transparency and trust to charitable donations.
        
        - **Transparent** - Track every dollar from donation to impact
        - **Efficient** - Smart contracts automate fund distribution
        - **Verifiable** - Hashgraph-backed proof of donation and usage
        - **Engaging** - Earn badges and track your impact
        """)
        
        if not st.session_state.get('logged_in', False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.button(":blue[Join Now]", type="primary", use_container_width=True, 
                          on_click=lambda: st.session_state.update({"_nav": "Login"}))
            with col_b:
                st.button(":orange[Learn More]", use_container_width=True)
    
    with col2:
        st.image(load_local_image("hedera_give_logo.jpeg"), use_container_width=True)
    
    # Statistics section
    st.divider()
    st.subheader(":green[Our Impact]")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Donations", "$1.2M")
    with col2:
        st.metric("Active Charities", "52")
    with col3:
        st.metric("Donors", "3,240")
    with col4:
        st.metric("Success Rate", "99.8%")
    
    # Featured causes - load campaigns from JSON and select first 3 campaigns
    st.divider()
    st.subheader("Featured Causes")
    
    campaigns = load_json_data('campaigns.json')
    # If campaigns.json is a list, use it directly; otherwise, if wrapped in a key like "causes", extract that key.
    if isinstance(campaigns, dict) and "causes" in campaigns:
        campaigns = campaigns["causes"]
    
    featured_causes = campaigns[:3]
    
    # Display featured causes in columns
    cols = st.columns(3)
    for i, cause in enumerate(featured_causes):
        with cols[i]:
            # Use safe access with a fallback placeholder image if missing
            st.image(load_local_image(cause.get("image")), use_container_width=True)
            st.subheader(cause.get("name", "Unnamed Campaign"))
            st.write(cause.get("description", "No description available."))
            
            # Progress bar calculation with safe division
            goal = cause.get("goal", 1)
            raised = cause.get("raised", 0)
            progress = raised / goal if goal else 0
            st.progress(progress)
            st.write(f":green[${raised:,}] / ${goal:,} goal")
            
            st.button(":orange[Donate Now]", key=f"donate_{cause.get('id', i)}", use_container_width=True)

    # How it works section
    st.divider()
    st.subheader("How HederaGive Works")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 1. Donate")
        st.markdown("Choose a cause and make a secure donation. Every transaction is recorded on the Hedera Hashgraph.")
    with col2:
        st.markdown("### 2. Track")
        st.markdown("Follow your donation's journey from receipt to disbursement with real-time hashgraph verification.")
    with col3:
        st.markdown("### 3. Verify Impact")
        st.markdown("See the real-world impact of your generosity through verified reports and updates.")
    
    # Recent activity visualization (sample data remains unchanged)
    st.divider()
    st.subheader("Recent Platform Activity")
    
    transactions = pd.DataFrame({
        'date': pd.date_range(start='2025-03-01', periods=30, freq='D'),
        'amount': [500, 750, 1200, 300, 2500, 1100, 650, 800, 950, 1500, 
                   425, 675, 1350, 275, 2200, 1050, 600, 825, 975, 1450,
                   550, 700, 1150, 325, 2300, 1075, 625, 850, 925, 1550],
        'category': ['Education', 'Healthcare', 'Environment', 'Poverty', 'Disaster Relief', 
                     'Education', 'Healthcare', 'Environment', 'Poverty', 'Disaster Relief',
                     'Education', 'Healthcare', 'Environment', 'Poverty', 'Disaster Relief',
                     'Education', 'Healthcare', 'Environment', 'Poverty', 'Disaster Relief',
                     'Education', 'Healthcare', 'Environment', 'Poverty', 'Disaster Relief',
                     'Education', 'Healthcare', 'Environment', 'Poverty', 'Disaster Relief']
    })
    
    chart = alt.Chart(transactions).mark_circle(size=60).encode(
        x='date',
        y='amount',
        color='category',
        tooltip=['date', 'amount', 'category']
    ).properties(
        width=800,
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
    # Testimonials section
    st.divider()
    st.subheader("Testimonials")
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown("> *HederaGive has transformed how we report our impact to donors. The transparency builds trust.*")
        st.markdown("**- Sarah Johnson, Education for All**")
    
    with cols[1]:
        st.markdown("> *I can finally see exactly how my donations are being used. This is what charitable giving should be.*")
        st.markdown("**- Michael Chen, Donor**")
    
    with cols[2]:
        st.markdown("> *The gamification elements make giving fun and engaging. I love earning badges for my contributions!*")
        st.markdown("**- Aisha Patel, Donor**")

if __name__ == "__main__":
    show()
