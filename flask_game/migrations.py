
from flask_migrate import Migrate
from app import app, db

migrate = Migrate(app, db)

def upgrade():
    # Create tables
    db.create_all()
    
    # Drop and recreate tables
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            print("Tables recreated successfully")
        except Exception as e:
            print(f"Migration error: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    upgrade()
