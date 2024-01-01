# v2.1.1
# Powered By Gearheart Studios

import requests
import base64
import json
import re

from statistics import mode

#Global Variables

Kroger_Client_ID = 'KROGER_CLIENT_ID'
Kroger_Client_Secret = 'KROGER_CLIENT_SECRET'
Kroger_Credentials = base64.b64encode(f'{Kroger_Client_ID}:{Kroger_Client_Secret}'.encode('utf-8')).decode('utf-8')
Kroger_Location_ID = 'KROGER_LOCATION_ID_OPTIONAL'
Kroger_Location_Name = 'None Found'
Grocery_List = []
Grocery_List_Data = []
Grocery_Item_Name = 0
Kroger_Item_Comments = 0

Trello_Api_Key = 'TRELLO_API_KEY'
Trello_Api_Token = 'TRELLO_API_TOKEN'
Trello_Api_Secret = 'TRELLO_API_SECRET'
Trello_Board_ID = 'TRELLO_BOARD_ID'
Trello_List_ID = 'TRELLO_LIST_ID'

#Get Kroger Access Token
def getKrogerAcessToken(scope):

    get_token_url = 'https://api.kroger.com/v1/connect/oauth2/token'


    if scope != 'none':
        data = {
          'grant_type': 'client_credentials',
          'scope': scope
        }
    else:
        data = {
          'grant_type': 'client_credentials',
        }
        
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {Kroger_Credentials}'
    }
    
    response = requests.post(get_token_url, headers=headers, data=data)
    if response.status_code == 200:
        access_token_data = response.json()
        access_token = access_token_data.get('access_token')
        return access_token
    else:
        print('Error while obtaining acess token:', response.status_code, response.text)

def getKrogerLocationDetails(location_id):
    location_url = f'https://api.kroger.com/v1/locations/{location_id}'
    access_token = getKrogerAcessToken('none')

    location_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    location_response = requests.get(location_url, headers=location_headers)

    if location_response.status_code == 200:
        response = location_response.json()
        if "data" in response and "address" in response["data"]:
            address_info = response["data"]["address"]
            name = address_info.get("addressLine1", "")
            return name
    else:
        print('Error:', location_response.status_code, location_response.text)

def getKrogerProductDetails(items):
    base_product_url = 'https://api.kroger.com/v1/products'
    product_access_token = getKrogerAcessToken('product.compact')
    
    for item in items:
        parts = item.split(", ")
        item_name = None
        item_notes = None
        item_card_id = None
        aisle_values = []
        for part in parts:
            if ": " in part:
                key, value = part.split(": ", 1)  # Split only once
                if key.strip() == "comments": 
                    item_notes = value.strip() if value.strip() != '' else "None"
                elif key.strip() == "product_name":
                    item_name = value.strip() if value.strip() != '' else "None"
                elif key.strip() == "card_id":
                    item_card_id = value.strip() if value.strip() != '' else "None"
        print(f"Searching item {item_name}...")

        product_url = f'{base_product_url}?filter.term={item_name}&filter.locationId={Kroger_Location_ID}'

        product_headers = {
                'Authorization': f'Bearer {product_access_token}',
                'Cache-Control': 'no-cache'   
        }

        product_response = requests.get(product_url, headers=product_headers)
        if product_response.status_code == 200:
            product_data = product_response.json()       
            for item_data in product_data['data']:
                aisle_locations = item_data.get('aisleLocations', [])
                for aisle_location in aisle_locations:
                    description = aisle_location.get('description')
                    # Try to find an integer in the description
                    match = re.search(r'\d+', description)
                    if match:
                        aisle_value = int(match.group(0))
                    else:
                        # If no integer is found, look for a string
                        match = re.search(r'\b\w+\b', description)
                        if match:
                            aisle_value = match.group(0)
                        else:
                            aisle_value = None  # No integer or string found
                            print(f"No aisle found for {item_name}")
                    aisle_values.append(aisle_value)
            try:
                if aisle_values:
                    Grocery_List_Data.append(f'comments: {item_notes}, product_name: {item_name}, location: {mode(aisle_values)}, id: {item_card_id}')
                if not aisle_values:
                    Grocery_List_Data.append(f'comments: {item_notes}, product_name: {item_name}, location: NONE, id: {item_card_id}')
            except:
                print('Couldnt Add To List Grocery_Data_List')
        else:
            print(f'Error {product_response.status_code} with message {product_response.text}')
    product_location_file_name = './product_locations.json'
    with open (product_location_file_name, "w") as json_file:
        json.dump(Grocery_List_Data, json_file, indent=4)
    print(f'File saved as {product_location_file_name}')


def custom_sort_key(item):
    parts = item.split(", ")
    for part in parts:
        if ": " in part:
            key, value = part.split(": ", 1)
            if key.strip() == "location":
                location_value = value.strip() if value.strip() != '' else "None"
    try:
        return int(location_value)
    except:
        return float('inf')

