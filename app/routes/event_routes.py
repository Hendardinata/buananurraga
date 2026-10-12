from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.event_service import EventService
from app.core.auth import login_required, role_required

event_bp = Blueprint('event', __name__, url_prefix='/events')

@event_bp.route('/')
@login_required
@role_required(['super_admin', 'admin_pusat'])
def index():
    events = EventService.get_all_events()
    return render_template('events/index.html', events=events)

@event_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def create():
    if request.method == 'POST':
        poster_file = request.files.get('poster')
        title = request.form.get('title')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        
        if not title or not event_date or not location:
            flash('Judul, tanggal, dan lokasi event wajib diisi!', 'error')
            return render_template('events/form.html', event=None)
        
        username = session.get('user_id')
        EventService.create_event(request.form, poster_file, username)
        flash('Event baru berhasil ditambahkan dan siap dipublikasikan!', 'success')
        return redirect(url_for('event.index'))
        
    return render_template('events/form.html', event=None)

@event_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def edit(event_id):
    event = EventService.get_event_by_id(event_id)
    if not event:
        flash('Event tidak ditemukan.', 'error')
        return redirect(url_for('event.index'))
        
    if request.method == 'POST':
        poster_file = request.files.get('poster')
        EventService.update_event(event_id, request.form, poster_file)
        flash('Data event berhasil diperbarui!', 'success')
        return redirect(url_for('event.index'))
        
    return render_template('events/form.html', event=event)

@event_bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def delete(event_id):
    if EventService.delete_event(event_id):
        flash('Event berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus event.', 'error')
    return redirect(url_for('event.index'))

@event_bp.route('/toggle/<int:event_id>', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def toggle(event_id):
    event = EventService.toggle_active(event_id)
    if event:
        st = 'dipublikasikan' if event.is_active else 'disembunyikan'
        flash(f'Status publikasi event berhasil diubah ({st}).', 'success')
    return redirect(url_for('event.index'))
