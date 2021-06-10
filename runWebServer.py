from flask import Flask, render_template, redirect, request  
from werkzeug.utils import secure_filename
import os.path

# Local application imports
from Scripts import handleOPT as opt
from Scripts import configHandler as conf

app = Flask(__name__) 

# Config Stuff
config = conf.readConf()
username = "ehrbase-user"
# File Uploads
app.config['UPLOAD_FOLDER'] = 'Input'
app.config['MAX_CONTENT_PATH'] = 6291456 # 6mb  ## IF we upload data as CSV there might be bigger files?
# OPT-Upload
optname = "Testwert"
successOfOPTUpload = "alert-secondary"
rueckmeldungOPTUpload = "Laden sie eine OPT-Datei hoch" #TODO: Auswahl von bereits vorhanden OPT-FILES
visibilityOPTUploadFeedback = "invisible .d-none"
# CSV-Upload
csvname = "test1"
successOfCSVUpload = "alert-secondary"
rueckmeldungCSVUpload = "Laden sie eine CSV-Datei hoch" #TODO: Auswahl von bereits vorhanden CSV-FILES
visibilityCSVUploadFeedback = "invisible .d-none"
# Navigation
currentTab = "uploadOPT"

test = "true"

@app.route("/") 
def home(): 
    return render_template('main.html')

@app.route('/flat_loader')
def flat_loader():
    global username
    global password
    global baseAdress 
    global openEHREndpoint
    global FLATEndpoint
    global optname
    global successOfOPTUpload 
    global rueckmeldungOPTUpload
    global csvname
    global successOfCSVUpload
    global rueckmeldungCSVUpload
    global visibilityCSVUploadFeedback
    global visibilityOPTUploadFeedback
    return render_template('flat_loader.html', 
                            username=username, 
                            optname=optname, 
                            successOfOPTUpload=successOfOPTUpload, 
                            rueckmeldungOPTUpload=rueckmeldungOPTUpload,
                            csvname = csvname,
                            successOfCSVUpload = successOfCSVUpload,
                            rueckmeldungCSVUpload = rueckmeldungCSVUpload,
                            visibilityCSVUploadFeedback = visibilityCSVUploadFeedback,
                            currentTab = currentTab,
                            visibilityOPTUploadFeedback = visibilityOPTUploadFeedback
                            
                            )

@app.route('/data_catalogue')
def data_catalogue():
    global test
    return render_template('data_catalogue.html', test=test)

@app.route('/aql_builder')
def aql_builder():
    return render_template('aql_builder.html')

# TODO Make forms easily updateable with WTForms
# https://betterprogramming.pub/how-to-use-flask-wtforms-faab71d5a034

######################################################################
##################### Helper Functions
######################################################################

# Allowed File Check
def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

######################################################################
##################### FORM Handler
######################################################################
# "Login Info" Form from "FLAT_Loader" Step: 1. Upload OPT
@app.route("/setUserInfo", methods=["POST"])
def setUserData():
    global username 
    global password
    global currentTab

    currentTab = "uploadOPT"
    # TODO Null and Input Check --> Feedback? --> See WTForms
    username = str(request.form["exampleInputEmail1"])
    password = str(request.form["exampleInputPassword1"])
    authHeader = opt.getAuthHeader(username, password)
    conf.setLoginData(authHeader)
    print("AuthHeader: ", authHeader)
    return redirect(request.referrer)  

# "EHR-Repo Info" Form from "FLAT_Loader" Step: 1. Upload OPT
@app.route("/setRepoInfo", methods=["POST"])
def setRepoInfo():
    global baseAdress 
    global openEHREndpoint
    global FLATEndpoint
    global currentTab

    currentTab = "uploadOPT"
    # TODO Null and Input Check --> Feedback? --> See WTForms
    baseAdress = str(request.form["baseAdress"])
    openEHREndpoint = str(request.form["openEHREndpoint"])
    FLATEndpoint = str(request.form['FLATEndpoint'])
    conf.setTargetRepo(baseAdress, openEHREndpoint, FLATEndpoint)
    print("baseAdress: ", baseAdress)
    print("opener: ", openEHREndpoint)
    print("flat: ", FLATEndpoint)
    return redirect(request.referrer)  

