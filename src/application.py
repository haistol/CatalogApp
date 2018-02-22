#!/usr/bin/env python3
from flask import Flask, render_template, make_response, request, redirect, flash, jsonify, url_for
from flask import session as login_session
from flask import make_response
import random, string
from  oauth2client.client import flow_from_clientsecrets
from  oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import db_modules

CLIENT_ID = json.loads(
    open('client_secrets.json','r').read())['web']['client_id']


app = Flask(__name__)
app.secret_key = "3QMRGOWGA04EG5NSJR0LS1DYJRSQA44G"

@app.route('/', methods=['GET'])
def index():
    return "welcome"

@app.route('/catalog', methods=['GET'])
@app.route('/catalog/categories', methods=['GET'])
def get_categories():
    if(not 'statet' in login_session):
        state = ''.join(random.choice(string.ascii_uppercase + string.
            digits) for x in range(32))
        login_session['state'] = state
    categories = db_modules.getCategories()
    items=db_modules.getLatest10Items()
    return render_template('categories.html', categories=categories,items=items,user=login_session)

@app.route('/catalog/categories/<string:category_name>', methods=['GET'])
def get_items_by_category(category_name):
    categories = db_modules.getCategories()
    category=getCategory(categories, category_name)
    items=db_modules.getCategoryItems(category.id)
    return render_template(
                'categoryitems.html',
                categories=categories,
                category=category,
                items=items,
                user=login_session)

@app.route(
    '/catalog/categories/<string:category_name>/<string:item_name>',
    methods=['GET'])
def get_category_item(category_name, item_name):
    categories = db_modules.getCategories()
    category=getCategory(categories, category_name)
    item=db_modules.getCategoryItem(category.id,item_name)
    return render_template(
                'item.html',
                category=category,
                item=item,
                user=login_session)

@app.route(
    '/catalog/categories/<string:category_name>/items/new',
    methods=['POST', 'GET'])
def add_item_to_category(category_name):
    if 'user_id' not in login_session:
        return redirect('/catalog')
    categories = db_modules.getCategories()
    category=getCategory(categories, category_name)
    if request.method == 'POST':
        data={'name':request.form['name'],
        'description':request.form['description'],
        'category_id': category.id,
        'user_id':login_session['user_id']}
        db_modules.createCategoryItem(data)
        return redirect(url_for('get_items_by_category',category_name=category_name))
    else:
        return render_template('newcategoryitem.html',category=category,user=login_session)
    

@app.route(
    '/catalog/categories/<string:category_name>/<string:item_name>/edit',
    methods=['POST', 'GET'])
def edit_category_item(category_name, item_name):
    if 'user_id' not in login_session:
        return redirect('/catalog')
    categories = db_modules.getCategories()
    category=getCategory(categories, category_name)
    item=db_modules.getCategoryItem(category.id,item_name)
    if request.method == 'POST':
        item.name=request.form['name']
        item.description=request.form['description']
        db_modules.commitUpdate()
        return redirect(url_for('get_category_item', category_name=category_name, item_name=request.form['name']))
    else:
        return render_template(
                    'editcategoryitem.html',
                    category=category,
                    item=item,
                    user=login_session)
    
@app.route(
    '/catalog/categories/<string:category_name>/<string:item_name>/delete',
    methods=['POST', 'GET'])
def delete_category_item(category_name, item_name):
    if 'user_id' not in login_session:
        return redirect('/catalog')
    categories = db_modules.getCategories()
    category=getCategory(categories, category_name)
    item=db_modules.getCategoryItem(category.id,item_name)
    if request.method == 'POST':
        db_modules.deleteCategoryItem(item)
        return redirect(url_for('get_items_by_category',category_name=category_name))
    else:
        return render_template(
                    'deletecategoryitem.html',
                    category=category,
                    item=item,
                    user=login_session)
    

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'),
        401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json',
        scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response("""Failed to upgrade the
         authorization code.""", 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ("""https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"""
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1].decode('utf-8'))
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),
            50)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id =credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match givin user IS."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        useid = db_modules.getUserID(login_session['email'])
        if useid is not None:
            login_session['user_id']= useid
            response = make_response(
                json.dumps("Current user is already connected"),
                200)
            response.headers['Content-Type'] = 'application/json'
            return response
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token,
        'alt':'json'}
    answer = requests.get(userinfo_url,params = params)
    data = json.loads(answer.text)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    useid = db_modules.getUserID(data['email'])
    if useid is not None:
        login_session['user_id']= useid
    else:
        login_session['user_id']= db_modules.createUser(login_session)
        
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('credentials')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

def getCategory(categories, category_name):
    for category in categories:
        if category.name == category_name:
            return category
    return None

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8881)
