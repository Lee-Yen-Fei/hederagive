import streamlit as st
from page import home, login, donor_dashboard, explore_causes, charity_management, impact_reports
import utils.state_management as state
from utils.data_utils import load_json_data, load_local_image

# Configure the Streamlit page
st.set_page_config(
    page_title="HederaGive",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# Navigation sidebar
with st.sidebar:
    st.image(load_local_image("hedera_give_logo.jpeg"), use_container_width=False, width=100)
    st.title(":orange[HederaGive]")
    st.markdown("*Transparent Giving with Web3*")
    
    if st.session_state.logged_in:
        st.write(f"Welcome, {st.session_state.current_user['name']}")
        
        # Display user's total impact and badges
        st.metric("Total Impact", f"${(st.session_state.current_user.get('total_donated', 0) or 0):,.2f}")
        
        # Show user badges
        if 'badges' in st.session_state.current_user and st.session_state.current_user['badges']:
            st.write("Your Badges:")
            badges_cols = st.columns(3)
            for i, badge in enumerate(st.session_state.current_user['badges']):
                with badges_cols[i % 3]:
                    st.markdown(f"**{badge['emoji']}**")
                    st.caption(badge['name'])
        
        # Navigation options
        st.subheader("Navigation")
        nav_options = ["Home"]
        
        if st.session_state.user_type == "donor":
            nav_options.extend(["My Dashboard", "Explore Causes", "Impact Reports"])
        elif st.session_state.user_type == "charity":
            nav_options.extend(["Charity Management", "Impact Reports"])
        
        page = st.radio("", nav_options)
        
        if st.button(":blue[Logout]"):
            state.logout()
            st.rerun()
    else:
        st.info("Please log in to access all features")
        page = st.radio("", ["Home", "Login"])

# Page routing
if not st.session_state.logged_in:
    if page == "Home":
        home.show()
    elif page == "Login":
        login.show()
else:
    if page == "Home":
        home.show()
    elif page == "My Dashboard":
        donor_dashboard.show()
    elif page == "Explore Causes":
        explore_causes.show()
    elif page == "Charity Management":
        charity_management.show()
    elif page == "Impact Reports":
        impact_reports.show()

# Footer
with st.container():
    st.divider()
    cols = st.columns([3, 1])
    with cols[0]:
        st.markdown("**HederaGive** | Powered by :blue[**Hedera Hashgraph**] and :blue[**Streamlit**]")
    with cols[1]:
        st.markdown("by :blue[**LEE YEN FEI**]")