def sortProductLocations():
    # Read the JSON data from the file
    with open('product_locations.json', 'r') as file:
        data = json.load(file)
    
    # Sort the data using the custom key function
    sorted_data = sorted(data, key=custom_sort_key)
    
    # Write the sorted data back to the file
    with open('product_locations.json', 'w') as file:
        json.dump(sorted_data, file, indent=4)
    
    print("Data sorted and saved to product_locations.json")

def getItemCards():
    base_url = "https://api.trello.com/1/lists/{}/cards".format(Trello_List_ID)
    params = {
        "key": Trello_Api_Key,
        "token": Trello_Api_Token,
    }
    # Send a GET request to the Trello API to fetch cards in the list
    response = requests.get(base_url, params=params)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        cards = response.json()
        # Extract card names and append them to the 'items' list
        for card in cards:
            card_name = card["name"]
            if '<GS>' in card_name:
                parts = card_name.split(", ")
                product_name = None
                comments_data = None
                id_data = card["id"]
                for part in parts:
                    if ": " in part:
                        key, value = part.split(": ", 1)
                        if key.strip() == "Name":
                            product_name = value.strip() if value.strip() != '' else "None"
                        elif key.strip() == "Notes":
                            comments_data = value.strip() if value.strip() != '' else "None"
                        
                Grocery_List.append(f' comments: {comments_data}, product_name: {product_name}, card_id: {id_data}')
            else:
                if '#' in card_name:
                    card_comments = card_name.split('#')[1].strip()
                    card_item = card_name.split('#')[0].strip()
                else:
                    card_comments = None
                    card_item = card_name

                card_id = card["id"]
                Grocery_List.append(f'comments: {card_comments}, product_name: {card_item}, card_id: {card_id}')
    else:
        print("Error fetching cards from Trello. Status code:", response.status_code)
        
def writeToTrello():
    BASE_URL = 'https://api.trello.com/1/cards'
    
    # Open the file and read its lines
    with open('./product_locations.json', 'r') as file:
        data = json.load(file)
    for entry in data:
        parts = entry.split(", ")
        product_name = None
        location_value = None
        comments_data = None
        id_data = None
        for part in parts:
            if ": " in part:
                key, value = part.split(": ", 1)  # Split only once
                if key.strip() == "product_name":
                    product_name = value.strip() if value.strip() != '' else "None"
                elif key.strip() == "location":
                    location_value = value.strip() if value.strip() != '' else "None"
                elif key.strip() == "comments":
                    comments_data = value.strip() if value.strip() != '' else "None"  # Set to "None" if empty
                elif key.strip() == "id":
                    id_data = value.strip() if value.strip() != '' else "None"

        card_data = {
            'name': f'{location_value}, Name: {product_name}, Notes: {comments_data}, |<GS>',
            'desc': '',
            'idList': Trello_List_ID,
            'key': Trello_Api_Key,
            'token': Trello_Api_Token
        }
        delete_data = {
            "key": Trello_Api_Key,
            "token": Trello_Api_Token,
        }
        response = requests.post(BASE_URL, data=card_data)
        if response.status_code == 200:
            created_card = response.json()
            print(f"Card '{created_card['name']}' created successfully.")
            
            delete_url = f"https://api.trello.com/1/cards/{id_data}"
            delete_response = requests.delete(delete_url, params=delete_data)
            if delete_response.status_code == 200:
                print(f'Delete card {product_name} with id {id_data}')
            else:
                print(f'Failed to delete the card. Status code: {delete_response.status_code}')
        else:
            print(f"Failed to create the card. Status code: {response.status_code}")
    
    changeTrelloListName(f'Location: {Kroger_Location_Name} || gearheartstudios.com/simplygrocery')
            
def changeTrelloListName(Message):
    LIST_URL = f'https://api.trello.com/1/lists/{Trello_Board_ID}'
    
    list_data = {
        'key': Trello_Api_Key,
        'token': Trello_Api_Token,
        'name': Message
    }

    response = requests.put(LIST_URL, data=list_data)
    
    if response.status_code == 200:
        print(f"List name changed.")
    else:
        print(f"Failed to change name. Status code: {response.status_code}")

def getVars():
    with open('./variables/variables.json', 'r') as file:
        data = json.load(file)
        for entry in data:
            parts = entry.split(", ")
            location_var = None
            for part in parts:
                if ": " in part:
                    key, value = part.split(": ", 1)  # Split only once
                    if key.strip() == "Location":
                        location_var = value.strip()
    return(location_var)

def getLocationDetails():
    location_url = f'https://api.kroger.com/v1/locations/{Kroger_Location_ID}'
    access_token = getKrogerAcessToken('none')

    location_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    location_response = requests.get(location_url, headers=location_headers)

    if location_response.status_code == 200:
        response = location_response.json()
        if "data" in response and "address" in response["data"]:
            address_info = response["data"]["address"]
            name = address_info.get("addressLine1", "")
            return name
    else:
        print('Error:', location_response.status_code, location_response.text)
        

Kroger_Location_ID = getVars()
Kroger_Location_Name = getLocationDetails()
getItemCards()
getKrogerProductDetails(Grocery_List)
sortProductLocations()
writeToTrello()
