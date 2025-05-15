"""from flask import Flask, jsonify, request,render_template;
from flask_cors import CORS;
from datetime import datetime
import prediction

app = Flask(__name__,template_folder='templates')
CORS(app)
"""
Created a Flask API to serve the prediction model
"""

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    selected_date = datetime.strptime(request.form['target_date'], '%Y-%m-%d')
    current_date = datetime.now()
    
    target_date = request.form.get("target_date","")
    
    if not target_date:
        return jsonify({"error": "No target date provided"}), 400
    
    try:
        predict =  prediction.predict_exchange_rate(target_date)
        predict = round(float(predict),2)
        
        if predict is None:
            return jsonify({"error": "Prediction failed"}), 500
        
        return render_template("predict.html", 
                         prediction=predict,
                         selected_date=selected_date,
                         current_date=current_date)
    
    except Exception as e:
        return render_template("predict.html", prediction="Error: " + str(e))
    
if __name__ == '__main__':
    app.run(debug=True)"""

#changing the file for vercel deployment
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime
import prediction
from asgiref.wsgi import WsgiToAsgi
import os

# Make sure Flask knows where templates are
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_route():
    try:
        target_date = request.form.get("target_date", "")
        if not target_date:
            return jsonify({"error": "No target date provided"}), 400

        selected_date = datetime.strptime(target_date, '%Y-%m-%d')
        current_date = datetime.now()

        prediction_result = prediction.predict_exchange_rate(target_date)
        prediction_result = round(float(prediction_result), 2)

        return render_template("predict.html",
                               prediction=prediction_result,
                               selected_date=selected_date,
                               current_date=current_date)
    except Exception as e:
        return render_template("predict.html", prediction="Error: " + str(e))

# Convert Flask app to ASGI-compatible
asgi_app = WsgiToAsgi(app)

# Required entry point for Vercel
def handler(scope, receive, send):
    return asgi_app(scope, receive, send)