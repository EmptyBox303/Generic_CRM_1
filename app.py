
from flask import (
    Blueprint, flash, Flask, g, redirect, render_template, request, session, url_for
)
import sqlite3 as sql
app = Flask(__name__)
@app.route("/", methods = ["GET"])
def org_page_get():
    #setup sql connection
    """ db = sql.connect('sql.db')
    cursor = db.cursor()
    with open('queries/org_setup.sql', 'r') as file:
        org_table_setup = file.read()
    cursor.execute(org_table_setup)
    db.commit()
    db.close() """

    return render_template("index.html")


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sql.connect("sql.db")
    return db

if __name__ == "__main__":
    app.run(debug=True)
    
    #display list of organizations
    #each has a button to delete
    #for each button:
    #   delete organization
    #   for each contact in organization:
    #       delete contact
    #has a button to add organization
    #when pressed:
    #   prompts user to type in new organization name
    #   if organization exists already:
    #       alert user
    #   otherwise add organization
    #clicking on each organization returns to rout "/<orgname>"


