from domain import DomainAPI, to_dict

import json, os
import pandas as pd

with open("config.json", 'r') as file:
    config = json.load(file)

api = DomainAPI(config["credentials"]["id"], config["credentials"]["secret"])

def get_listings(api):

    with open("config.json", 'r') as file:
        config = json.load(file)


    search_params = {
        "listingType": "Sale",
        "propertyTypes": config["propertyTypes"],
        "locations": config["locations"]
    }

    data = api.find_all_listings(search_params, verbose=True)

    df = pd.DataFrame([to_dict(d) for d in data if "listing" in d])

    df['Date Added'] = pd.to_datetime(pd.to_datetime('now').strftime('%Y-%m-%d'))

    df.set_index('id', inplace=True, drop=True)
    # del df['íd']

    return df

new_listings = get_listings(api)

listings_filename = "listings.csv"

if(not os.path.exists(listings_filename)):
    new_listings.to_csv(listings_filename)

else:
    old_listings = pd.read_csv(listings_filename, index_col=0)
    listings = pd.concat([old_listings, new_listings]).drop_duplicates()

    listings.to_csv(listings_filename)
