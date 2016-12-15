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
category4 = Category(category="Baseball")
category5 = Category(category="Football")

session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.add(category5)
session.commit()

# add item 
item1 = Item(item = "Socer Ball", content='A football, soccer ball, or association football ball is the ball used in the sport of association football. The name of the ball varies according to whether the sport is called "football", "soccer", or "association football".', category = category1, user_id = 1)
item2 = Item(item = "Soccer Net", content="A game played on a rectangular field with net goals at either end in which two teams of 11 players each try to drive a ball into the other's goal by kicking, heading, or using any part of the body except the arms and hands.", category = category1, user_id = 1)
item3 = Item(item = "Shin Guards", content="a pad worn to protect the shins when playing soccer, hockey, and other sports.", category = category1, user_id = 2)
item4 = Item(item = "Soccer Shoes", content="Firm ground is the classic soccer shoe with cleats/studs designed to provide traction and stability on most natural grass, outdoor soccer fields. Firm Ground or molded cleats generally have a series of non-removable PU/TPU/rubber studs that are either bladed or conical in shape.", category = category1, user_id = 1)
item5 = Item(item = "Soccer Goalkeepr Gear", content="Keeperstop.com is the best resource for goalkeeper gloves, finger protection, soccer goalie jerseys and shirts, goalkeeper drills, and more. ", category = category1, user_id = 1)
item6 = Item(item = "Basketball", content="A basketball is a spherical inflated ball used in basketball games. Basketballs typically range in size from very small promotional items only a few inches in diameter to extra large balls nearly a foot in diameter used in training exercises.", category=category2, user_id = 2)
item7 = Item(item = "Basketball Shoes", content="Basketball is a strenuous exercise, in order to cope with intense exercise, for a pair of basketball shoes is concerned, you need to have good durability, support, stability, comfort and good damping effect.", category=category2, user_id = 1)

session.add(item1)
session.add(item6)
session.add(item3)
session.add(item7)
session.add(item5)
session.add(item1)
session.add(item4)

session.commit()

print "Added data!"

