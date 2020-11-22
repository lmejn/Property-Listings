from domain import DomainAPI, to_dict

import json, os
import pandas as pd

def load_config():
    with open("config.json", 'r') as file:
        config = json.load(file)
    return config


def load_api():
    config = load_config()
    return DomainAPI(config["credentials"]["id"], config["credentials"]["secret"])


def _get_listings(api, search_params):

    data = api.find_all_listings(search_params, verbose=True)

    df = pd.DataFrame([to_dict(d) for d in data if "listing" in d])
    # df.set_index('id', inplace=True, drop=True)

    return df


def get_listings(api):

    config = load_config()

    search_params = {
        "listingType": "Sale",
        "propertyTypes": config["propertyTypes"],
        "locations": config["locations"]
    }

    df = _get_listings(api, search_params)
    df['Date Added'] = pd.to_datetime(pd.to_datetime('now').strftime('%Y-%m-%d'))

    return df


def get_listings_in_price_range(api, min_price=None, max_price=None):

    config = load_config()

    search_params = {
        "listingType": "Sale",
        "propertyTypes": config["propertyTypes"],
        "locations": config["locations"],
    }
    
    if(min_price is not None):
        search_params['minPrice'] = int(min_price)

    if(max_price is not None):
        search_params['maxPrice'] = int(max_price)

    return _get_listings(api, search_params)


if __name__ == "__main__":

    api = load_api()

    new_listings = get_listings(api)

    listings_filename = "listings.csv"

    if(not os.path.exists(listings_filename)):
        new_listings.to_csv(listings_filename)

    else:
        old_listings = pd.read_csv(listings_filename, index_col=0)
        listings = pd.concat([old_listings, new_listings])

        listings = listings[~listings.index.duplicated(keep="first")]

        listings.to_csv(listings_filename)
