import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix
from pickle import dump, load

##Para instalar dependencias:
##  pip install numpy
##  pip install -U scikit-learn

def extract_row_prices(json_row, max = 10000):
    data = []
    counter = 0
    for price in json_row["candles"]:
        data.append(price["open"])
        data.append(price["high"])
        data.append(price["low"])
        data.append(price["close"])
        counter += 1
        if counter == max:
            break
    return np.array(data)

def extract_forecast_prices(json_row, max = 10000):
    data = []
    counter = 0
    for price in json_row:
        candle = []
        candle.append(price["open"])
        candle.append(price["high"])
        candle.append(price["low"])
        candle.append(price["close"])
        data.append(candle)
        counter += 1    
        if counter == max:
            break
    return np.array(data)

def extract_model_forecast_data(js):
    print("extracting data")
    data = extract_forecast_prices(js)
    pca_data = data.reshape(4, -1)
    print(pca_data.shape)
    pca = PCA(n_components=1)
    pca.fit(pca_data)
    pca_data = pca.transform(pca_data)
    print(pca_data.shape)
    components = []
    for component in pca_data:
        components.append(component[0])
    return np.array(components).reshape(1, -1)


def extract_data(json_data):
    data = []
    for row in json_data:
        data.append(np.append(extract_row_prices(row), row["tag"]))
    return np.array(data)

def extract_model_data(js):
    print("extracting data")
    data = extract_data(js)
    pca_x = data[:,:-1]
    y = data[:, -1].astype("str")
    print(pca_x.shape)
    pca = PCA(n_components=4)
    pca.fit(pca_x)
    pca_x = pca.transform(pca_x)
    print(pca_x.shape)
    return train_test_split(pca_x, y, test_size=0.2)

def get_model_metrics(model, x_test, y_test):
    print("generating model metrics")
    prediction = model.predict(x_test)
    accuracy = accuracy_score(y_test, prediction)
    matrix = confusion_matrix(y_test, prediction)
    return accuracy, matrix

def train_model(js):
    print("training model")
    x_train, x_test, y_train, y_test = extract_model_data(js)
    model = SVC(C=3, kernel="linear", tol=0.001, decision_function_shape="ovr", gamma="auto")
    model.fit(x_train, y_train)
    accuracy, matrix = get_model_metrics(model, x_test, y_test)
    print(accuracy)
    print(matrix)
    return model

def save_model(model, path):
    print("saving model into:", path)
    fmodel = open(path, "wb")
    dump(model, fmodel)
    fmodel.close()

def load_model(path):
    print("loading model from:", path)
    fmodel = open(path, "rb")
    model = load(fmodel)
    fmodel.close()
    return model

def make_prediction(model, x_data):
    print("making prediction")
    prediction = model.predict(x_data)
    return prediction

if __name__ == "__main__":
    #file = open("eurusd_data/EURUSD1440.json")
    file = open("text.json")
    js = json.load(file)
    file.close()

    #Para entrenar un nuevo modelo
    #model = train_model(js)
    #save_model(model, "model.bit")

    #Para cargar un modelo guardado (sin hacer otra vez train)
    model = load_model("model.bit")
    #x_train, x_test, y_train, y_test = extract_model_data(js)
    x_test= extract_model_forecast_data(js)
    print(x_test.shape)

    #Generar prediccion (valores resultantes ichimoku)
    prediction = make_prediction(model, x_test)
    print(prediction, len(prediction))