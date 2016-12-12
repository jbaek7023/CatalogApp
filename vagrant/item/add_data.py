from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Category, Base, User, Item

engine = create_engine('sqlite:///itemcategory.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# add category 1 
category1 = Category(category="Soccer")
category2 = Category(category="Basketball")
category3 = Category(category="Swimming")

session.add(category1)
session.commit()
session.add(category2)
session.commit()
session.add(category3)
session.commit()

# add item 
item1 = Item(item = "Twoshinguards", content="two shinguards yeah yeah", category = category1)
item2 = Item(item = "solelygreat", content="two shinguards yeah yeah", category = category1)
session.add(item1)
session.commit()

print "Added data!"

