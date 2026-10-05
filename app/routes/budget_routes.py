from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.core.auth import login_required, role_required, get_current_user
from app.services.budget_service import BudgetService

budget_bp = Blueprint('budget', __name__, url_prefix='/budget')

@budget_bp.route('/', methods=['GET'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def index():
    user = get_current_user()
    budgets = BudgetService.get_all_budgets()
    
    total_pemasukan = sum(float(b.get('NOMINAL', 0)) for b in budgets if str(b.get('JENIS', '')).upper() == 'PEMASUKAN')
    total_pengeluaran = sum(float(b.get('NOMINAL', 0)) for b in budgets if str(b.get('JENIS', '')).upper() == 'PENGELUARAN')
    saldo_akhir = total_pemasukan - total_pengeluaran
    
    # Pagination (10 per page)
    per_page = 10
    total_items = len(budgets)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages)) if total_items > 0 else 1
    
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_budgets = budgets[start_idx:end_idx]
    start_item = start_idx + 1 if total_items > 0 else 0
    
    return render_template('budget/index.html', 
                          budgets=paginated_budgets, 
                          user=user,
                          total_pemasukan=total_pemasukan,
                          total_pengeluaran=total_pengeluaran,
                          saldo_akhir=saldo_akhir,
                          page=page,
                          total_pages=total_pages,
                          total_items=total_items,
                          per_page=per_page,
                          start_item=start_item,
                          end_item=end_idx)

@budget_bp.route('/add', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def add():
    try:
        keterangan = request.form.get('keterangan')
        jenis = request.form.get('jenis')
        nominal = float(request.form.get('nominal', 0))
        cabang = request.form.get('cabang', 'PUSAT')
        
        BudgetService.add_budget(keterangan, jenis, nominal, cabang)
        flash('Data anggaran berhasil ditambahkan!', 'success')
    except Exception as e:
        flash(f'Gagal menambahkan anggaran: {str(e)}', 'error')
        
    return redirect(url_for('budget.index'))
