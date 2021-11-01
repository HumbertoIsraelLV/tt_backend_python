from pymongo import MongoClient
from dateutil.parser import parse

def get_database():
    # CONNECTION_STRING = "mongodb+srv://aeternam:master.ae13@eurusd.yhq8o.mongodb.net/EURUSD?retryWrites=true&w=majority"
    CONNECTION_STRING = "mongodb+srv://admin:admin@project1.cqzcd.mongodb.net/"
    client = MongoClient(CONNECTION_STRING)
    return client['EURUSD']

def get_items_from_date_range(collection_name, start_date, end_date):
    dbname = get_database()
    collection_name = dbname[collection_name]
    start_date=parse(start_date)
    end_date=parse(end_date)
    response = collection_name.find({'_id': {"$gte":start_date, "$lte":end_date}})
    items_list=[]
    for i in response:
        items_list.append(i)
    return items_list

# --------------------------------------------------
# TESTS:
# --------------------------------------------------
if __name__ == "__main__":    
    response=get_items_from_date_range()