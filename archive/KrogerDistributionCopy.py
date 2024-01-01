###################################
#                                 #
# Trello To Kroger Aisle Numbers  #
#     Code By Aaron Gearheart     #
# Powered By GearheartStudios.com #
#                                 #
###################################


import requests
import base64
import json
import re
import statistics

from statistics import mode

#Global Variables{
#Kroger Variables
client_id = 'YOUR_KROGER_API_CLIENT_ID'
client_secret = 'YOUR_KROGER_API_CLIENT_SECRETE'
credentials = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
location_id = 'YOUR_KROGER_LOCATION_ID'
items = []
name = 0
comments = 0

#Trello Variables
API_KEY = 'YOUR_TRELLO_API_KEY'
API_TOKEN = 'YOUR_TRELLO_API_TOKEN'
API_SECRET = 'YOUR_TRELLO_API_SECRET'
BOARD_ID = 'YOUR_TRELLO_BOARD_ID'
WRITE_LIST_ID = 'YOUR_TRELLO_LIST_ID_TO_WRITE_TO'
READ_LIST_ID = 'YOUR_TRELLO_LIST_ID_TO_READ_FROM'
#}


def getAccessToken(credentials, scope):
    # Define the API endpoint for obtaining the token
    token_url = 'https://api.kroger.com/v1/connect/oauth2/token'

    # Define the request payload
    if scope != 'none':
        data = {
          'grant_type': 'client_credentials',
          'scope': scope
        }
    else:
        data = {
          'grant_type': 'client_credentials',
        }

    # Define the headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {credentials}'
    }

    # Send the POST request to obtain the access token
    response = requests.post(token_url, headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        # Request successful, parse the JSON response
        token_data = response.json()
        access_token = token_data.get('access_token')
        return access_token
    else:
        print('Error:', response.status_code, response.text)
    
def getLocationDetails():
    location_url = f'https://api.kroger.com/v1/locations/{location_id}'
    access_token = getAccessToken(credentials, 'none')

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
    

def getProducts(items):
    base_product_url = 'https://api.kroger.com/v1/products'
    product_access_token = getAccessToken(credentials, 'product.compact')
    product_data_cache = []
    
    product_aisle_numbers = []
    #Repeat per item
    for item in items:
        #Strip comments
        comments = None
        if '#' in item:
            comments = item.split('#')[1].strip()
            item = item.split('#')[0].strip()
        # Construct the URL with the current item
        product_url = f'{base_product_url}?filter.term={item}&filter.locationId={location_id}'
        aisle_values = []

        # Define headers
        product_headers = {
            'Authorization': f'Bearer {product_access_token}',
            'Cache-Control': 'no-cache'   
        }
        # Make the GET request
        product_response = requests.get(product_url, headers=product_headers)
        # Check if the request was successful (status code 200)
        if product_response.status_code == 200:
            # Process the response data here (e.g., print it)
            product_data = product_response.json() #Parsed JSON
            product_data_cache.append(product_data) #Sending JSON data to cache
            # Iterate over the product data to extract aisle locations
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
                    aisle_values.append(aisle_value)
        try:
            product_aisle_numbers.append(f'comments: {comments}, product_name: {item}, location: {mode(aisle_values)}')
        except:
            pass
    product_location_file_name = 'product_locations.json'
    with open (product_location_file_name, "w") as json_file:
        json.dump(product_aisle_numbers, json_file, indent=4)
    print(f'File saved as {product_location_file_name}')

def custom_sort_key(item):
    try:
        # Extract the numeric value from the string
        location_value = int(item.split(':')[-1].strip())
        return location_value
    except ValueError:
        print(item)
        # For non-numeric values, return a high value to push them to the end
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

def writeToTrello():
    BASE_URL = 'https://api.trello.com/1/cards'
    LIST_URL = f'https://api.trello.com/1/lists/{WRITE_LIST_ID}'


    # Open the file and read its lines
    with open('product_locations.json', 'r') as file:
        data = json.load(file)
    
    for entry in data:
        parts = entry.split(", ")
        product_name = None
        location_value = None
        comments_data = None  # Initialize comments_data
        for part in parts:
            if ": " in part:
                key, value = part.split(": ", 1)  # Split only once
                if key.strip() == "product_name":
                    product_name = value.strip()
                elif key.strip() == "location":
                    location_value = value.strip()
                elif key.strip() == "comments":
                    comments_data = value.strip() if value.strip() != '' else "None"  # Set to "None" if empty

        card_data = {
            'name': f'{location_value}, {product_name}, Notes: {comments_data}',
            'desc': '',
            'idList': WRITE_LIST_ID,
            'key': API_KEY,
            'token': API_TOKEN
        }

        response = requests.post(BASE_URL, data=card_data)

        # Check if the request was successful
        if response.status_code == 200:
            created_card = response.json()
            print(f"Card '{created_card['name']}' created successfully.")
        else:
            print(f"Failed to create the card. Status code: {response.status_code}")
    list_data = {
        'key': API_KEY,
        'token': API_TOKEN,
        'name': f'Aisle Locations List (Currently {total_items} items) Location: {name})'
    }

    response = requests.put(LIST_URL, data=list_data)
    if response.status_code == 200:
        print(f"List name changed.")
    else:
        print(f"Failed to change name. Status code: {response.status_code}")

def getItemCards():
    global total_items
    total_items = 0

    base_url = "https://api.trello.com/1/lists/{}/cards".format(READ_LIST_ID)

    params = {
        "key": API_KEY,
        "token": API_TOKEN,
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
            items.append(card_name)
            total_items += 1
    else:
        print("Error fetching cards from Trello. Status code:", response.status_code)

def purgeCards():
    base_url = "https://api.trello.com/1/lists/{}/cards".format(WRITE_LIST_ID)

    params = {
        "key": API_KEY,
        "token": API_TOKEN,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        # Parse the JSON response
        cards = response.json()
        # Extract card names and append them to the 'items' list
        for card in cards:
            card_id = card["id"]
            
            delete_url = "https://api.trello.com/1/cards/{}".format(card_id)
            delete_response = requests.delete(delete_url, params=params)
            if delete_response.status_code == 200:
                print("Deleted card with ID:", card_id)
            else:
                print("Error deleting card with ID:", card_id, "Status code:", delete_response.status_code)
            
    else:
        print("Error fetching cards from Trello. Status code:", response.status_code)

try:
    name = getLocationDetails()
    print(f"Using location ID {location_id} at {name} location")
    step = 'purgeCards'
    purgeCards()
    step = 'getItemCards'
    getItemCards()
    step = 'getProducts'
    getProducts(items)
    step = 'sortProductLocations'
    sortProductLocations()
    step = 'writeToTrello'
    writeToTrello()
    step = 'Waiting between runs'
    step = 'Resetting'
except KeyboardInterrupt:
    print(f'Stopped by user at step {step}')
