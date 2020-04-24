
import joblib
import os
import subprocess
import sys
import re
import math
import pandas as pd
import numpy as np
import random
import time

import fasttext

class FasttextClassifier:
    def __init__(self):
        self.model = fasttext.load_model("model.ftz")
        
    def preprocessing(self, input_data):
        
        # JSON to pandas DataFrame
        input_data = pd.DataFrame(input_data, index=[0], columns=['libelle'])
        input_data['libelle'] = input_data['libelle'].str.upper()

        # Nettoyage 'Description EAN'
        replace_values_ean = {
            ',': ' ',
            '&': ' ',
            '\+': ' ',
            r'\s\d+\s': ' ',
            r'^\d+ ': '',
            r'\d+\.?\d*(K?GR?)\s': ' #POIDS ',
            r'\d+\.?\d*(C?MM?)\s': ' #DIMENSION ',
            r'\d+\.?\d*([CM]?L)\s': ' #VOLUME ',
            r'\d+\.?\d*(%)\s': ' #POURCENTAGE ',
            r'\d+\.?\d*(X|\*)\s': ' #LOT ',
            r'\d+\.?\d*(X)\d\s': ' #LOT ',
            r'\d+\.?\d*(CT)\s': '#UNITE',
            r'(\sX?S\s)|(\sM\s)|(\sX?X?L\s)': ' #TAILLE ',
            r'\d+\/\d+': ' #TAILLE ',
            '&AMP': ' ',
        }
        input_data.replace({"libelle": replace_values_ean},regex=True,inplace=True)
        input_data.replace({"libelle": {r'([ ]{2,})': ' '}}, inplace=True, regex=True) # Suppression des espaces multiples
        input_data=input_data['libelle'][0]
        return input_data
        
    def predict(self, input_data):
        res = self.model.predict(input_data, k=3)
        return res
    
    def postprocessing(self, res):
        return {"predictions": [{"label":p[0].replace('__label__',''), "prediction":round(float(p[1]),2)} for p in np.transpose(res)], "status": "OK"}
        #return np.transpose(res)

    def compute_prediction(self, input_data):
        try:
            input_data = self.preprocessing(input_data)
            prediction = self.predict(input_data)
            prediction = self.postprocessing(prediction)
        except Exception as e:
            return {"status": "Error", "message": str(e)}

        return prediction
