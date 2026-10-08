from app import create_app
from app.extensions import db
from app.models.achievement import Achievement

app = create_app()

def create_tables():
    with app.app_context():
        print("Creating missing tables...")
        db.create_all()
        print("Done.")

if __name__ == '__main__':
    create_tables()
