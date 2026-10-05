import os

class StartupValidator:
    """
    Validator to check if required environment variables are set
    and the schema/templates are present.
    In the future, this will also validate the connection to Google Sheets.
    """
    @staticmethod
    def validate_env_vars():
        required_vars = [
            'SECRET_KEY',
            'GOOGLE_SPREADSHEET_ID',
            'GOOGLE_DRIVE_FOLDER_ID',
            'GAS_API_URL'
        ]
        
        missing = []
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)
                
        if missing:
            return False, f"Missing required environment variables: {', '.join(missing)}"
            
        return True, "Environment variables valid."

    @staticmethod
    def run_all_checks():
        # Will add more checks (e.g., checking sheet columns) later
        env_valid, env_msg = StartupValidator.validate_env_vars()
        if not env_valid:
            print(f"[WARNING] Startup Validation Failed: {env_msg}")
        else:
            print("[INFO] Startup Validation Passed: Configuration is ready.")
