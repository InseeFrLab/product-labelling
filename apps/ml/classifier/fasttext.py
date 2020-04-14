
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

#subprocess.call('cd apps/ml/classifier/fastText && python3 -m pip install -q fasttext && cd ', shell=True)
import fasttext

class FasttextClassifier:
    def __init__(self):
        path_to_artifacts = "research/"
        self.model = fasttext.load_model(path_to_artifacts + "fasttext.bin")
        
    def preprocessing(self, input_data):
        
        # JSON to pandas DataFrame
        input_data = pd.DataFrame(input_data, index=[0])
        
        replace_values_ean = {',' : ' ', '&' : ' ','\+':' ',r'\d+\.?\d*([CM]?[LM]|CT|GR?|KG|X|\*|%)': ' ',r' \d+ ': ' ',r'^\d+ ':''} 
        input_data.replace({"libelle": replace_values_ean},regex=True,inplace=True)
        input_data.replace({"libelle": {r'([ ]{2,})': ' '}}, inplace=True, regex=True)
        #input_data['libelle'].to_csv('predict.txt',header=False,index=False,encoding="utf-8")     
        input_data=input_data['libelle'][0]
        return input_data.upper()
        
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
