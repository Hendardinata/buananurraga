import re

class DataNormalizer:
    @staticmethod
    def clean_text(text):
        if not text:
            return ""
        # Remove multiple spaces and trim
        return re.sub(r'\s+', ' ', str(text)).strip()
        
    @staticmethod
    def normalize_branch_name(branch):
        """Fixes inconsistencies like 'LOMBOK TENGAH ' to 'LOMBOK TENGAH'"""
        return DataNormalizer.clean_text(branch).upper()

    @staticmethod
    def normalize_phone_number(phone):
        if not phone:
            return ""
        phone = str(phone).replace(" ", "").replace("-", "")
        # Standardize to 62...
        if phone.startswith("08"):
            return "628" + phone[2:]
        if phone.startswith("+62"):
            return phone[1:]
        return phone
