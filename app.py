
from flask import (
    Blueprint, flash, Flask, g, redirect, render_template, request, session, url_for
)
from logging.config import dictConfig
import sqlite3 as sql
import re
import typing

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
    db, cur = get_db()
    find_organization = (cur.execute(f"SELECT id FROM organization WHERE name = \"{orgname}\"")).fetchone()
    if (find_organization is None):
        return render_template("org_notfound.html",org_name = orgname)
    
    org_id = find_organization["id"]
    d,p,message = org_contacts_process(request,cur,db,org_id)
    if (d != -1): request.form.delete = d
    if (p != -1): request.form.prompt = p

    list_of_contacts = (cur.execute(f"SELECT * FROM contact WHERE organization_id = {org_id}")).fetchall()

    return render_template("contacts_in_org.html",org_name = orgname, contacts = list_of_contacts, disp_message = message)

    
@app.route("/contact/<contact_id_str>",methods = ['GET','POST'])
def contact_info_page(contact_id_str):
    contact_id = int(contact_id_str)
    db, cur = get_db()

    #CASE invalid contact id
    find_contact = (cur.execute(f"SELECT * FROM contact WHERE id = {contact_id}")).fetchone()
    if (find_contact is None): return "This is invalid contact page"


    return "Working normal"



def org_contacts_process(request,cur,db,org_id) -> tuple[int | None, int | None, str]:
    #CASE: GET method
    if (request.method == "GET"):
        return request_default_response()
    
    assert request.method == "POST"
    #CASE: trigger edit prompt
    if request.form.get("Edit") is not None:
        return post_request_edit_contact(request,cur)

    #CASE: execute deletion
    elif(request.form.get("delete") is not None):
        return post_request_delete_contact(request,cur,db)
        
    assert request.form.get("prompt") is not None

    contact_id = int(request.form.get("prompt"))

    #CASE: cancel prompt
    if request.form.get("confirm") == "Cancel":
        return request_default_response()
    
    #CASE: trigger deletion prompt
    if request.form.get("confirm") == "Delete":
        return request_default_response(delete = contact_id,message=\
                                     "Are you sure you want to delete this contact? All associated contact info will be deleted as well.")
    

    fname = request.form.get("fname").rstrip()
    lname = request.form.get("lname").rstrip()
    dob = request.form.get("dob")
    
    #CASE: invalid input
    valid, message = are_inputs_valid(fname.lower(),lname.lower(),dob)
    if (not valid): 
        return request_default_response(None,-1,message)
    
    exact_matches = cur.execute(f"SELECT * FROM contact \
                WHERE organization_id = {org_id}\
                AND LOWER(first_name) = \"{fname.lower()}\"\
                AND LOWER(last_name) = \"{lname.lower()}\"\
                AND dob = \"{dob}\"\
                AND id != {contact_id}").fetchall()
    
    if (contact_id == 0):
        #CASE: adding contact
        if (len(exact_matches) != 0):
            return request_default_response(None,-1,\
                                            "There already exists a contact with identical first and last name and dob within this organization.")
        else:
            cur.execute(f"INSERT INTO contact(first_name,last_name,dob,organization_id) VALUES\
                        (\"{fname}\",\"{lname}\",\"{dob}\",{org_id})")
            db.commit()
            return request_default_response(message="You have successfully added a contact.")
    
    else:
        if (len(exact_matches) != 0):
            return request_default_response(-1,None,\
                                            "Please enter new contact information that does not overlap with exiting contacts.")
        else:
            
            cur.execute(f"UPDATE contact\
                        SET first_name = '{fname}',\
                            last_name = '{lname}',\
                            dob = '{dob}', \
                            organization_id = {org_id} \
                        WHERE id = {contact_id}")
            db.commit()
            return request_default_response(message="You have successfully edited and saved your changes to a contact.")

    

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

def are_inputs_valid(fname : str, lname : str, dob : str) -> tuple[bool,str]:
    valid = True
    message = ""
    if (len(fname) == 0 or len(lname) == 0):
        valid = False
        message = "Please enter non-whitespace names for both your first and last name entry."
    elif (len(fname) > 31 or len(lname) > 31):
        valid = False
        message = "Please enter first and last names under 31 characters."
    elif (len(dob) == 0):
        valid = False
        message = "Please enter a Date of Birth."
    return (valid,message)
    #function should return a true false for validity, then a relevant message



def post_request_edit_contact(request,cur):
    contact_id = int(request.form.get("Edit"))
    if (contact_id != 0):
        find_contact = (cur.execute(f"SELECT * FROM contact WHERE id = {contact_id}").fetchone())
        request.form.fname = find_contact["first_name"]
        request.form.lname = find_contact["last_name"]
        request.form.dob = find_contact["dob"]
    request.form.prompt = contact_id
    #returns for delete, prompt, and message
    return (None,contact_id,"")
    
def post_request_delete_contact(request,cur,db):
    deletion_id = int(request.form.get("delete"))
    cur.execute(f"DELETE FROM contact WHERE id = {deletion_id}")
    db.commit()
    return (None,None, "You have successfully deleted contact.")


def request_default_response(delete = None,prompt = None,message : str = ""):
    return (delete,prompt,message)

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
    


