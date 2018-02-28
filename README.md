# CatalogApp

This application project will provide a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. In this project, the combination of a dynamic websites with persistent data storage will result in a web application that provides a compelling service to the users.

## Installation

1. Clone this repo.
2. Install Python 3.x (https://www.python.org/downloads).
3. Install pip tool for Python 3.
4. Test your Python installation.
    * Open a command line terminal.
    * On that terminal run : `python --version` or `python3 --version`.
    * You should see a line with the python version you have installed.
5. Install the Python requirements module using pip.
    * Open a command line terminal.
    * On that terminal run : `pip3 install -r requirements.txt`.
6. Install PostgreSQL database (https://www.postgresql.org/download)
7. Create a new database with the name `catalog`
    * Configure the PostgreSQL (https://www.postgresql.org/docs/10/static/tutorial-start.html).
8. Configure the app to use a database user with access to the `catalog` DB
    * Go to repo directory location on your machine.
    * With a text editor open the file `db_modules.py`
    * Modify the line 8 with your user credentials: `engine = create_engine('postgresql://USERNAME:PASSWORD@localhost/catalog')`
9. Initialize the databe `catalog`
    * Open a command line terminal.
    * On that terminal go to repo directory location on your machine.
    * On that terminal run: `python created_database.py` or `python3 created_database.py`
    * Note.: the `created_database.py` script will create a predeterment list of categories feel free of edit the names in that list to meet your needs.
10. Get a Google Oauth2 API credentials
    * https://developers.google.com/identity/protocols/OAuth2
    * create a new credential for the app
11. In the credetial setting 
    * add point of origin: `http://localhost:8881`
    * add redirection URI: `http://localhost:8881/gconnect`
    * If you are planing to change the port for the app you need to change the port in these URIs
12. Add your Google Oauth2 API credentials to the app
    * Download the JSON from the credetial settings page.
    * Rename the downloaded file to `client_secrets.json`.
    * copy the file where the `application.py` script is located in the repo directory on your machine.

## Run Step

1. Open a command line terminal.
2. On that terminal go to repo directory location on your machine.
3. On that terminal run: `python application.py` or `python3 application.py`.
    * By default the app will listen on the port `8881`, you can change the port by editing the  `application.py` script line 309: `app.run(host='0.0.0.0', port=8881)`
4. Open a web browser and enter the URL `http://localhost:8881/catalog`
    * If you have changed the port in for the app you will need to change the port in the URL