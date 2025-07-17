
from flask import (
    Blueprint, flash, Flask, g, redirect, render_template, request, session, url_for
)
from logging.config import dictConfig
import sqlite3 as sql


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "2034tupgfbdsJI0--tqwhudbP9q5w[yyjokuui[lj[];m]/zxcb/dtkjokhlpn,;';N(J(})||KJKHU)"

@app.route("/", methods = ['GET','POST'])
def org_page():
    db, cur = get_db()
    message = ""
    show_confirmation = False
    if (request.method == 'POST'):
        neworgname = request.form.get("neworgname")
        remove_org_name = request.form.get("remove")
        removal_confirmation = request.form.get("confirm")

        #CASE: confirming deletion of organization. Organization name is stored in session["remove"]
        if removal_confirmation is not None:
            assert session.get("remove") is not None
            if removal_confirmation == "Confirm":
                cur.execute(f"DELETE FROM organization WHERE name = \"{session.get("remove")}\"")
                db.commit()
            else:
                message = f"Removal of \"{session.get("remove")}\" has been cancelled."

        #CASE: creating new organization. 
        elif remove_org_name is None:
            assert neworgname is not None

            #No trailing whitespace, no spaces in the name, all lowercased
            neworgname = neworgname.rstrip().replace(' ', '_').lower()
            org_name_overlap = (cur.execute( \
                f"SELECT name FROM organization WHERE name = \"{neworgname}\"")).fetchall()
            
            #Invalid: Whitespace names
            if (len(neworgname) == 0):
                message = "Please enter a non-whitespace name."
                request.form.neworgname = ""

            #Invalid: name is too long
            elif (len(neworgname) > 255):
                message = "Please enter an organization name shorter than 255 characters."

            #Invalid: org name is already used
            elif (len(org_name_overlap) != 0):
                message = "This organization name already exists; Please use a different name."
            
            #Valid: New organization added, name field is cleared
            else:
                cur.execute( \
                    f"INSERT INTO organization(name) VALUES (\"{neworgname}\")")
                db.commit()
                request.form.neworgname = ""

        #CASE: requesting deletion of an organization. 
        else:
            message = f"Do you wish to remove \"{remove_org_name}\"? All associated contacts and contact info will be deleted."
            session["remove"] = remove_org_name
            show_confirmation = True
        
        
    
    get_orgs = (cur.execute("SELECT name FROM organization ORDER BY name")).fetchall()

    return render_template("index.html", orgs = get_orgs, warn = message, show = show_confirmation)




@app.route("/organization/<orgname>", methods = ['GET','POST'])
def contact_page(orgname):
    session.clear()
    db, cur = get_db()
    find_organization = (cur.execute(f"SELECT id FROM organization WHERE name = \"{orgname}\"")).fetchone()
    if (find_organization is None):
        return render_template("org_notfound.html",org_name = orgname)
    
    return f"Hello World {find_organization["id"]}"

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sql.connect("sql.db")
        db.row_factory = sql.Row
        cur = db.cursor()
    return db, cur

    
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


