from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.gallery_service import GalleryService
from app.core.auth import login_required, role_required

gallery_bp = Blueprint('gallery', __name__, url_prefix='/gallery')

@gallery_bp.route('/')
@login_required
@role_required(['super_admin', 'admin_pusat'])
def index():
    posts = GalleryService.get_all_posts()
    return render_template('gallery/index.html', posts=posts)

@gallery_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def create():
    if request.method == 'POST':
        image_file = request.files.get('image')
        title = request.form.get('title')
        post_date = request.form.get('post_date')
        
        if not title:
            flash('Judul dokumentasi wajib diisi!', 'error')
            return render_template('gallery/form.html', post=None)
            
        username = session.get('user_id')
        GalleryService.create_post(request.form, image_file, username)
        flash('Dokumentasi baru berhasil ditambahkan dan disinkronkan ke Landing Page!', 'success')
        return redirect(url_for('gallery.index'))
        
    return render_template('gallery/form.html', post=None)

@gallery_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def edit(post_id):
    post = GalleryService.get_post_by_id(post_id)
    if not post:
        flash('Dokumentasi tidak ditemukan.', 'error')
        return redirect(url_for('gallery.index'))
        
    if request.method == 'POST':
        image_file = request.files.get('image')
        GalleryService.update_post(post_id, request.form, image_file)
        flash('Data dokumentasi berhasil diperbarui!', 'success')
        return redirect(url_for('gallery.index'))
        
    return render_template('gallery/form.html', post=post)

@gallery_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def delete(post_id):
    if GalleryService.delete_post(post_id):
        flash('Dokumentasi berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus dokumentasi.', 'error')
    return redirect(url_for('gallery.index'))

@gallery_bp.route('/toggle/<int:post_id>', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin_pusat'])
def toggle(post_id):
    post = GalleryService.toggle_active(post_id)
    if post:
        st = 'dipublikasikan' if post.is_active else 'disembunyikan'
        flash(f'Status publikasi dokumentasi berhasil diubah ({st}).', 'success')
    return redirect(url_for('gallery.index'))
