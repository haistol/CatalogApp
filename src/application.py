#!/usr/bin/env python3
from flask import Flask, render_template, make_response, request, redirect

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "welcome"


@app.route('/catalog', methods=['GET'])
@app.route('/catalog/categories', methods=['GET'])
def get_categories():
    pass


@app.route('/catalog/categories/new', methods=['POST', 'GET'])
def add_category():
    if request.method = 'POST':
        return redirect(url_for('get_category'))
    else:
        return render_template('newcategory.html')


@app.route('/catalog/categories/<category_id>/edit', methods=['POST', 'GET'])
def edit_category(category_id):
    if request.method = 'POST':
        return redirect(url_for('get_category'))
    else:
        return render_template('editcategory.html', category=category_id)


@app.route('/catalog/categories/<category_id>/items', methods=['GET'])
def get_items_by_category(category_id):
    return render_template(
                'newcategoryitem.html',
                category=category,
                items=items)


@app.route(
    '/catalog/categories/<category_id>/items/new',
    methods=['POST', 'GET'])
def add_item_to_category(category_id):
    if request.method = 'POST':
        return redirect(url_for('get_items_by_category', category_id))
    else:
        return render_template('newcategoryitem.html')
    pass


@app.route(
    '/catalog/categories/<category_id>/<item_id/edit',
    methods=['POST', 'GET'])
def edit_category_item(category_id, item_id):
    if request.method = 'POST':
        return redirect(url_for('get_items_by_category', category_id))
    else:
        return render_template(
                    'editcategoryitem.html',
                    category=category,
                    items=items,
                    edit_item=item_id)
    pass

@app.route('/catalog/login', methods=['GET'])
def user_login():
    pass


@app.route('/catalog/signup', methods=['GET'])
def user_signup():
    pass


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8881)
