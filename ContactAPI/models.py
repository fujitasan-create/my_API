from sqlalchemy import Column,Integer,String,Text
from database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(15), nullable=True, unique=True)
    message = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Contact(name={self.name}, email={self.email}, phone={self.phone})>"