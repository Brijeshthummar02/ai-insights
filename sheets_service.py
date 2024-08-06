import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

class SheetsService:
    def __init__(self, credentials_json, sheet_name):
        """
        Initializes the SheetsService with Google Sheets credentials and sheet name.
        If the sheet does not exist, it creates a new sheet.
        """
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet_name = sheet_name
        self.sheet = self._get_or_create_sheet(sheet_name)
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def _get_or_create_sheet(self, sheet_name):
        """
        Returns the sheet if it exists or creates it if it does not.
        """
        try:
            sheet = self.client.open(sheet_name).sheet1
            self.logger.info(f'Sheet "{sheet_name}" found.')
        except gspread.SpreadsheetNotFound:
            self.logger.info(f'Sheet "{sheet_name}" not found. Creating a new sheet.')
            sheet = self.client.create(sheet_name).sheet1
            # Optionally, share the sheet with your email for easy access
            # sheet.share('your_email@example.com', perm_type='user', role='writer')
            self._initialize_sheet(sheet)
        return sheet

    def _initialize_sheet(self, sheet):
        """
        Initializes the sheet with headers.
        """
        headers = ['Report ID', 'Client Name', 'Report Content', 'PDF URL', 'Timestamp']
        sheet.append_row(headers)
        self.logger.info('Sheet initialized with headers.')

    def read_data(self):
        """
        Reads all records from the Google Sheet.
        """
        self.logger.debug('Reading data from Google Sheets')
        try:
            data = self.sheet.get_all_records()
            self.logger.info('Data read successfully')
            return data
        except Exception as e:
            self.logger.error(f'Error reading data: {e}')
            return []

    def write_data(self, data):
        """
        Writes a new row of data to the Google Sheet.
        """
        self.logger.debug('Writing data to Google Sheets')
        try:
            self.sheet.append_row(data)
            self.logger.info('Data written successfully')
        except Exception as e:
            self.logger.error(f'Error writing data: {e}')
