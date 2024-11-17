import gspread
import httplib2
import sys
import os
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import re

sheet_name = "copyBOM"

# CLIENT_SECRET = 'client_secret_dev.json'


base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

# Construct the full path to client_secret_dev.json
CLIENT_SECRET = os.path.join(base_dir, "client_secret_dev.json")

SCOPE = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email",
]
STORAGE = Storage("credentials.storage")


def get_user_info():
    global user_info
    credentials = STORAGE.get()

    try:
        user_info_service = build(
            serviceName="oauth2",
            version="v2",
            http=credentials.authorize(httplib2.Http()),
        )
        user_info = None
        user_info = user_info_service.userinfo().get().execute()

    except Exception as e:
        print("Error getting user info: ", e)

    if user_info and user_info.get("id"):
        print("User info found")
        return user_info["email"]
    else:
        print("No user info found")
        return None


def authorize_credentials_old():
    credentials = STORAGE.get()
    # If the credentials don't exist in the storage location or are invalid, run the flow
    if credentials is None or credentials.invalid:
        return False
    else:
        # Refresh the access token
        try:
            credentials.refresh(httplib2.Http())
        except Exception as e:
            print("Error refreshing credentials", e)
            return False

        # Everything is good
        return True


# Authorize the api call
def google_connect():
    # Fetch credentials from storage
    credentials = STORAGE.get()
    # If the credentials doesn't exist in the storage location then run the flow
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials


def authorize_api():
    client = gspread.authorize(STORAGE.get())
    return client


def search_for_string(user_input):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    sheet_BOM = client.open(sheet_name).get_worksheet(0)

    word_patterns = ".*".join(rf"\b{re.escape(word)}\b" for word in user_input.split())
    criteria_re = re.compile(rf".*{word_patterns}.*", re.IGNORECASE)
    search = sheet_BOM.findall(criteria_re)

    return search


def get_id_from_sheet(pos):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    sheet_BOM = client.open(sheet_name).get_worksheet(0)

    id = sheet_BOM.cell(int(pos), 1).value
    return id


# Function for getting the value in a cell of the google sheets
def get_titles(id):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    # Name of the sheets to read

    # Open a specific worksheet
    sheet_BOM = client.open(sheet_name).get_worksheet(0)

    # Get all the column values from the BOM sheet
    data = [
        "Nom",
        "QuCAD",
        "QuCOM",
        "Manufacturier",
        "Matériaux",
        "Longueur/aire en pouce",
    ]
    status = ["Order status", "DXF / CAM", "Fab Status", "TYPE"]

    text = {}
    drop = {}

    for sheet_key in data:
        patterns = [rf"\b{re.escape(sheet_key)}\b"]
        combined_pattern = re.compile(rf'({".*".join(patterns)})', re.IGNORECASE)

        try:
            cell = sheet_BOM.cell(
                sheet_BOM.find(id, in_column=1).row,
                sheet_BOM.find(combined_pattern, in_row=1).col,
            )
            text[sheet_key] = cell.value
        except Exception as e:
            print(f"error for {sheet_key}", e)

    for sheet_key in status:
        patterns = [rf"\b{re.escape(sheet_key)}\b"]
        combined_pattern = re.compile(rf'({".*".join(patterns)})', re.IGNORECASE)
        try:
            cell = sheet_BOM.cell(
                sheet_BOM.find(id, in_column=1).row,
                sheet_BOM.find(combined_pattern, in_row=1).col,
            )
            drop[sheet_key] = cell.value
        except Exception as e:
            print(f"error for {sheet_key}: ", e)

    return text, drop


# Function to get the dropdown values from the google sheets
def get_drop(drop):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    patterns = [rf"\b{re.escape(drop)}\b"]
    combined_pattern = re.compile(rf'({".*".join(patterns)})', re.IGNORECASE)

    # Name of the sheets to read
    # Open a specific worksheet
    try:
        sheet_dropdown = client.open(sheet_name).get_worksheet(2)
        options = sheet_dropdown.col_values(
            sheet_dropdown.find(combined_pattern, in_row=1).col
        )
        options.pop(0)

    except Exception as e:
        print(e)
        options = []
    return options


# Fcuntion to modify the google sheets
def modify_sheet(id, data_dict):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    print(id, ": ", data_dict)

    # Open a specific worksheet
    worksheet = client.open(sheet_name).get_worksheet(0)
    failed = {}
    for title, data in data_dict.items():
        try:
            cell_col = worksheet.find(title, in_row=1).col
            cell_row = worksheet.find(id, in_column=1).row
            worksheet.update_cell(cell_row, cell_col, data)
        except Exception as e:
            print("failed: ", title, data)
            failed.update({title: data})

    if failed:
        return failed
    else:
        return None
