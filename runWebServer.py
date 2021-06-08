from flask import Flask, render_template, redirect, request  

# Local application imports
from Scripts import handleOPT
from Scripts import configHandler as conf

app = Flask(__name__) 

distance = 0.1

@app.route("/") 
def home(): 
    global distance
    global username
    username = "ehrbase-user"
    global password
    return render_template('main.html', distance=distance)

# TODO Make forms easily updateable with WTForms
# https://betterprogramming.pub/how-to-use-flask-wtforms-faab71d5a034

# "Login Info" Form from "FLAT_Loader" Step: 1. Upload OPT
@app.route("/setUserData", methods=["POST"])
def setUserData():
    global username 
    global password
    # TODO Null and Input Check --> Feedback? --> See WTForms
    username = str(request.form["exampleInputEmail1"])
    password = str(request.form["exampleInputPassword1"])
    authHeader = handleOPT.getAuthHeader(username, password)
    conf.setLoginData(authHeader)
    print("AuthHeader: ", authHeader)
    return redirect(request.referrer)  

# "EHR-Repo Info" Form from "FLAT_Loader" Step: 1. Upload OPT
 

app.run(debug = True)