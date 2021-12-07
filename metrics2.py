import statistics
from db_manager import get_items_from_date_range
from tagger import get_json_tags_from_date_range
from ml import train_model, save_model, load_model, extract_model_forecast_data, make_prediction


# best_accuracy=0
# best_year=0
# best_streak=0

collection_name="Hour"
minimum_year={
    "Day":2000,
    "Week":2002,
    "Month":2002,
    "Hour": 2010
}
print(f"Collection: {collection_name} \n")

# TRAIN
year=2020
train_start_date=f"{minimum_year[collection_name]}-01-01T00:00:00.000Z"
train_end_date=f"{year}-01-01T00:00:00.000Z"
json_tags=get_json_tags_from_date_range(collection_name, train_start_date, train_end_date)
model = train_model(json_tags)
save_model(model, f"./models/{collection_name}.bit")

# FORECAST
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
# for streak in range(1,42:
for tolerance in range(1,31):
# for tolerance in [30]:
    ranges=[]
    peaks=[]
    correct_predicts=0
    total_predicts=0
    true_positive=0
    false_positive=0
    true_negative=0
    false_negative=0
    for i in range(sample_limit):
        peaks_count=0
        current_close=new_candles[i]["close"]
        flag=True
        j=i+1
        if((j)>=limit):
            flag=False
        if(float(prediction[i])>0):
            current_tolerance=tolerance
            current_high=current_close
            while(flag):
                if(current_high<new_candles[j]["close"]):
                    current_tolerance=tolerance
                    current_high=new_candles[j]["close"]
                    if((j+1)<limit):
                        j=j+1
                    else:
                        flag=False
                else:
                    current_tolerance=current_tolerance-1
                    if(current_high!=current_close):
                        peaks_count=peaks_count+1
                    if(current_tolerance==0):
                        flag=False
                    elif((j+1)<limit):
                        j=j+1
                    else:
                        flag=False
            if(peaks_count>0):
                correct_predicts=correct_predicts+1
                true_positive=true_positive+1
                ranges.append(j-i)
            else:
                false_positive=false_positive+1
            peaks.append(peaks_count)
            total_predicts=total_predicts+1
        elif(float(prediction[i])<0):
            current_tolerance=tolerance
            current_low=current_close
            while(flag):
                if(current_low>new_candles[j]["close"]):
                    current_tolerance=tolerance
                    current_low=new_candles[j]["close"]
                else:
                    current_tolerance=current_tolerance-1
                    if(current_low!=current_close):
                        peaks_count=peaks_count+1
                    if(current_tolerance==0):
                        flag=False
                if((j+1)<limit and flag):
                    j=j+1
                else:
                    flag=False
            if(peaks_count>0):
                correct_predicts=correct_predicts+1
                true_negative=true_negative+1
                ranges.append(j-i)
            else:
                false_negative=false_negative+1
            peaks.append(peaks_count)
            total_predicts=total_predicts+1

    # print("Metrics:")
    # print(f"Total: {total_predicts}, Correct: {correct_predicts}")
    accuracy=correct_predicts/total_predicts
    average_range=sum(ranges)/len(ranges)
    # if(accuracy>best_accuracy):
    #     best_accuracy=accuracy
    #     best_year=year
    print(f"Tolerance: {tolerance}, Accuracy: {accuracy}")
    print(f"Total Forecasts: {total_predicts}, Correct Forecasts: {correct_predicts}")
    print(f"True Positive: {true_positive}, False Positive: {false_positive}")
    print(f"True Negative: {true_negative}, False Negative: {false_negative}")
    print(f"Trend Duration (Periods):")
    print(f"Mean: {average_range}, Mode: {statistics.mode(ranges)}, Median: {statistics.median(ranges)}")
    print("--------------------------------------------------------------------------------")
print("/////////////////////////////////////////////////////////////////////////////////")
# print(f"Collection: {collection_name}")
# print(f"Best metrics: Pivot year: {best_year}, Accuracy: {best_accuracy}, Streak: {best_streak}")