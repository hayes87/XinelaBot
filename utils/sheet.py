# https://docs.google.com/spreadsheets/d/1NRhDtTA6CVb6JHFUoSUVtEg3H12o-MUE7c4n3dre9xw/edit#gid=0
import json
import os

import gspread
from google.oauth2 import service_account
import ast


class Sheet:
    def __init__(self, sheet_key, worksheet_index=0):
        self.worksheet_index = worksheet_index
        credentials = self._get_credentials_from_env()
        self.client = self._authorize_gspread(credentials)
        self.sheet_key = sheet_key
        self.worksheet = None

    @staticmethod
    def _get_credentials():
        return service_account.Credentials.from_service_account_file(
            "resources/credentials.json",
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

    @staticmethod
    def _get_credentials_from_env():
        json_from_env = os.getenv("CREDENTIAL_JSON")
        if json_from_env is None:
            print("Json is invalid")
            return None
        credentials = json.loads(json_from_env)
        return service_account.Credentials.from_service_account_info(credentials,
                                                                     scopes=[
                                                                         'https://www.googleapis.com/auth/spreadsheets'])

    @staticmethod
    def _authorize_gspread(credentials):
        try:
            return gspread.authorize(credentials)
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return None

    def _get_worksheet(self):
        if self.worksheet is not None:
            return self.worksheet

        try:
            sheet = self.client.open_by_key(self.sheet_key)
            self.worksheet = sheet.get_worksheet(self.worksheet_index)
            return self.worksheet
        except Exception as e:
            print(f"Error getting worksheet: {e}")
            return None

    def refresh_worksheet(self):
        self.worksheet = None
        return self._get_worksheet()

    def get_column_values(self, column_index):
        worksheet = self._get_worksheet()

        if worksheet is None:
            print("Unable to access the worksheet.")
            return []

        column_values = worksheet.col_values(column_index)[1:]
        filtered_values = [value for value in column_values if value.strip()]

        return filtered_values

    def eval_get_column_values(self, column_index):
        worksheet = self._get_worksheet()

        if worksheet is None:
            print("Unable to access the worksheet.")
            return []

        column_values = worksheet.col_values(column_index)[1:]
        filtered_values = [ast.literal_eval(value) for value in column_values if value.strip()]

        return filtered_values
