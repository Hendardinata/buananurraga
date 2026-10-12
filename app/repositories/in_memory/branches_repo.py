class BranchesRepo:
    def __init__(self):
        self.branches = {
            'LOTIM': {
                'branch_code': 'LOTIM',
                'branch_name': 'Lombok Timur',
                'kabupaten_kota': 'Lombok Timur',
                'status': 'ACTIVE',
                'photo_url': '/static/img/branches/lotim.jpg'
            },
            'LOTENG': {
                'branch_code': 'LOTENG',
                'branch_name': 'Lombok Tengah',
                'kabupaten_kota': 'Lombok Tengah',
                'status': 'ACTIVE',
                'photo_url': '/static/img/branches/loteng.jpg'
            },
            'LOBAR': {
                'branch_code': 'LOBAR',
                'branch_name': 'Lombok Barat',
                'kabupaten_kota': 'Lombok Barat',
                'status': 'ACTIVE',
                'photo_url': '/static/img/branches/lobar.jpg'
            },
            'LOTARA': {
                'branch_code': 'LOTARA',
                'branch_name': 'Lombok Utara',
                'kabupaten_kota': 'Lombok Utara',
                'status': 'ACTIVE',
                'photo_url': '/static/img/branches/lotara.jpg'
            },
            'MATARAM': {
                'branch_code': 'MATARAM',
                'branch_name': 'Mataram',
                'kabupaten_kota': 'Kota Mataram',
                'status': 'ACTIVE',
                'photo_url': '/static/img/branches/mataram.jpg'
            },
            'SUMBAWA': {
                'branch_code': 'SUMBAWA',
                'branch_name': 'Sumbawa',
                'kabupaten_kota': 'Sumbawa',
                'status': 'ACTIVE',
                'photo_url': '/static/img/branches/sumbawa.jpg'
            }
        }

    def get_all_branches(self):
        return list(self.branches.values())

    def get_branch(self, branch_code):
        return self.branches.get(branch_code)

branches_repo = BranchesRepo()
