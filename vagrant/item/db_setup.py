import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key = True)
    category = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'category' : self.category,
        }    

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    uid = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """return object data in easily serializeable format"""
        return {
            'uid' : self.uid,
            'name' : self.name,
            'email' : self.email,
            'picture' :self.picture,
        }

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    item = Column(String(250), nullable=False)
    content = Column(String(250))

    category_id = Column(Integer, ForeignKey('category.category'))
    category = relationship(Category)

    user_id = Column(String(250), ForeignKey('user.uid'), nullable=True)
    user = relationship(User)

    @property
    def serialize(self):
        """return object data in easily serializeable format"""
        return {
            'id' : self.id,
            'item' : self.item,
            'content' : self.content,
        }

engine = create_engine('sqlite:///itemcategory.db')

Base.metadata.create_all(engine)