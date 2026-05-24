from database import SessionLocal
from services.demo_seed import seed_demo_data


def main():
    db = SessionLocal()
    try:
        seed_demo_data(db)
        print("Demo data created or already exists.")
        print("Login: admin@dps.com / admin123")
        print("IDs: workspace_id=1, role_id=1, persona_id=1, conversation_id=1")
    finally:
        db.close()


if __name__ == "__main__":
    main()
