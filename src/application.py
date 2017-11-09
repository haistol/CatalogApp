#!/usr/bin/env python3
from flask import Flask, render_template, make_response, request

app=Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "welcome"

@app.route('/catalog', methods=['GET'])
@app.route('/catalog/categories', methods=['GET'])
def get_categories():
    pass

@app.route('/catalog/categories/new', methods=['POST', 'GET'])
def add_category():
    pass

@app.route('/catalog/categories/<category_id>/items', methods=['GET'])
def get_items_by_category(id=category_id):
    pass

@app.route('/catalog/categories/<category_id>/items/new', methods=['POST','GET'])
def add_item_to_category(id=category_id):
    pass

@app.route('/catalog/login', methods=['GET'])
def user_login():
    pass

@app.route('/catalog/signup', methods=['GET'])
def user_signup():
    pass

if __name__ =="__main__":
    app.debug=True
    app.run(host='0.0.0.0', port=8881)