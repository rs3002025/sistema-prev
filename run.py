from app import app, db

# This context is necessary for Flask-SQLAlchemy to work correctly
with app.app_context():
    # You can uncomment the line below to create the database and tables
    # db.create_all()
    pass

if __name__ == '__main__':
    app.run(debug=True)
