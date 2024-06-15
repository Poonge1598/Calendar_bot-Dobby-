from pprint import pprint
from google_authentication import create_service  # Ensure correct import
import streamlit_authenticator as stauth
import streamlit as st
import os
from openai_utils import text_to_speech, autoplay_audio, speech_to_text, ask_chatgpt_with_tools
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from google_calendar_utils import function_dict, tools

# Use secrets from Streamlit's secrets management
CLIENT_SECRET = {
    "installed": {
        "client_id": st.secrets["google"]["client_id"],
        "project_id": st.secrets["google"]["project_id"],
        "auth_uri": st.secrets["google"]["auth_uri"],
        "token_uri": st.secrets["google"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
        "client_secret": st.secrets["google"]["client_secret"],
        "redirect_uris": st.secrets["google"]["redirect_uris"]
    }
}

API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

st.set_page_config(page_title="Streamlit Basic Authentication", layout="wide")

#-- USER AUTHENTICATION -- 
#@st.cache_data()
def authenticate_user():
    service = create_service(CLIENT_SECRET, API_NAME, API_VERSION, SCOPES)
    if service:
        st.session_state['authenticated'] = True
        st.session_state['service'] = service

def login():
    if 'authenticated' not in st.session_state:
        st.button('Login into our calendar app', key='Login', on_click=authenticate_user)
    else:
        if st.session_state['authenticated']:
            return True
        else:
            st.button('Login into our calendar app', key='Login', on_click=authenticate_user)
            return False

if login():
    # Float feature initialization
    float_init()

    def initialize_session_state():
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi! How may I assist you today with your schedule?"}
            ]

    initialize_session_state()

    st.title("Calendar Bot 🤖")

    # Create footer container for the microphone
    footer_container = st.container()
    with footer_container:
        audio_bytes = audio_recorder()

    for message in st.session_state.messages:
        if isinstance(message, dict) and 'role' in message and 'content' in message:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
    
    elif audio_bytes:
        # Write the audio bytes to a file
        with st.spinner("Transcribing..."):
            webm_file_path = "temp_audio.mp3"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)

            transcript = speech_to_text(webm_file_path)
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(transcript)
                os.remove(webm_file_path)

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking🤔..."):
                final_response = ask_chatgpt_with_tools(st.session_state['service'], st.session_state.messages, function_dict, tools, verbose=False)
            with st.spinner("Generating audio response..."):    
                audio_file = text_to_speech(final_response)
                autoplay_audio(audio_file)
            st.write(final_response)
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            os.remove(audio_file)

    # Float the footer container and provide CSS to target it with
    footer_container.float("bottom: 0rem; right: 0rem;")
