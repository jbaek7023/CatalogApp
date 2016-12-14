from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Item, Category

from flask import session as login_session
import random, string

# google import stuff
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///itemcategory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state=''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=login_session['state'])


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
    item_elem = session.query(Item).filter_by(item=item).one() 
    
    creator = getUserInfo(item_elem.user_id)

    # if user didn't log in or the user is not the one who made the item
    if 'username' not in login_session:
        return render_template('public_content.html', item=item_elem)
    elif creator is not None:
        if creator.id != login_session['user_id']:
            return render_template('public_content.html', item=item_elem)
        else:
            return render_template('content.html', item=item_elem)
    else:
        return render_template('public_content.html', item=item_elem)




@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        flash("You have to login to add item")
        return redirect('/login')

    if request.method == 'POST':
        category = request.form['category']
        newItem = Item(
            item=request.form['title'],
            content=request.form['description'],
            category_id = category, 
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("%s has been created" % request.form['title'])
        return redirect(url_for('catalog' , category = category))
    else:
        categories = session.query(Category).all()
        return render_template('item_add.html', categories=categories)

@app.route('/catalog/<string:item>/edit', methods=['GET', 'POST'])
def editItem(item):
    if 'username' not in login_session:
        flash("You have to login to edit item")
        return redirect('/login')

    categories = session.query(Category).all()
    editedItem = session.query(Item).filter_by(item=item).one()

    if request.method == 'POST':
        if request.form['title']:
            editedItem.item = request.form['title']
        if request.form['description']:
            editedItem.content = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']

        flash("item '%s' has been edited" % request.form['title'])

        return redirect(url_for('items', category_id=request.form['category'], item=editedItem.item))
    else:
        return render_template('item_edit.html', categories=categories, item=editedItem)

@app.route('/catalog/<string:item>/delete', methods=['GET', 'POST'])
def deleteItem(item):
    if 'username' not in login_session:
        flash("You have to login to delete item")
        return redirect('/login')

    if request.method == 'POST':
        item_elem = session.query(Item).filter_by(item=item).one()
            
        category_id = item_elem.category_id

        session.delete(item_elem)
        session.commit()

        flash("item '%s' has been deleted" % item_elem.item)

        return redirect(
            url_for(
                'catalog',
                category=category_id))
    else:
        return render_template('item_delete.html')

@app.route('/catalog.json')
def mainJSON():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    
    return jsonify(Items=[i.serialize for i in items], Categories=[c.serialize for c in categories])

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
    # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'% access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
        json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    # changed credientials -> credentials.access_token
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    
     # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']


    # see if the user exists; if it doesn't, make a new one. 
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id



    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    return output

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

@app.route('/gdisconnect')
def gdisconnect():
    credentials_ = login_session.get('credentials')
    
    if credentials_ is None:
        response = make_response(json.dumps('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    access_token = login_session['credentials'] 
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    print result

    if result['status'] =='200':
        # Reset the user's session.
        # del login_session['credentials']
        # del login_session['gplus_id']
        # del login_session['username']
        # del login_session['email']
        # del login_session['picture']

        response = make_response(json.dumps('Successfully Disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response('Failed to revoke token for given user', 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/clear')
def clearSession():
    login_session.clear()
    return "Session cleared"

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None

def createUser(login_session):
    newUser = User(name = login_session['username'], email=login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    
    return user.id

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('main'))
    else:
        flash("You were not logged in")
        return redirect(url_for('main'))

# Config Footer starts from here
if __name__ == '__main__':
    app.secret_key = 'HBVu_VGHUQbvfV3Zyf4stdTd'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
