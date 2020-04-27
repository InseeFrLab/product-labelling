
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
        # Standardisation du libelle
        replace_accents = {
                'à': 'a',
                'â': 'a',
                'é': 'e',
                'è': 'e',
                'ï': 'i',
                'î': 'i',
                'ô': 'o',
                'ù': 'u',
                }
        input_data.replace({"libelle": replace_accents}, regex=True, inplace=True)
        input_data['libelle'] = input_data['libelle'].str.upper()
        # Nettoyage du libelle
        replace_values_ean = {
            ',': ' ',
            '&': ' ',
            '\+': ' ',
            r'\d+\.?\d*\s?(K?GR?)\b': ' #POIDS ',
            r'\d+\.?\d*\s?(C?MM?)\b': ' #DIMENSION ',
            r'\d+\.?\d*\s?([CM]?L)\b': ' #VOLUME ',
            r'\d+\.?\d*\s?(%)\b': ' #POURCENTAGE ',
            r'\d+\.?\d*\s?(X|\*)\b': ' #LOT ',
            r'\d+\.?\d*\s?(X)\d\b': ' #LOT ',
            r'\d+\.?\d*\s?(CT)\b': ' #UNITE ',
            r'(\sX*S\b)|(\sM\b)|(\sX*L\b)': ' #TAILLE ',
            r'\s\d{2,}\/\d{2,}\b': ' #TAILLE ',
            '&AMP': ' ',
            r'\s\d+\b': ' ',
            r'^\d+ ': '',
            }
        input_data.replace({"libelle": replace_values_ean}, regex=True, inplace=True)
        input_data.replace({"libelle": {r'([ ]{2,})': ' '}}, regex=True, inplace=True) # Suppression des espaces multiples
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
