from flask import Flask, jsonify, request
from db_manager import get_items_from_date_range
from tagger import get_json_tags_from_date_range
from ml import train_model, save_model, load_model, extract_model_forecast_data, make_prediction

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return {
        "message":"Hello!"
    }

@app.route('/ML', methods=['POST'])
def ml():
    #VALUES FOR ARGUMENTS ARE SET
    body=request.get_json()
    try:
        forecast_or_train=body["forecast_or_train"]
    except:
        forecast_or_train="forecast"
    try:
        collection_name=body["collection_name"]
    except:
        collection_name="Day"
    try:
        start_date=body["start_date"]  
    except: 
        start_date="2000-01-01T00:00:00.000Z"
    try:
        end_date=body["end_date"]
    except: 
        end_date="2022-01-01T00:00:00.000Z"

    if(forecast_or_train=="train"):
        json_tags=get_json_tags_from_date_range(collection_name, start_date, end_date)
        model = train_model(json_tags)
        save_model(model, f"./models/{collection_name}.bit")
        return {
            "collection_name":   collection_name,
            "start_date":   start_date,
            "end_date":   end_date,
            "trained": "ok"
        }
    else:
        candles=get_items_from_date_range(collection_name, start_date, end_date)
        model = load_model(f"./models/{collection_name}.bit")
        # x_train, x_test, y_train, y_test = extract_model_data(candles)
        #Generar prediccion (valores resultantes ichimoku)
        data=extract_model_forecast_data(candles)
        prediction = make_prediction(model, data)
        return {
            "collection_name":   collection_name,
            "start_date":   start_date,
            "end_date":   end_date,
            "prediction":prediction
        }
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(port=5000)