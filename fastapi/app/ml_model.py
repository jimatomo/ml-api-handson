import pandas as pd
import numpy as np
import pickle
import lightgbm
import json

class ML_API:
    """
    Titanic Model Prediction
    """
    def __init__(self):
        # model instanse
        self.model = self.load_model()

    def load_model (self):
        with open('model.pkl', 'rb') as f:
            _model = pickle.load(f)
        return _model

    def predict(self, input_data):
        # Parse Json(Dict) to pandas df
        input_json = json.loads(input_data)
        data = pd.DataFrame(input_json)
        passenger_ids = data['PassengerId']

        # Preprocessing
        data['Sex'].replace(['male', 'female'], [0, 1], inplace=True)
        data['Embarked'].fillna(('S'), inplace=True)
        data['Embarked'] = data['Embarked'].map({'S': 0, 'C': 1, 'Q': 2}).astype(int)
        data['Fare'].fillna(np.mean(data['Fare']), inplace=True)
        data['Age'].fillna(data['Age'].median(), inplace=True)
        data['FamilySize'] = data['Parch'] + data['SibSp'] + 1
        data['IsAlone'] = 0
        data.loc[data['FamilySize'] == 1, 'IsAlone'] = 1

        delete_columns = ['Name', 'PassengerId', 'Ticket', 'Cabin']
        data.drop(delete_columns, axis=1, inplace=True)
        
        prediction = self.model.predict(data)

        # Postprocessing
        data['Prediction'] = prediction
        result = pd.concat([passenger_ids, data], axis=1)

        return {"prediction": result.to_dict(orient='records')}
