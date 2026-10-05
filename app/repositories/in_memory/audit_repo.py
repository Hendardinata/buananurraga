import json
import os
import uuid
from datetime import datetime

class AuditRepo:
    def __init__(self, log_dir='storage/logs', log_file='audit.jsonl'):
        self.log_dir = log_dir
        self.log_file = log_file
        self.log_path = os.path.join(self.log_dir, self.log_file)
        
        # Ensure directory exists
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log_action(self, user_id, action, target_member_id=None, details=None, ip_address=None):
        log_entry = {
            'log_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'target_member_id': target_member_id,
            'details': details or {},
            'ip_address': ip_address
        }
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
        return log_entry

audit_repo = AuditRepo()
