import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_fallback'
    
    # Google API settings
    GOOGLE_SPREADSHEET_ID = os.environ.get('GOOGLE_SPREADSHEET_ID')
    GOOGLE_DRIVE_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
    GAS_API_URL = os.environ.get('GAS_API_URL')
    GAS_SECRET_TOKEN = os.environ.get('GAS_SECRET_TOKEN')
    
    # Template Version (Schema validation)
    TEMPLATE_VERSION = '2.0.0'
    
    # Business Constants
    MAX_HIJAU_PER_BATCH = 999
    
    NOMINAL_BIAYA = {
        'KAS_PUSAT': 15000,
        'KTA': 15000,
        'SERTIFIKAT': 20000,
        'PENGADAAN_SABUK': 50000,
        'PENGADAAN_BENDERA': 150000,
        'PENGADAAN_BADGE': 8500
    }
