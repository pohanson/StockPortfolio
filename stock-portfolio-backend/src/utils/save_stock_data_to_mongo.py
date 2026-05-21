"""Run the file to port the stock data into the mongo database,
assuming that the mongod server is already running"""

import numpy as np
import pandas as pd
import pymongo

if __name__ == "__main__":
    df = pd.read_csv("./data/stocksListings.csv")
    df = df.loc[:, ["Trading Name", "Trading Code", "RIC", "Sector"]]
    df = df.replace(np.nan, None)

    client = pymongo.MongoClient()
    coll = client.data.stock_data
    coll.delete_many({})
    for d in df.T.to_dict().values():
        coll.insert_one(
            {
                "_id": d["Trading Code"],
                "TradingName": d["Trading Name"],
                "TradingCode": d["Trading Code"],
                "RIC": d["RIC"],
                "Sector": d["Sector"],
            }
        )
