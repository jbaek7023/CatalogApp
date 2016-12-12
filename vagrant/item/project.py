from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Item, Category

app = Flask(__name__)

engine = create_engine('sqlite:///itemcategory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Config Header ends here

#string check for ids 

@app.route('/')
def main():
    categories = session.query(Category).all()
    items = session.query(Item).all()

    return render_template('main.html', categories=categories, items=items)

@app.route('/catalog/<string:category>/items')
def catalog(category):
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id = category).all()
    
    return render_template('items.html', category = category ,categories=categories, items=items)

@app.route('/catalog/<string:category_id>/<string:item>')
def items(category_id, item):
    # find the item element which is in the category and named category 
    category = session.query(Category).get(category_id)
    return 'ategory'+category
    # item_elem = session.query(Item).filter_by(item=item, category=category.id).one()

    # return render_template('content.html', item=item_elem)

@app.route('/catalog/<string:item>/edit')
def editItem(item):
    return 'editing '+item

@app.route('/catalog/<string:item>/delete')
def deleteItem(item):
    return 'didn\'t delete the item yet: '+item


@app.route('/catalog.json')
def catalogJSON():
    return 'json!'

# Config Footer starts from here
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
