from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from models import Base


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(30), unique=True, nullable=False)
    company = Column(String(150), nullable=False, default='Not specified')
    creation_date = Column(DateTime, default=datetime.now)
    last_update = Column(DateTime, default=datetime.now)
    sales_contact_id = Column(Integer, ForeignKey('collaborator.id',
                                                  ondelete='SET NULL'), nullable=True)
    collaborator = relationship('Collaborator', backref='clients')

    def __repr__(self):
        return f"Client {self.full_name} : mail {self.email}, phone {self.phone_number}"
