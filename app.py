from flask import Flask, render_template, request
import requests

app = Flask(__name__)

import pickle 
with open("model.pkl","rb") as f:
    model=pickle.load(f)
with open("encoder.pkl","rb") as f:
    encoder=pickle.load(f)
    
weather_api="ccfb0161da3049bdd4dbbe98986f6ed7"

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric"
    res = requests.get(url)
    data = res.json()
    
    if res.status_code != 200:
        raise Exception(data.get("message", "Failed to get weather data"))

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    
    # Rainfall data (optional, may be missing)
    rainfall = data.get("rain", {}).get("1h", 0.0)  # default to 0.0 if not available

    return temperature, humidity, rainfall
    
# Dummy logic to suggest crop based on simple conditions
def predict_crop(nitrogen, phosphorus, potassium,temperature,humidity, ph,rainfall):
    pred=model.predict([[nitrogen, phosphorus, potassium,temperature,humidity, ph,rainfall]])
    label=encoder.inverse_transform(pred)
    return label[0]

@app.route('/', methods=['GET', 'POST'])
def index():
    crop = ""
    if request.method == 'POST':
        city = request.form['city']
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorus'])
        potassium = float(request.form['potassium'])
        ph = float(request.form['ph'])
        temperature, humidity, rainfall = get_weather(city)

        crop = predict_crop(nitrogen, phosphorus, potassium,temperature,humidity, ph,rainfall)
    
    return render_template('index.html', crop=crop)

if __name__ == '__main__':
    app.run(debug=True)
