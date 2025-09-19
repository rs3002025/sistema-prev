from app import app, db

with app.app_context():
    print("Creating database and tables...")
    db.create_all()
    print("Database and tables created successfully.")
