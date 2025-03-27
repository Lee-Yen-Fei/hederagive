import streamlit as st
import utils.state_management as state
import time

# Mock user database for demo purposes
MOCK_USERS = {
    "donor@example.com": {
        "password": "password123",
        "name": "Alex Johnson",
        "type": "donor",
        "wallet_id": "0.0.12345",
        "total_donated": 1250.50,
        "badges": [
            {"name": "First Donation", "emoji": "🌱"},
            {"name": "Regular Giver", "emoji": "🌟"},
            {"name": "Education Supporter", "emoji": "📚"}
        ]
    },
    "charity@example.com": {
        "password": "password123",
        "name": "Global Relief Foundation",
        "type": "charity",
        "wallet_id": "0.0.67890",
        "total_received": 45250.75,
        "causes": ["Disaster Relief", "Healthcare"]
    }
}

def show():
    st.title("Login to CharityChain")
    
    # Login tabs
    tab1, tab2, tab3 = st.tabs(["Email Login", "HashPack Wallet", "Create Account"])
    
    with tab1:
        with st.form("email_login_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button(":blue[Login]", use_container_width=True)
            
            if submit:
                if email in MOCK_USERS and MOCK_USERS[email]["password"] == password:
                    user = MOCK_USERS[email].copy()
                    user.pop("password", None)  # Remove password from session data
                    
                    # Show a loading spinner for effect
                    with st.spinner("Logging in..."):
                        time.sleep(1)
                    
                    # Set session state
                    state.login(user, user["type"])
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
    
    with tab2:
        st.write("Connect with HashPack wallet for secure blockchain authentication")
        
        wallet_id = st.text_input("HashPack Wallet ID (e.g. 0.0.12345)")
        
        if st.button("Connect Wallet", use_container_width=True):
            # In a real app, this would verify ownership of the wallet
            # For demo, we'll just check if the wallet ID exists in our mock data
            for email, user_data in MOCK_USERS.items():
                if user_data.get("wallet_id") == wallet_id:
                    user = user_data.copy()
                    user.pop("password", None)
                    
                    with st.spinner("Verifying wallet ownership..."):
                        time.sleep(1.5)
                    
                    # Set session state
                    state.login(user, user["type"])
                    st.success("Wallet connected successfully!")
                    st.rerun()
                    break
            else:
                st.error("Wallet not recognized. Please try again or create an account.")
    
    with tab3:
        with st.form("signup_form"):
            new_email = st.text_input("Email Address")
            new_name = st.text_input("Name")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            account_type = st.radio("Account Type", ["Donor", "Charity"])
            
            wallet_connect = st.checkbox("Connect HashPack Wallet")
            if wallet_connect:
                new_wallet_id = st.text_input("Wallet ID")
            
            submit_signup = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_signup:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_email or not new_name or not new_password:
                    st.error("Please fill in all required fields")
                else:
                    # In a real app, this would create a new user in the database
                    # For demo, we'll just show a success message
                    with st.spinner("Creating your account..."):
                        time.sleep(1.5)
                    
                    user_type = "donor" if account_type == "Donor" else "charity"
                    
                    # Create a new mock user
                    new_user = {
                        "name": new_name,
                        "type": user_type,
                        "wallet_id": new_wallet_id if wallet_connect else None,
                        "total_donated": 0 if user_type == "donor" else None,
                        "total_received": 0 if user_type == "charity" else None,
                        "badges": [] if user_type == "donor" else None,
                        "causes": [] if user_type == "charity" else None
                    }
                    
                    # Set session state
                    state.login(new_user, user_type)
                    st.success("Account created successfully!")
                    st.rerun()
    
    # Informational content
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Why Login with HashPack?")
        st.markdown("""
        - **Secure** - No password required
        - **Fast** - One-click authentication
        - **Verifiable** - Blockchain-backed identity
        - **Convenient** - Same wallet for donations
        """)
    
    with col2:
        st.subheader("Benefits of CharityChain")
        st.markdown("""
        - Track all your donations in one place
        - Verify impact with blockchain evidence
        - Earn badges and rewards
        - Receive personalized cause recommendations
        - Automatic tax documentation
        """)