import os
import uuid
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.event import Event

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

class EventService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def save_poster(file):
        """
        Save uploaded poster image to app/static/uploads/events/
        Returns the web URL path e.g. /static/uploads/events/xxx.jpg
        """
        if not file or not file.filename:
            return None

        if not EventService.allowed_file(file.filename):
            return None

        ext = file.filename.rsplit('.', 1)[1].lower()
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        rand_str = uuid.uuid4().hex[:8]
        unique_name = f"poster_{now_str}_{rand_str}.{ext}"
        
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'events')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_name)
        file.save(file_path)
        
        return f'/static/uploads/events/{unique_name}'

    @staticmethod
    def get_all_events(only_active=False):
        query = Event.query
        if only_active:
            query = query.filter_by(is_active=True)
        return query.order_by(Event.id.desc()).all()

    @staticmethod
    def get_active_events():
        return Event.query.filter_by(is_active=True).order_by(Event.id.desc()).all()

    @staticmethod
    def get_event_by_id(event_id):
        return Event.query.get(event_id)

    @staticmethod
    def create_event(data, poster_file=None, username=None):
        poster_url = None
        if poster_file and poster_file.filename:
            poster_url = EventService.save_poster(poster_file)
        
        # Fallback to poster_url from form if given as text link and no file uploaded
        if not poster_url and data.get('poster_url'):
            poster_url = data.get('poster_url').strip()

        event = Event(
            title=data.get('title', '').strip(),
            category=data.get('category', 'Kejuaraan').strip(),
            event_date=data.get('event_date', '').strip(),
            location=data.get('location', '').strip(),
            description=data.get('description', '').strip(),
            organizer=data.get('organizer', 'Pengurus Pusat Buana Nurraga').strip(),
            poster_url=poster_url,
            registration_link=data.get('registration_link', '').strip(),
            status=data.get('status', 'UPCOMING').strip(),
            is_active=True if str(data.get('is_active', '1')).lower() in ['1', 'true', 'on'] else False,
            created_by=username
        )
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def update_event(event_id, data, poster_file=None):
        event = Event.query.get(event_id)
        if not event:
            return None

        if poster_file and poster_file.filename:
            new_poster = EventService.save_poster(poster_file)
            if new_poster:
                event.poster_url = new_poster
        elif data.get('poster_url'):
            event.poster_url = data.get('poster_url').strip()

        event.title = data.get('title', event.title).strip()
        event.category = data.get('category', event.category).strip()
        event.event_date = data.get('event_date', event.event_date).strip()
        event.location = data.get('location', event.location).strip()
        event.description = data.get('description', event.description).strip()
        event.organizer = data.get('organizer', event.organizer).strip()
        event.registration_link = data.get('registration_link', event.registration_link).strip()
        event.status = data.get('status', event.status).strip()
        
        if 'is_active' in data:
            event.is_active = True if str(data.get('is_active', '')).lower() in ['1', 'true', 'on'] else False

        db.session.commit()
        return event

    @staticmethod
    def delete_event(event_id):
        event = Event.query.get(event_id)
        if not event:
            return False
        
        if event.poster_url and event.poster_url.startswith('/static/uploads/events/'):
            try:
                fname = os.path.basename(event.poster_url)
                p = os.path.join(current_app.root_path, 'static', 'uploads', 'events', fname)
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

        db.session.delete(event)
        db.session.commit()
        return True

    @staticmethod
    def toggle_active(event_id):
        event = Event.query.get(event_id)
        if not event:
            return None
        event.is_active = not event.is_active
        db.session.commit()
        return event