# getOPTFile
@app.route("/getOPTFile", methods=["POST"])
def getOPTFile():
    global optname
    global successOfOPTUpload
    global rueckmeldungOPTUpload
    global currentTab
    global visibilityOPTUploadFeedback

    currentTab = "uploadOPT"
    ALLOWED_EXTENSIONS= {'opt'}
    f = request.files['exampleFormControlFile1']
    if f and allowed_file(f.filename, ALLOWED_EXTENSIONS):
        f.save( os.path.join(app.config['UPLOAD_FOLDER'], 'OPT' , secure_filename(f.filename)) )
        successOfOPTUpload = "alert-success"
        optname = secure_filename(f.filename)
        rueckmeldungOPTUpload = "Erfolg! TemplateName: " + optname
        conf.settemplateName(optname)
        print(f.filename)
        visibilityOPTUploadFeedback = "visible"

        return redirect(request.referrer) 
    elif not f:
        successOfOPTUpload = "alert-warning"
        rueckmeldungOPTUpload = "Datei auswählen, dann uploaden"
    else:
        successOfOPTUpload = "alert-danger"
        rueckmeldungOPTUpload = "Fehler beim Upload:"+os.linesep+"Es können nur Dateien mit der Endung 'OPT' hochgeladen werden!"
        return redirect(request.referrer)  

    return redirect(request.referrer) 

# getCSVFile  ##TODO What if the user has multiple files or lots of files? Can we assume: one csv file = one mapping = one data set = one template
@app.route("/getCSVFile", methods=["POST"])
def getCSVFile():
    global csvname
    global successOfCSVUpload
    global rueckmeldungCSVUpload
    global visibilityCSVUploadFeedback
    global currentTab

    currentTab = "selectData"
    f = request.files['csvUpload']
    ALLOWED_EXTENSIONS= {'csv'}
    if f and allowed_file(f.filename, ALLOWED_EXTENSIONS):
        f.save( os.path.join(app.config['UPLOAD_FOLDER'], 'CSV' , secure_filename(f.filename)) )
        successOfCSVUpload = "alert-success"
        csvname = secure_filename(f.filename)
        rueckmeldungCSVUpload = "Erfolg! CSVName: " + csvname
        conf.settemplateName(csvname)
        print(f.filename)
        visibilityCSVUploadFeedback = "visible"

        #Read File for Rendering in Data Preview

        return redirect(request.referrer) 
    elif not f:
        successOfCSVUpload = "alert-warning"
        rueckmeldungCSVUpload = "Datei auswählen, dann uploaden"
    else:
        successOfCSVUpload = "alert-danger"
        rueckmeldungCSVUpload = "Fehler beim Upload:"+os.linesep+"Es können nur Dateien mit der Endung 'csv' hochgeladen werden!"
        return redirect(request.referrer)  


######################################################################
##################### Buttons
######################################################################

# buildMapping
@app.route("/buildMapping", methods=["POST"])
def buildMapping():
    
    # File has to be uploaded -> file name
    # AuthHeader needs to be present in config
    # ehr-repo info need to be present in config

    print ("Test")

    # Just call the optHandler!!!
    opt.handleOPT(
        config['targetRepo']['workdir'], 
        config['targetRepo']['templateName'], 
        config['targetRepo']['inputCSV'], 
        config['targetRepo']['targetRepoAdress'],
        config['targetRepo']['targetAuthHeader'],
        config['targetRepo']['targetflatAPIadress'],
        config['targetRepo']['targetopenEHRAPIadress']
        )

    return redirect(request.referrer) 

app.run(debug = True)