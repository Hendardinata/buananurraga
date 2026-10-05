class BranchesRepo:
    def __init__(self):
        self.branches = {
            'LOTIM': {
                'branch_code': 'LOTIM',
                'branch_name': 'Lombok Timur',
                'kabupaten_kota': 'Lombok Timur',
                'status': 'ACTIVE'
            },
            'LOTENG': {
                'branch_code': 'LOTENG',
                'branch_name': 'Lombok Tengah',
                'kabupaten_kota': 'Lombok Tengah',
                'status': 'ACTIVE'
            },
            'LOBAR': {
                'branch_code': 'LOBAR',
                'branch_name': 'Lombok Barat',
                'kabupaten_kota': 'Lombok Barat',
                'status': 'ACTIVE'
            },
            'LOTARA': {
                'branch_code': 'LOTARA',
                'branch_name': 'Lombok Utara',
                'kabupaten_kota': 'Lombok Utara',
                'status': 'ACTIVE'
            },
            'MATARAM': {
                'branch_code': 'MATARAM',
                'branch_name': 'Mataram',
                'kabupaten_kota': 'Kota Mataram',
                'status': 'ACTIVE'
            },
            'SUMBAWA': {
                'branch_code': 'SUMBAWA',
                'branch_name': 'Sumbawa',
                'kabupaten_kota': 'Sumbawa',
                'status': 'ACTIVE'
            }
        }

    def get_all_branches(self):
        return list(self.branches.values())

    def get_branch(self, branch_code):
        return self.branches.get(branch_code)

branches_repo = BranchesRepo()
