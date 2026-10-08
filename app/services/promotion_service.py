from app.repositories.google_sheet.gas_client import GasClient
from app.core.numbering import NumberingEngine
from app.core.cache import ttl_cache

class PromotionService:
    @staticmethod
    @ttl_cache(ttl_seconds=60)
    def fetch_staging_data():
        # Ideally, we should fetch from "DATA MENTAH" sheet
        # I'll implement a new GAS action for this, but for now we can mock it 
        # or use a new GAS action 'getStagingMembers'
        try:
            return GasClient._call_api('getStagingMembers')
        except:
            return []

    @staticmethod
    def process_promotion(event_date, location, promotions):
        """
        promotions is a list of dicts: {'nama_lengkap', 'cabang', 'new_level', 'ttl', 'whatsapp', ...}
        """
        # Sort and generate Nomor Induk
        processed_promotions = NumberingEngine.sort_and_assign_numbers(promotions, event_date)
        
        from datetime import datetime
        try:
            formatted_date = datetime.strptime(event_date, '%Y-%m-%d').strftime('%d-%m-%Y') if event_date else ""
        except:
            formatted_date = event_date
            
        payload = {
            "event_date": formatted_date,
            "location": location,
            "promotions": processed_promotions
        }
        
        # Send atomic request to GAS to update 3 sheets
        return GasClient._call_api('batchPromoteMembers', payload=payload)

    @staticmethod
    def upgrade_members(event_date, location, members):
        """
        members is a list of dicts: {'nomor_induk', 'new_level', 'nama_lengkap'}
        """
        from datetime import datetime
        try:
            formatted_date = datetime.strptime(event_date, '%Y-%m-%d').strftime('%d-%m-%Y') if event_date else ""
        except:
            formatted_date = event_date
            
        payload = {
            "event_date": formatted_date,
            "location": location,
            "members": members
        }
        
        return GasClient.upgrade_members(payload)

    @staticmethod
    def consolidated_promote(event_date, location, new_members, upgrade_members):
        from app.core.numbering import NumberingEngine
        from datetime import datetime
        
        # Sort and generate Nomor Induk for new members
        processed_new_members = NumberingEngine.sort_and_assign_numbers(new_members, event_date)
        
        try:
            formatted_date = datetime.strptime(event_date, '%Y-%m-%d').strftime('%d-%m-%Y') if event_date else ""
        except:
            formatted_date = event_date
            
        payload = {
            "event_date": formatted_date,
            "location": location,
            "new_members": processed_new_members,
            "upgrade_members": upgrade_members
        }
        
        return GasClient.consolidated_promote(payload)
