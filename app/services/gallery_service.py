import os
import uuid
import re
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.gallery import GalleryPost

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

class GalleryService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def slugify(text):
        if not text:
            return 'umum'
        t = text.lower().strip()
        t = re.sub(r'[\s_]+', '-', t)
        t = re.sub(r'[^a-z0-9\-]', '', t)
        return t or 'umum'

    @staticmethod
    def save_image(file):
        """
        Simpan berkas gambar foto dokumentasi ke app/static/uploads/instagram/
        Mengembalikan path URL publik seperti /static/uploads/instagram/xxx.jpg
        """
        if not file or not file.filename:
            return None

        if not GalleryService.allowed_file(file.filename):
            return None

        ext = file.filename.rsplit('.', 1)[1].lower()
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        rand_str = uuid.uuid4().hex[:8]
        unique_name = f"insta_{now_str}_{rand_str}.{ext}"
        
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'instagram')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_name)
        file.save(file_path)
        
        return f'/static/uploads/instagram/{unique_name}'

    @staticmethod
    def get_all_posts(only_active=False):
        query = GalleryPost.query
        if only_active:
            query = query.filter_by(is_active=True)
        return query.order_by(GalleryPost.order_num.asc(), GalleryPost.id.desc()).all()

    @staticmethod
    def get_active_posts():
        return GalleryPost.query.filter_by(is_active=True).order_by(GalleryPost.order_num.asc(), GalleryPost.id.desc()).all()

    @staticmethod
    def get_post_by_id(post_id):
        return GalleryPost.query.get(post_id)

    @staticmethod
    def create_post(data, image_file=None, username=None):
        image_url = None
        if image_file and image_file.filename:
            image_url = GalleryService.save_image(image_file)
        
        # Fallback to image_url from form if given as text link/existing path
        if not image_url and data.get('image_url'):
            image_url = data.get('image_url').strip()

        if not image_url:
            image_url = '/static/uploads/instagram/default.jpg'

        category = data.get('category', 'Kejuaraan').strip()
        slug = data.get('category_slug', '').strip() or GalleryService.slugify(category)

        post = GalleryPost(
            title=data.get('title', '').strip(),
            category=category,
            category_slug=slug,
            image_url=image_url,
            post_date=data.get('post_date', '').strip() or datetime.now().strftime('%d %B %Y'),
            location=data.get('location', 'Mataram, NTB').strip(),
            likes=int(data.get('likes') or 0),
            comments=int(data.get('comments') or 0),
            caption=data.get('caption', '').strip(),
            instagram_url=data.get('instagram_url', 'https://www.instagram.com/buananurraga/').strip(),
            order_num=int(data.get('order_num') or 0),
            is_active=True if str(data.get('is_active', '1')).lower() in ['1', 'true', 'on'] else False,
            created_by=username
        )
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def update_post(post_id, data, image_file=None):
        post = GalleryPost.query.get(post_id)
        if not post:
            return None

        if image_file and image_file.filename:
            new_img = GalleryService.save_image(image_file)
            if new_img:
                if post.image_url and post.image_url.startswith('/static/uploads/instagram/'):
                    try:
                        old_p = os.path.join(current_app.root_path, 'static', 'uploads', 'instagram', os.path.basename(post.image_url))
                        if os.path.exists(old_p):
                            os.remove(old_p)
                    except Exception:
                        pass
                post.image_url = new_img
        elif data.get('image_url'):
            post.image_url = data.get('image_url').strip()

        category = data.get('category', post.category).strip()
        post.category = category
        post.category_slug = data.get('category_slug', '').strip() or GalleryService.slugify(category)
        post.title = data.get('title', post.title).strip()
        post.post_date = data.get('post_date', post.post_date).strip()
        post.location = data.get('location', post.location).strip()
        post.caption = data.get('caption', post.caption).strip()
        post.instagram_url = data.get('instagram_url', post.instagram_url).strip()
        
        if 'likes' in data:
            post.likes = int(data.get('likes') or 0)
        if 'comments' in data:
            post.comments = int(data.get('comments') or 0)
        if 'order_num' in data:
            post.order_num = int(data.get('order_num') or 0)
        if 'is_active' in data:
            post.is_active = True if str(data.get('is_active', '')).lower() in ['1', 'true', 'on'] else False

        db.session.commit()
        return post

    @staticmethod
    def delete_post(post_id):
        post = GalleryPost.query.get(post_id)
        if not post:
            return False

        if post.image_url and post.image_url.startswith('/static/uploads/instagram/'):
            try:
                fname = os.path.basename(post.image_url)
                p = os.path.join(current_app.root_path, 'static', 'uploads', 'instagram', fname)
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

        db.session.delete(post)
        db.session.commit()
        return True

    @staticmethod
    def toggle_active(post_id):
        post = GalleryPost.query.get(post_id)
        if not post:
            return None
        post.is_active = not post.is_active
        db.session.commit()
        return post
