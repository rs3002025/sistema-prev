from app import app, db, bcrypt
from app import User

def main():
    with app.app_context():
        print("--- Create Admin User ---")
        username = "admin"
        password = "password"

        if User.query.filter_by(username=username).first():
            print(f"User '{username}' already exists.")
            return

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin_user = User(username=username, password_hash=hashed_password, role='admin')

        db.session.add(admin_user)
        db.session.commit()

        print(f"Admin user '{username}' created successfully.")

if __name__ == '__main__':
    main()
