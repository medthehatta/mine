import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def login(credential_file_path):
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            tok_info = pickle.load(token)
            if all(scp in tok_info["scopes"] for scp in SCOPES):
                creds = tok_info["creds"]
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credential_file_path, SCOPES
            )
            creds = flow.run_console()
        with open("token.pickle", "wb") as token:
            pickle.dump(
                {"scopes": SCOPES, "creds": creds}, token,
            )

    return creds


def entries(client, url, sheet, rng=None, indirect=None):
    book = client.open_by_url(url)
    sheet_ = book.worksheet(sheet)

    if rng:
        data = sheet_.get(rng)
        return [dict(zip(data[0], entry)) for entry in data[1:]]
    elif indirect:
        sheet_range = sheet_.get(indirect)[0][0]
        return entries(client, url, sheet, rng=sheet_range)
    else:
        return sheet_.get_all_records()
