from app.repositories.google_sheet.gas_client import GasClient
from app.core.normalizer import DataNormalizer
from app.core.cache import ttl_cache

class MemberService:
    @staticmethod
    @ttl_cache(ttl_seconds=60)
    def get_all_members():
        # Fetch raw data from GAS
        raw_members = GasClient.get_all_members()
        
        # Normalize and process data if needed
        cleaned_members = []
        for member in raw_members:
            # Clean branch name just in case of trailing spaces
            member['CABANG'] = DataNormalizer.normalize_branch_name(member.get('CABANG', ''))
            member['NAMA LENGKAP'] = DataNormalizer.clean_text(member.get('NAMA LENGKAP', ''))
            
            # Additional processed fields can be added here
            cleaned_members.append(member)
            
        return cleaned_members

    @staticmethod
    def get_member_by_id(nomor_induk):
        target = str(nomor_induk).strip().lower()
        members = MemberService.get_all_members()
        for member in members:
            val = str(member.get('NOMOR INDUK', '')).strip().lower()
            if val == target:
                return member
            # Also handle if nomor induk has branch suffix or is part of it
            if val and target and (val in target or target in val):
                # exact match preferred, but if query was just the number part (e.g. 25052025001)
                val_clean = val.split(' - ')[0].strip()
                target_clean = target.split(' - ')[0].strip()
                if val_clean == target_clean:
                    return member
        return None

    @staticmethod
    def update_kta_status(nomor_induk, status="PUNYA"):
        result = GasClient.update_kta_status(nomor_induk, status=status)
        try:
            MemberService.get_all_members.clear_cache()
        except Exception:
            pass
        return result
