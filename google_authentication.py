import streamlit as st
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account

CREDENTIAL_INFOS = {
    "type": st.secrets["google"]["type"],
    "project_id": st.secrets["google"]["project_id"],
    "private_key_id": st.secrets["google"]["private_key_id"],
    "private_key": st.secrets["google"]["private_key"],
    "client_email": st.secrets["google"]["client_email"],
    "client_id": st.secrets["google"]["client_id"],
    "auth_uri": st.secrets["google"]["auth_uri"],
    "token_uri": st.secrets["google"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["google"]["client_x509_cert_url"],
    "universe_domain": st.secrets["google"]["universe_domain"]
}

API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']


def create_service():
    
    creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Authenticate using the service account
            credentials = service_account.Credentials.from_service_account_info(
            CREDENTIAL_INFOS, scopes=SCOPES)

    # Create the service  
    service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials, static_discovery=False)
    print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
    return service