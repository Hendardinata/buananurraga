from app.extensions import db
from datetime import datetime

class GalleryPost(db.Model):
    __tablename__ = 'gallery_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(64), nullable=False, default='Kejuaraan')
    category_slug = db.Column(db.String(64), nullable=False, default='kejuaraan')
    image_url = db.Column(db.String(512), nullable=False)
    post_date = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(256), nullable=False, default='Mataram, NTB')
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    caption = db.Column(db.Text, nullable=True)
    instagram_url = db.Column(db.String(512), nullable=True, default='https://www.instagram.com/buananurraga/')
    order_num = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(64), nullable=True)

    def __init__(self, title, category, image_url, post_date, location='Mataram, NTB',
                 category_slug=None, likes=0, comments=0, caption=None,
                 instagram_url='https://www.instagram.com/buananurraga/',
                 order_num=0, is_active=True, created_by=None, **kwargs):
        super(GalleryPost, self).__init__(**kwargs)
        self.title = title
        self.category = category
        self.category_slug = category_slug or category.lower().replace(' ', '-')
        self.image_url = image_url
        self.post_date = post_date
        self.location = location
        self.likes = likes
        self.comments = comments
        self.caption = caption
        self.instagram_url = instagram_url
        self.order_num = order_num
        self.is_active = is_active
        self.created_by = created_by

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'category_slug': self.category_slug,
            'categorySlug': self.category_slug,
            'image': self.image_url,
            'image_url': self.image_url,
            'date': self.post_date,
            'post_date': self.post_date,
            'location': self.location,
            'likes': self.likes,
            'comments': self.comments,
            'caption': self.caption,
            'url': self.instagram_url,
            'instagram_url': self.instagram_url,
            'order_num': self.order_num,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'created_by': self.created_by
        }
