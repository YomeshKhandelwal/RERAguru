import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json
import requests
import bot
import Glogin

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('reraguru1-8f6bc9f0bc5f.json')
    firebase_admin.initialize_app(cred)

# Firebase Web API Key
FIREBASE_API_KEY = "AIzaSyAeO5uifnXESaKfebfMwHtQkWW2Ei-Ivq0"

def app():
    st.title(":violet[RERAguru] :house:")

    # Initialize session state variables
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    # Sign up function
    def sign_up_with_email_and_password(email, password, username=None):
        try:
            rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            if username:
                payload["displayName"] = username
            r = requests.post(rest_api_url, data=json.dumps(payload))
            if r.status_code == 200:
                return r.json()['email']
            else:
                st.warning(f"Error during signup: {r.json()['error']['message']}")
        except Exception as e:
            st.warning(f'Signup failed: {e}')

    # Sign in function
    def sign_in_with_email_and_password(email, password):
        try:
            rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            r = requests.post(rest_api_url, data=json.dumps(payload))
            if r.status_code == 200:
                data = r.json()
                return {
                    'email': data['email'],
                    'username': data.get('displayName', email)  # If no username, fallback to email
                }
            else:
                st.warning(f"Error during signin: {r.json()['error']['message']}")
                return None
        except Exception as e:
            st.warning(f'Signin failed: {e}')
            return None

    # Password reset function
    def reset_password(email):
        try:
            rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
            payload = {
                "email": email,
                "requestType": "PASSWORD_RESET"
            }
            r = requests.post(rest_api_url, data=json.dumps(payload))
            if r.status_code == 200:
                return True, "Reset email sent successfully"
            else:
                return False, r.json().get('error', {}).get('message', 'Unknown error')
        except Exception as e:
            return False, str(e)

    # Handle login
    def handle_login():
        email = st.session_state.email_input
        password = st.session_state.password_input

        # Replace with your actual Firebase API Key
        FIREBASE_API_KEY = "AIzaSyAeO5uifnXESaKfebfMwHtQkWW2Ei-Ivq0"

        rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            r = requests.post(rest_api_url, data=json.dumps(payload))
            r.raise_for_status()  # Raise an exception for non-200 status codes

            data = r.json()
            st.session_state.username = data.get('displayName', email)  # If no username, fallback to email
            st.session_state.useremail = data['email']
            st.session_state.authenticated = True
            st.success("Login successful!")

        except requests.exceptions.RequestException as e:
            st.warning(f"Error during login: {e}")
        except ValueError as e:
            st.warning(f"Error parsing response: {e}")

    # Handle logout
    def handle_logout():
        st.session_state.authenticated = False
        st.session_state.username = ''
        st.session_state.useremail = ''
        

    # Render login/signup form if not authenticated
    if not st.session_state.authenticated:
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password', type='password')
        st.session_state.email_input = email
        st.session_state.password_input = password

        if choice == 'Sign up':
            username = st.text_input("Enter your unique username")
            if st.button('Create my account'):
                user_email = sign_up_with_email_and_password(email, password, username)
                if user_email:
                    st.success('Account created successfully! Please login.')
                    st.balloons()
        else:
            st.button('Login', on_click = handle_login)
            if st.button('Sign in with Google'):
                if not st.session_state.get("authenticated", False):
                    Glogin.app()
                else:
                    st.success(f"Welcome back, {st.session_state['username']}!")
                    bot.app()  # Load the chatbot


            # Option to reset password
            if st.button('Forgot Password'):
                email_for_reset = st.text_input('Enter email to reset password')
                if st.button('Send Reset Link'):
                    success, message = reset_password(email_for_reset)
                    if success:
                        st.success(message)
                    else:
                        st.warning(f"Password reset failed: {message}")

    # If authenticated, show chatbot and logout option
    else:
        st.write(f'Logged in as: {st.session_state.username}')
        bot.app()  # Load the chatbot app after login
        if st.button('Sign out'):
            handle_logout()

# Run the app
if __name__ == "__main__":
    app()
