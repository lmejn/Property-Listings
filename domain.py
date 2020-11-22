import requests
from requests.auth import HTTPBasicAuth
import time
import pandas as pd


class DomainAPI():

    def __init__(self, client_id, client_secret):
        self.access_token = self.get_access_token(client_id, client_secret)

        self.auth = {"Authorization": "Bearer " + self.access_token}

        self.total_n_queries = 0

    def get_access_token(self, client_id, client_secret):
        data = {"client_id": client_id,
                "client_secret":client_secret,
                "grant_type":"client_credentials",
                "scope":"api_listings_read",
                "Content-Type":"text/json"}

        r = requests.post('https://auth.domain.com.au/v1/connect/token', data=data)
        if(r.ok):
            token=r.json()
            return token["access_token"]
        print(r.reason)
        return None


    def find_listings(self, search_params):
        url = "https://api.domain.com.au/v1/listings/residential/_search"

        if("pageSize" not in search_params):
            search_params["pageSize"] == 100
        
        r = requests.post(url, headers=self.auth, json=search_params)
        self.total_n_queries += 1
        time.sleep(1)

        if(r.ok):
            return r.json()
        print(r.reason)
        return None

    def find_all_listings(self, search_params, max_no_pages=4, page_size=100, verbose=False):

        if(page_size > 100):
            print("Domain has max of 100 entries per page, limiting to page size of 100")

        search_params["pageSize"] = min(page_size, 100)

        data = []
        for page_number in range(1, max_no_pages):
            if(verbose):
                print(f"Page {page_number}: ", end="")

            search_params["pageNumber"] = page_number
            new_data = self.find_listings(search_params)
            if(new_data is None):
                break

            data += new_data
            
            if(verbose):
                print(f"{len(new_data)} listings found")

            if(len(new_data) < page_size):
                break
        return data


def to_dict(entry):
    
    listing = entry['listing']
    
    data = {}
    
    data['id'] = listing['id']
    data['price/details'] = listing['priceDetails']['displayPrice']
    
    property_details = listing['propertyDetails']
    
    for s in property_details['features']:
        data["feature/" + s] = True
        
    data['type'] = property_details['propertyType']
    
    for s in ['bathrooms', 'bedrooms', 'carspaces']:
        if(s in property_details):
            data[s] = property_details[s]
            
    for s in ['unitNumber', 'streetNumber', 'street',
              'area', 'region', 'suburb', 'postcode',
              'displayableAddress','latitude', 'longitude', 'landArea']:
        if(s in property_details):
            data['location/'+s] = property_details[s]
        
    return data
