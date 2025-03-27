import streamlit as st

def login(user_data, user_type):
    """
    Set the session state for a logged-in user
    
    Parameters:
    user_data (dict): User information
    user_type (str): Type of user ('donor' or 'charity')
    """
    st.session_state.logged_in = True
    st.session_state.current_user = user_data
    st.session_state.user_type = user_type

def logout():
    """Clear the session state for logout"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.user_type = None

def get_user_info():
    """Return current user information if logged in"""
    if st.session_state.logged_in:
        return st.session_state.current_user
    return None

def is_logged_in():
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)

def get_user_type():
    """Get the type of logged-in user"""
    return st.session_state.get('user_type', None)

def update_user_data(key, value):
    """
    Update a specific field in the user data
    
    Parameters:
    key (str): The field to update
    value: The new value
    """
    if st.session_state.logged_in:
        st.session_state.current_user[key] = value