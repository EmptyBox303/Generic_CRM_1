from flask import Flask
app = Flask(__name__)
@app.route("/")
def CRM():
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


