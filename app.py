import hmac
import streamlit as st

# Set the page configuration
st.set_page_config(
    page_title="Daily WP",
    page_icon=":airplane:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define Pages using st.page
aclist = st.Page(
    "pages/aclist/ac_reg.py", title="Aircraft List", icon=":material/dashboard:", default=True
)
admin = st.Page("pages/admin.py", title="Admin page", icon=":material/bug_report:")
dailywp = st.Page(
    "pages/dailywp.py", title="Daily WP", icon=":material/notification_important:"
)

mainbase = st.Page("pages/mainbase.py", title="Main Base", icon=":material/flight_land:")

# Define logout page for navigation
def logout():
    st.session_state.logged_in = False
    st.session_state["password_correct"] = False  # Reset password check
    st.session_state.pop("username", None)  # Clear username
    st.session_state.pop("password", None)  # Clear password
    st.rerun()  # Refresh the app after logout


# Check if user is logged in
def check_password():
    """Returns `True` if the user has provided the correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets["passwords"][st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 User not known or password incorrect")
    return False


# Ensure the user is authenticated
if not check_password():
    st.stop()

# Navigation Logic
if st.session_state.get("password_correct", False):
    # Define the navigation structure
    pg = st.navigation(
        {
            "Main Menu": [dailywp,aclist ,mainbase,admin]  # Reports section
        }
    )

    # Add a logout button
    if st.button("Logout"):
        logout()
else:
    pg = st.navigation([st.Page("login", title="Log in", icon=":material/login:")])

pg.run()  # This will handle the navigation and run the selected page