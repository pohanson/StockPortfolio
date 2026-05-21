"""Run the file to generate a json file containing objects with
keys being the stock code, and the value the corresponding stock name"""

import json

import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("./data/stocksListings.csv", index_col="Trading Code")
    df = df.loc[:, ["Trading Name"]]
    data = df.to_dict()["Trading Name"]
    print(json.dumps(data))
    with open("./stock_code_name.json", "w") as f:
        json.dump(data, f)
