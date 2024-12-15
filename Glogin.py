import streamlit as st
import firebase_admin
from httpx_oauth.clients.google import GoogleOAuth2
import asyncio
from firebase_admin import credentials, auth, initialize_app

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred = credentials.Certificate("reraguru1-8f6bc9f0bc5f.json")
    initialize_app(cred)

def app():
    # Get client ID and secrets from Streamlit secrets
    client_id = st.secrets["client_id"]
    client_secret = st.secrets["client_secrets"]
    redirect_url = "https://reragurubot.streamlit.app"

    # Initialize the OAuth2 client
    client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)

    # Handle the callback from Google (if "code" is present in the URL)
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]  # Get the first "code" parameter value
        try:
            # Exchange the authorization code for an access token
            token = asyncio.run(client.get_access_token(code, redirect_url))
            # Fetch user profile information
            user_info = asyncio.run(client.get_user_info(token["access_token"]))

            # Update Streamlit session state with user details
            st.session_state.authenticated = True
            st.session_state.username = user_info.get("name", "Google User")
            st.session_state.useremail = user_info.get("email", "No Email")

            # Redirect to the chatbot after successful login
            st.experimental_rerun()
        except Exception as e:
            st.warning(f"Error during Google login: {e}")
    else:
        # Redirect to Google login page if not authenticated
        authorization_url = asyncio.run(client.get_authorization_url(
            redirect_url,
            scope=["email", "profile"],
            extras_params={"access_type": "offline"},
        ))
        st.markdown(f'<meta http-equiv="refresh" content="0;url={authorization_url}" />', unsafe_allow_html=True)
