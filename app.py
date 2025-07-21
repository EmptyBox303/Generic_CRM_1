
from flask import (
    Blueprint, flash, Flask, g, redirect, render_template, request, session, url_for
)
from logging.config import dictConfig
import sqlite3 as sql
import re


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "2034tupgfbdsJI0--tqwhudbP9q5w[yyjokuui[lj[];m]/zxcb/dtkjokhlpn,;';N(J(})||KJKHU)"


dob_pattern = re.compile("[0,1][0-9]/[0-3][0-9]/[0-9]{4}") ##mm/dd/yyyy
days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]

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




@app.route("/<orgname>", methods = ['GET','POST'])
def contact_page(orgname):
    session.clear()
    db, cur = get_db()
    find_organization = (cur.execute(f"SELECT id FROM organization WHERE name = \"{orgname}\"")).fetchone()
    if (find_organization is None):
        return render_template("org_notfound.html",org_name = orgname)
    org_id = find_organization["id"]
    list_of_contacts = (cur.execute(f"SELECT * FROM contact WHERE organization_id = {org_id}")).fetchall()
    if (request.method == "POST"):
        pass

    
    """
    post ADD contact
        if any field is left blank:
            Please fill out all three required fields using non-whitespace characters. 
        length restrictions on first and last name
            Please enter a name less than 255 characters in length. 
        Special character restrictions
            if fname or lname contains @#$%&*()_+=\|{}{}:;"?/><! or numbers: Please input a first/last name with no numbers or special characters. 
        dob regular expression match:
            if character count mismatch, non-numeric 0, 1, 3, 4, 6,7,8,9, non-slashes 2 and 5: Please input date of birth with mm/dd/yyyy format.
        If not valid date:
            Please input a valid date of birth. 
        if triple match fname lname and dob:
            deny add contact
            message = "An identical contact already exists within {{orgname}}. Please input a different first name, last name, or date or birth"

    post EDIT contact
        popup window below with similar form, similar warnings(write an external function processing this)
        Spawn with details filled in based on entry
        a save, delete, and cancel button
        when prompted SAVE:
            if window contents are unchanged, message "No details were changed in this contact. Press cancel to exit the editting window.
            Otherwise, save new info, message "Contact details have been altered." Kill window. 
        when prompted delete:
            trigger new window asking for confirmation, warning "all associated contact info will be deleted."
            if confirmed:
                kill all windows delete contact, confirmation message "Contact has been deleted."
            otherwise: kill confirmation window. 
        when prompted cancel:
            kill editting window

    post DELETE contact
        spawn removal window
        
    """



    return render_template("contacts_in_org.html")

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


def is_valid_dob(s : str) -> bool:
    if (len(s) != 10): return False
    if (dob_pattern.search(s) is None): return False
    month = int(s[0:2])
    day = int(s[3:5])
    year = int(s[6:])
    if (day == 0): return False
    if (month != 2): return (day <= days_in_month[month-1])
    feb_day_lim = 29 if (year % 400 == 0 or (year % 4 == 0 and year % 25 != 0)) else 28
    #is leap year if is divisible by 400 OR divisible by 4 but not 25
    return (day <= feb_day_lim)
    
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
    


