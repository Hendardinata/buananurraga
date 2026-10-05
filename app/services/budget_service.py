from app.repositories.google_sheet.gas_client import GasClient
from datetime import datetime

class BudgetService:
    @staticmethod
    def get_all_budgets():
        try:
            budgets = GasClient.get_budgets()
            if not budgets:
                return []
            
            # Convert all keys to uppercase and strip whitespace to ensure consistent access
            cleaned_budgets = []
            for b in budgets:
                cleaned = {str(k).strip().upper(): v for k, v in b.items()}
                # Skip empty rows (where all essential fields are missing or empty)
                if not cleaned.get('TANGGAL') and not cleaned.get('KETERANGAN') and not cleaned.get('NOMINAL'):
                    continue
                cleaned_budgets.append(cleaned)
            return cleaned_budgets
            
        except Exception as e:
            print(f"Error fetching budgets: {e}")
            return []

    @staticmethod
    def add_budget(keterangan, jenis, nominal, cabang="PUSAT"):
        payload = {
            "tanggal": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "keterangan": keterangan.upper(),
            "jenis": jenis.upper(),
            "nominal": nominal,
            "cabang": cabang.upper()
        }
        return GasClient.add_budget(payload)
