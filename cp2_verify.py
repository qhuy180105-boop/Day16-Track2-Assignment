import lightgbm
import sklearn
import pandas as pd
import numpy as np

print("Imports: OK")

import os
data_path = "data/creditcard.csv" if os.path.exists("data/creditcard.csv") else "creditcard.csv"
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    print("Shape:", df.shape)
    print("Missing:", int(df.isna().sum().sum()))
    print("Class counts:", df["Class"].value_counts().to_dict())
