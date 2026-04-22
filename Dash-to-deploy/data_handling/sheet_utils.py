import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

def load_data_from_gsheet(sheet_id, worksheet_name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)
    return df