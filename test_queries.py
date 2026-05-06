from database import SessionLocal
from models import User, Personality

db = SessionLocal()

# Merr userin e parë dhe shfaq personalities të tij
user = db.query(User).first()
for p in user.personalities:
    print(p.name, p.description)

# Merr personality të parë dhe shfaq userin e lidhur
personality = db.query(Personality).first()
print(personality.user.full_name, personality.user.email)
print('-------------------------------------------------')

db.close()
