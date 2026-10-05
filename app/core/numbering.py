from datetime import datetime

class NumberingEngine:
    @staticmethod
    def generate_nomor_induk(event_date_str, index):
        """
        Generates nomor induk: [DDMMYYYY][XXX]
        event_date_str format: 'YYYY-MM-DD'
        index: 1 to 999
        """
        # Parse date
        dt = datetime.strptime(event_date_str, '%Y-%m-%d')
        date_part = dt.strftime('%d%m%Y')
        
        # Format index as 3 digits
        index_part = str(index).zfill(3)
        
        return f"{date_part}{index_part}"

    @staticmethod
    def sort_and_assign_numbers(members_list, event_date_str):
        """
        Takes a list of members, sorts them alphabetically by NAMA LENGKAP,
        and assigns a generated nomor induk to each.
        Returns the modified list.
        """
        # Sort alphabetically
        sorted_members = sorted(members_list, key=lambda x: x.get('nama_lengkap', '').upper())
        
        # Assign numbers
        for i, member in enumerate(sorted_members, start=1):
            member['nomor_induk'] = NumberingEngine.generate_nomor_induk(event_date_str, i)
            member['nomor_induk_display'] = f"{member['nomor_induk']} - {member.get('cabang', '')}"
            
        return sorted_members
