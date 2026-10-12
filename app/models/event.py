from app.extensions import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(64), nullable=False, default='Kejuaraan')
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(256), nullable=False)
    organizer = db.Column(db.String(128), default='Pengurus Pusat Buana Nurraga')
    poster_url = db.Column(db.String(512), nullable=True)
    registration_link = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(32), default='UPCOMING') # UPCOMING, ONGOING, COMPLETED
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(64), nullable=True)

    def __init__(self, title, category, event_date, location, description=None, 
                 organizer='Pengurus Pusat Buana Nurraga', poster_url=None, 
                 registration_link=None, status='UPCOMING', is_active=True, 
                 created_by=None, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.title = title
        self.category = category
        self.event_date = event_date
        self.location = location
        self.description = description
        self.organizer = organizer
        self.poster_url = poster_url
        self.registration_link = registration_link
        self.status = status
        self.is_active = is_active
        self.created_by = created_by

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'event_date': self.event_date,
            'location': self.location,
            'organizer': self.organizer,
            'poster_url': self.poster_url,
            'registration_link': self.registration_link,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'created_by': self.created_by
        }
