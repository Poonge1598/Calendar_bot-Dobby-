import os
import datetime
import json
from tempfile import NamedTemporaryFile
from collections import namedtuple
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def create_service(client_secret_dict, api_name, api_version, *scopes, prefix=''):
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    
    creds = None

    # Save the client_secret_dict to a temporary JSON file
    with NamedTemporaryFile(delete=False, suffix=".json") as temp_client_secret_file:
        temp_client_secret_file.write(json.dumps(client_secret_dict).encode())
        temp_client_secret_file_path = temp_client_secret_file.name

    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(temp_client_secret_file_path, SCOPES)
                creds = flow.run_local_server(port=0)

        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        return None
    finally:
        os.remove(temp_client_secret_file_path)

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt
