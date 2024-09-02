from sqlalchemy.orm import Session
from src.database import engine
from src.models.models import Base, User, Role

def seed():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)

    # Create roles
    l1_role = Role(name='L1', actions='INSERT')
    l2_role = Role(name='L2', actions='UPDATE_APPROVE')
    l3_role = Role(name='L3', actions='SIGNOFF')

    db.add(l1_role)
    db.add(l2_role)
    db.add(l3_role)
    db.commit()

    # Create users
    u1 = {
        "name": "arpit_l1",
        "email": "arpit_l1@gmail.com",
        "phonenumber": "9725073656",
        "is_admin": False,
        "address": "abcd",
        "date_of_birth": "2000-09-01T09:43:44.063Z",
        "role_id": 1
        }
    
    u2 = {
        "name": "arpit_l2",
        "email": "arpit_l2@gmail.com",
        "phonenumber": "9725073657",
        "is_admin": False,
        "address": "abcd",
        "date_of_birth": "2000-09-01T04:36:03.346Z",
        "role_id": 2
        }

    u3 = {
        "name": "arpit_l3",
        "email": "arpit_l3@gmail.com",
        "phonenumber": "9725073658",
        "is_admin": False,
        "address": "abcd",
        "date_of_birth": "2000-09-01T04:36:03.346Z",
        "role_id": 3
        }
    
    user1 = User(**u1)
    user1.set_password("test_l1@123")
    user2 = User(**u2)
    user1.set_password("test_l2@123")
    user3 = User(**u3)
    user1.set_password("test_l3@123")

    db.add(user1)
    db.add(user2)
    db.add(user3)
    db.commit()

    db.close()

if __name__ == '__main__':
    seed()

"""
CREATE FORM:

curl -X 'POST' \
  'http://0.0.0.0:8000/api/forms' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "form1",
  "fields": {
"name":"String",
"age":"Integer",
"bool":"Boolean"
},
  "created_by": 8
}'

"""