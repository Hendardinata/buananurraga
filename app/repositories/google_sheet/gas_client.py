import requests
from flask import current_app

class GasClient:
    """
    Client for calling the Google Apps Script Web App.
    Acts as a bridge to Google Sheets and Drive.
    """
    
    @staticmethod
    def _call_api(action, payload=None):
        url = current_app.config['GAS_API_URL']
        secret_token = current_app.config['GAS_SECRET_TOKEN']
        spreadsheet_id = current_app.config['GOOGLE_SPREADSHEET_ID']
        
        if not url or not secret_token or not spreadsheet_id:
            raise ValueError("GAS config missing in environment variables (.env)")

        data = {
            "api_key": secret_token,
            "spreadsheet_id": spreadsheet_id,
            "action": action,
            "payload": payload or {}
        }

        response = requests.post(url, json=data)
        
        # Handle HTTP errors
        response.raise_for_status()
        
        # Parse JSON
        result = response.json()
        if not result.get('success'):
            raise Exception(f"GAS API Error: {result.get('error')}")
            
        return result.get('data')

    @staticmethod
    def get_all_members():
        return GasClient._call_api('getAllMembers')

    @staticmethod
    def add_member_to_staging(member_data):
        return GasClient._call_api('addMemberToStaging', payload=member_data)

    @staticmethod
    def upgrade_members(payload):
        return GasClient._call_api('upgradeMembers', payload=payload)

    @staticmethod
    def consolidated_promote(payload):
        return GasClient._call_api('consolidatedPromote', payload=payload)

    @staticmethod
    def upload_photo(base64_data, filename, folder_id, mime_type):
        payload = {
            "base64_data": base64_data,
            "filename": filename,
            "folder_id": folder_id,
            "mime_type": mime_type
        }
        return GasClient._call_api('uploadPhoto', payload=payload)

    @staticmethod
    def update_kta_status(nomor_induk, status="PUNYA"):
        return GasClient._call_api('updateMemberKtaStatus', payload={
            "nomor_induk": str(nomor_induk),
            "status": status
        })

    @staticmethod
    def get_budgets():
        return GasClient._call_api('getBudgets')

    @staticmethod
    def add_budget(budget_data):
        return GasClient._call_api('addBudget', payload=budget_data)
