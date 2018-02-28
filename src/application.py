#!/usr/bin/env python3
from flask import Flask, render_template, make_response
from flask import request, redirect, flash, jsonify, url_for
from flask import session as login_session
from flask import make_response
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests
import db_modules

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


app = Flask(__name__)
app.secret_key = "3QMRGOWGA04EG5NSJR0LS1DYJRSQA44G"


@app.route('/', methods=['GET'])
def index():
    return redirect('/catalog')


@app.route('/catalog', methods=['GET'])
def get_categories():
    """ View for the catalog endpoint.
        Return the category.html template filed with
        the catolog data"""
    if('statet' not in login_session):
        state = ''.join(random.choice(string.ascii_uppercase +
                        string.digits) for x in range(32))
        login_session['state'] = state
    categories = db_modules.getCategories()
    items = db_modules.getLatest10Items()
    return render_template(
                'categories.html',
                client_id=CLIENT_ID,
                categories=categories,
                items=items,
                user=login_session)


@app.route('/catalog/<string:category_name>', methods=['GET'])
def get_items_by_category(category_name):
    """ View for the catalog/<category_name> endpoint.
        Return the categoryitems.html template filed with
        the catolog data for an arbitrary category"""
    categories = db_modules.getCategories()
    category = getCategory(categories, category_name)
    items = db_modules.getCategoryItems(category.id)
    return render_template(
                'categoryitems.html',
                client_id=CLIENT_ID,
                categories=categories,
                category=category,
                items=items,
                user=login_session)


@app.route(
    '/catalog/<string:category_name>/<string:item_name>',
    methods=['GET'])
def get_category_item(category_name, item_name):
    """ View for the catalog/<category_name>/<item_name> endpoint.
        Return the item.html template filed with
        the catolog data for an arbitrary item"""
    categories = db_modules.getCategories()
    category = getCategory(categories, category_name)
    item = db_modules.getCategoryItem(category.id, item_name)
    return render_template(
                'item.html',
                client_id=CLIENT_ID,
                category=category,
                item=item,
                user=login_session)


@app.route(
    '/catalog/<string:category_name>/items/new',
    methods=['POST', 'GET'])
def add_item_to_category(category_name):
    """ View for the catalog/<category_name>/items/new endpoint.
        GET: Return the newcategoryitem.html template with
        form to add a new item to the category
        POST: Save the new item data and redirect to
        /catalog/<category_name> endpoint"""

    if 'user_id' not in login_session:
        return redirect('/catalog')
    categories = db_modules.getCategories()
    category = getCategory(categories, category_name)
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'category_id': category.id,
            'user_id': login_session['user_id']}
        db_modules.createCategoryItem(data)
        return redirect(url_for(
                    'get_items_by_category',
                    category_name=category_name))
    else:
        return render_template(
                    'newcategoryitem.html',
                    client_id=CLIENT_ID,
                    category=category,
                    user=login_session)


@app.route(
    '/catalog/<string:category_name>/<string:item_name>/edit',
    methods=['POST', 'GET'])
def edit_category_item(category_name, item_name):
    """ View for the catalog/<category_name>/<item_name>/edit endpoint.
        GET: Return the editcategoryitem.html template with
        form to edit a an arbitrary item
        POST: update the item data and redirect to
        /catalog/<category_name>/item_name> endpoint"""
    if 'user_id' not in login_session:
        return redirect('/catalog')
    categories = db_modules.getCategories()
    category = getCategory(categories, category_name)
    item = db_modules.getCategoryItem(category.id, item_name)
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        db_modules.commitUpdate()
        return redirect(url_for(
                    'get_category_item',
                    category_name=category_name,
                    item_name=request.form['name']))
    else:
        return render_template(
                    'editcategoryitem.html',
                    client_id=CLIENT_ID,
                    category=category,
                    item=item,
                    user=login_session)


@app.route(
    '/catalog/categories/<string:category_name>/<string:item_name>/delete',
    methods=['POST', 'GET'])
def delete_category_item(category_name, item_name):
    """ View for the catalog/<category_name>/<item_name>/delete endpoint.
        GET: Return the deletecategoryitem.html template
        with the confirmation to delete a an arbitrary item
        POST: delete the item data and redirect to
        /catalog/<category_name> endpoint"""
    if 'user_id' not in login_session:
        return redirect('/catalog')
    categories = db_modules.getCategories()
    category = getCategory(categories, category_name)
    item = db_modules.getCategoryItem(category.id, item_name)
    if request.method == 'POST':
        db_modules.deleteCategoryItem(item)
        return redirect(url_for(
                    'get_items_by_category',
                    category_name=category_name))
    else:
        return render_template(
                    'deletecategoryitem.html',
                    client_id=CLIENT_ID,
                    category=category,
                    item=item,
                    user=login_session)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Process the Google Oauth2 authorization sing in
        This function is a modified version of the one used
        in the Udacity google Oath2 lesson"""
    if request.args.get('state') != login_session['state']:
        response = make_response(
                    json.dumps('Invalid state parameter'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets(
                        'client_secrets.json',
                        scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response("""Failed to upgrade the
         authorization code.""", 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = (
        """https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"""
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    if result.get('error') is not None:
        response = make_response(
                    json.dumps(result.get('error')),
                    50)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
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
            login_session['user_id'] = useid
            response = make_response(
                json.dumps("Current user is already connected"),
                200)
            response.headers['Content-Type'] = 'application/json'
            return response
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {
            'access_token': credentials.access_token,
            'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    useid = db_modules.getUserID(data['email'])
    if useid is not None:
        login_session['user_id'] = useid
    else:
        login_session['user_id'] = db_modules.createUser(login_session)

    return "done"


@app.route('/gdisconnect')
def gdisconnect():
    """ Process the Google Oauth2 authorization sing out
        This function is a modified version of the one used
        in the Udacity google Oath2 lesson"""
    access_token = login_session.get('credentials')
    if access_token is None:
        response = make_response(
                    json.dumps('Current user not connected.'),
                    401)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')
    url = (
        """https://accounts.google.com/o/oauth2/revoke?token=%s"""
        % login_session['credentials'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
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
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(
                    json.dumps(
                        'Failed to revoke token for given user.',
                        400))
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')


"""
///////////////////////////////////////////////
////////////      API         /////////////////
//////////////////////////////////////////////
"""


@app.route(
        '/api/get_item/<string:category_name>/<string:item_name>',
        methods=['GET'])
def get_item_api(category_name, item_name):
    """ Return the information of a arbitrary Item in JSON format"""
    category = db_modules.getCategoryByName(category_name)
    item = db_modules.getCategoryItem(category.id, item_name)
    return jsonify(item=item.serialize)


@app.route('/api/get_category/<string:category_name>', methods=['GET'])
def get_category_api(category_name):
    """ Return the information of a arbitrary Category in JSON format"""
    category = db_modules.getCategoryByName(category_name)
    items = db_modules.getCategoryItems(category.id)
    response = category.serialize
    response["items"] = [item.serialize for item in items]
    return jsonify(category=response)


@app.route('/api/catalog', methods=['GET'])
def get_categories_api():
    """ Return the Catalog information in JSON format"""
    categories = db_modules.getCategories()
    response = []
    for category in categories:
        items = db_modules.getCategoryItems(category.id)
        result = category.serialize
        result["items"] = [item.serialize for item in items]
        response.append(result)
    return jsonify(categories=response)


def getCategory(categories, category_name):
    """ Return a category object if the name macht
     any in the list categories"""
    for category in categories:
        if category.name == category_name:
            return category
    return None


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8881)
