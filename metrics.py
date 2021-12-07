import statistics
from db_manager import get_items_from_date_range
from tagger import get_json_tags_from_date_range
from ml import train_model, save_model, load_model, extract_model_forecast_data, make_prediction


best_accuracy=0
best_year=0
best_streak=0

collection_name="Month"
minimum_year={
    "Day":2000,
    "Week":2002,
    "Month":2002,
    "Hour": 2010
}
print(f"Collection: {collection_name} \n")
jump=7
for year in range(minimum_year[collection_name]+jump, 2022, jump):
    train_start_date=f"{minimum_year[collection_name]}-01-01T00:00:00.000Z"
    train_end_date=f"{year}-01-01T00:00:00.000Z"
    json_tags=get_json_tags_from_date_range(collection_name, train_start_date, train_end_date)
    model = train_model(json_tags)
    save_model(model, f"./models/{collection_name}.bit")

    start_date=f"{year}-01-01T00:00:00.000Z"
    end_date="2022-01-01T00:00:00.000Z"

    candles=get_items_from_date_range(collection_name, start_date, end_date)
    model = load_model(f"./models/{collection_name}.bit")
    data=extract_model_forecast_data(candles)
    prediction = make_prediction(model, data)

    new_candles = candles[51:]
    limit = len(new_candles)
    last_range=[]
    sample_limit=limit
    print(f"Train: start: {train_start_date}, end: {train_end_date}")
    print(f"Forecast: start: {start_date}, end: {end_date}")
    print("--------------------------------------------------------------------------------")
    print("--------------------------------------------------------------------------------")
    for streak in range(1,4):

        correct_predicts=0
        total_predicts=0
        # print(prediction[:33])
        for i in range(sample_limit):
            # print(i)
            current_close=new_candles[i]["close"]
            flag=True
            j=i+1
            if((j)>=limit):
                flag=False
            if(float(prediction[i])>0):
                while(flag):
                    if(current_close<new_candles[j]["close"]):
                        if((j+1)<limit):
                            j=j+1
                        else:
                            flag=False
                    else:
                        flag=False
                post_j=j-1-i
                if(post_j>=streak):
                    correct_predicts=correct_predicts+1
                total_predicts=total_predicts+1
                last_range.append(post_j)
            elif(float(prediction[i])<0):
                while(flag):
                    if(current_close>new_candles[j]["close"]):
                        if((j+1)<limit):
                            j=j+1
                        else:
                            flag=False
                    else:
                        flag=False
                post_j=j-1-i
                if(post_j>=streak):
                    correct_predicts=correct_predicts+1
                total_predicts=total_predicts+1
                last_range.append(post_j)
        # print(last_range)
        # print(f"Average: {sum(last_range)/len(last_range)}")

        # print("Metrics:")
        # print(f"Total: {total_predicts}, Correct: {correct_predicts}")
        accuracy=correct_predicts/total_predicts
        if(accuracy>best_accuracy):
            best_accuracy=accuracy
            best_year=year
            best_streak=streak
        print(f"Minimum streak: {streak}, Accuracy: {accuracy}")
        print("--------------------------------------------------------------------------------")
    print("/////////////////////////////////////////////////////////////////////////////////")
print(f"Collection: {collection_name}")
print(f"Best metrics: Pivot year: {best_year}, Accuracy: {best_accuracy}, Streak: {best_streak}")