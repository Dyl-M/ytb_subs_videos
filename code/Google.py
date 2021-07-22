import pickle
import datetime
import os

from google_auth_oauthlib.flow import InstalledAppFlow  # , Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


def create_service(client_secret_file, api_name, api_version, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    csf = client_secret_file
    api_sn = api_name
    api_v = api_version
    scopes_ = list(scopes[0])
    print(scopes_)

    cred = None

    pickle_file = f'token_{api_sn}_{api_v}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(csf, scopes_)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_sn, api_v, credentials=cred)
        print(api_sn, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        return None


def convert_to_rfc_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute).isoformat() + 'Z'
    return dt
