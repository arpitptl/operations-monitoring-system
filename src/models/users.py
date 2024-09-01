from .models import Base
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Enum as SqlEnum
from sqlalchemy.orm import relationship
from enum import Enum
import bcrypt

class ActionEnum(Enum):
    INSERT = "INSERT"
    UPDATE_APPROVE = "UPDATE_APPROVE"
    SIGNOFF = "SIGNOFF"

class User(Base):
    __tablename__ = 'users'
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phonenumber = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    address = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    password_hash = Column(String, nullable=False)
    
    # Many to One relationship with roles
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role = relationship('Role')

    def set_password(self, password: str):
        """
        Hash the password and store it in the password_hash field.
        """
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verify the password against the stored hash.
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @classmethod
    def authenticate(cls, db_session, email: str, password: str):
        """
        Authenticate a user by email and password.
        """
        user = db_session.query(cls).filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
    
class Role(Base):
    __tablename__ = 'roles'
    
    role = Column(String, unique=True, nullable=False)
    actions = Column(SqlEnum(ActionEnum), nullable=False)