from flask import Flask , render_template, request, redirect

app = Flask(__name__) 

distance = 0.1

@app.route("/") 
def home(): 
    global distance
    return render_template('helloWorld.html')

@app.route("/setdistance", methods=["POST"])
def setdistance():
    global distance
    distance = float(request.form["distance"])
    print("set distance to", distance)
    return redirect(request.referrer)   

app.run(debug = True)