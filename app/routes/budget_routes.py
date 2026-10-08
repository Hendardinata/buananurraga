from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.core.auth import login_required, role_required, get_current_user
from app.services.budget_service import BudgetService
from app.repositories.in_memory.branches_repo import branches_repo

budget_bp = Blueprint('budget', __name__, url_prefix='/budget')

def format_datetime_id(dt_str):
    """
    Format string datetime (ISO atau DD/MM/YYYY) menjadi format Indonesia yang rapi:
    Contoh: '08 Okt 2026', '21:10'
    """
    if not dt_str:
        return "-", ""
    s = str(dt_str).strip()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    
    try:
        # Format ISO: '2026-10-08T21:10:00.000Z'
        if 'T' in s:
            clean = s.replace('Z', '').split('.')[0]
            dt = datetime.fromisoformat(clean)
            return f"{dt.day:02d} {months[dt.month - 1]} {dt.year}", dt.strftime('%H:%M')
            
        # Format DD/MM/YYYY HH:MM atau DD/MM/YYYY
        elif '/' in s:
            parts = s.split(' ')
            d_parts = parts[0].split('/')
            time_str = parts[1] if len(parts) > 1 else ''
            if len(d_parts) == 3:
                day, month, year = d_parts
                m_idx = int(month) - 1
                m_name = months[m_idx] if 0 <= m_idx < 12 else month
                return f"{int(day):02d} {m_name} {year}", time_str
                
        # Format YYYY-MM-DD
        elif '-' in s and len(s) >= 10:
            dt = datetime.strptime(s[:10], '%Y-%m-%d')
            time_str = s[11:16] if len(s) > 15 else ''
            return f"{dt.day:02d} {months[dt.month - 1]} {dt.year}", time_str
    except Exception:
        pass
        
    return s, ""

@budget_bp.route('/', methods=['GET'])
@login_required
@role_required(['super_admin', 'admin_pusat', 'admin_cabang'])
def index():
    user = get_current_user()
    all_budgets = BudgetService.get_all_budgets()
    all_branches = branches_repo.get_all_branches()
    user_branch_name = 'PUSAT'
    
    # 1. Tentukan basis data berdasarkan peran (Role Base Scope)
    if user['role'] in ['super_admin', 'admin_pusat']:
        base_budgets = all_budgets
    else:
        # admin_cabang hanya melihat cabang mereka sendiri
        branch = branches_repo.get_branch(user.get('branch_code'))
        user_branch_name = branch['branch_name'] if branch else user.get('branch_code', '')
        branch_name_upper = user_branch_name.upper()
        base_budgets = [b for b in all_budgets if str(b.get('CABANG', '')).upper() == branch_name_upper]
    
    # 2. Filter parameter dari UI (Search, Jenis, Cabang)
    search_query = request.args.get('search', '').strip()
    jenis_filter = request.args.get('jenis', '').strip().upper()
    branch_filter = request.args.get('branch', '').strip()

    # Jika super_admin/admin_pusat memilih filter cabang spesifik
    if user['role'] in ['super_admin', 'admin_pusat'] and branch_filter:
        scoped_budgets = [b for b in base_budgets if str(b.get('CABANG', '')).upper() == branch_filter.upper()]
    else:
        scoped_budgets = base_budgets

    # 3. Hitung akumulasi statistik (Pemasukan, Pengeluaran, Saldo)
    total_pemasukan = sum(float(b.get('NOMINAL', 0)) for b in scoped_budgets if str(b.get('JENIS', '')).upper() == 'PEMASUKAN')
    total_pengeluaran = sum(float(b.get('NOMINAL', 0)) for b in scoped_budgets if str(b.get('JENIS', '')).upper() == 'PENGELUARAN')
    saldo_akhir = total_pemasukan - total_pengeluaran

    # 4. Filter data tabel berdasarkan Jenis Transaksi dan Kata Kunci Pencarian
    display_budgets = scoped_budgets
    if jenis_filter in ['PEMASUKAN', 'PENGELUARAN']:
        display_budgets = [b for b in display_budgets if str(b.get('JENIS', '')).upper() == jenis_filter]
        
    if search_query:
        query_lower = search_query.lower()
        display_budgets = [
            b for b in display_budgets 
            if query_lower in str(b.get('KETERANGAN', '')).lower() or query_lower in str(b.get('CABANG', '')).lower()
        ]

    # 5. Format tampilan tanggal untuk setiap item
    enriched_budgets = []
    for b in display_budgets:
        item = dict(b)
        date_str, time_str = format_datetime_id(b.get('TANGGAL'))
        item['date_formatted'] = date_str
        item['time_formatted'] = time_str
        enriched_budgets.append(item)

    # 6. Paginasi (10 item per halaman)
    per_page = 10
    total_items = len(enriched_budgets)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages)) if total_items > 0 else 1
    
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_budgets = enriched_budgets[start_idx:end_idx]
    start_item = start_idx + 1 if total_items > 0 else 0
    
    return render_template('budget/index.html', 
                          budgets=paginated_budgets, 
                          user=user,
                          user_branch_name=user_branch_name,
                          all_branches=all_branches,
                          total_pemasukan=total_pemasukan,
                          total_pengeluaran=total_pengeluaran,
                          saldo_akhir=saldo_akhir,
                          search_query=search_query,
                          jenis_filter=jenis_filter,
                          branch_filter=branch_filter,
                          page=page,
                          total_pages=total_pages,
                          total_items=total_items,
                          per_page=per_page,
                          start_item=start_item,
                          end_item=end_idx)

@budget_bp.route('/add', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin_pusat', 'admin_cabang'])
def add():
    try:
        user = get_current_user()
        keterangan = request.form.get('keterangan', '').strip()
        jenis = request.form.get('jenis', 'PEMASUKAN').strip()
        nominal_str = request.form.get('nominal', '0')
        
        try:
            nominal = float(nominal_str)
        except ValueError:
            nominal = 0.0

        if not keterangan:
            flash('Keterangan transaksi wajib diisi!', 'warning')
            return redirect(url_for('budget.index'))

        if nominal <= 0:
            flash('Nominal transaksi kas harus lebih dari Rp 0!', 'warning')
            return redirect(url_for('budget.index'))
        
        if user['role'] in ['super_admin', 'admin_pusat']:
            cabang = request.form.get('cabang', 'PUSAT').strip()
            if not cabang:
                cabang = 'PUSAT'
        else:
            from app.repositories.in_memory.branches_repo import branches_repo
            branch = branches_repo.get_branch(user.get('branch_code'))
            cabang = branch['branch_name'] if branch else user.get('branch_code', 'PUSAT')
        
        BudgetService.add_budget(keterangan, jenis, nominal, cabang)
        flash('Data transaksi kas berhasil dicatat ke pembukuan!', 'success')
    except Exception as e:
        flash(f'Gagal menambahkan transaksi kas: {str(e)}', 'error')
        
    return redirect(url_for('budget.index'))
