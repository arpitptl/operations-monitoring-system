from .models import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON  # Use JSON for PostgreSQL
from sqlalchemy.orm import relationship


class Form(Base):
    __tablename__ = 'forms'
    
    name = Column(String, unique=True, nullable=False)
    fields = Column(JSON, nullable=False)
    description = Column(String, nullable=True, default="description")
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User')
    
    def __repr__(self):
        return f'<Form {self.name}>'