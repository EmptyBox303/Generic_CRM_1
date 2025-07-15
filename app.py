
from flask import (
    Blueprint, flash, Flask, g, redirect, render_template, request, session, url_for
)
import sqlite3 as sql
app = Flask(__name__)
@app.route("/")
def CRM():
    #setup sql connection
    """ db = sql.connect('sql.db')
    cursor = db.cursor()
    with open('queries/org_setup.sql', 'r') as file:
        org_table_setup = file.read()
    cursor.execute(org_table_setup)
    db.commit()
    db.close() """

    return "<p>Hello, World!</p>"
    
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


