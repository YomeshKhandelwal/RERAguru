import streamlit as st
from streamlit_option_menu import option_menu
import account, bot

class Multiapp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({"title": title, "function": function})

    def run(self):
        with st.sidebar:
            selected_app = option_menu(
                menu_title="MENU",
                options=["app", "account"],
                icons=["chat-fill", "person-circle"],
                menu_icon="char-text-fill",
                default_index=1,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        # Run the selected app
        if selected_app == "account":
            account.app()
        elif selected_app == "app":
            bot.app()

def app():
    multi_app = Multiapp()
    multi_app.run()

# Run the app
if __name__ == "__main__":
    app()
