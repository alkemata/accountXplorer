from werkzeug.security import generate_password_hash
from app import app, db
from models import User

def init_db():
    with app.app_context():
        try: 
            db.create_all()  # Create tables
            # Check if the initial user exists
            if not User.query.filter_by(username=app.config['INITIAL_USERNAME']).first():
                # Add initial user
                hashed_password = generate_password_hash(app.config['INITIAL_PASSWORD'], method='sha256')
                new_user = User(username=app.config['INITIAL_USERNAME'], password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                print("Initialized the database and added the initial user.")
        except Exception as e:
            logger.error("Error initializing the database: %s", e)
            raise

if __name__ == '__main__':
    init_db()
