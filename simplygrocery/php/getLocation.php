<?php

// Global Variables
$client_id = 'YOUR_KROGER_CLIENT_ID';
$client_secret = 'YOUR_KROGER_CLIENT_SECRET';

$credentials = base64_encode("$client_id:$client_secret");

function getAccessToken($credentials, $scope) {
    // Define the API endpoint for obtaining the token
    $token_url = 'https://api.kroger.com/v1/connect/oauth2/token';

    // Define the request payload
    $data = [
        'grant_type' => 'client_credentials',
        'scope' => $scope
    ];

    // Define the headers
    $headers = [
        'Content-Type: application/x-www-form-urlencoded',
        'Authorization: Basic ' . $credentials
    ];

    // Send the POST request to obtain the access token
    $response = http_post($token_url, http_build_query($data), implode("\r\n", $headers));

    // Check the response
    if ($response) {
        // Request successful, parse the JSON response
        $token_data = json_decode($response, true);
        $access_token = $token_data['access_token'];
        // echo 'Access Token:', $access_token;
        return $access_token;
    } else {
        echo 'Error:', $response;
    }
}

function getLocations($zipcode) {
    global $credentials;

    $location_url = "https://api.kroger.com/v1/locations?filter.zipCode.near=$zipcode&filter.radiosInMiles=10";
    $location_access_token = getAccessToken($credentials, '');

    $location_headers = [
        "Authorization: Bearer $location_access_token",
        "Cache-Control: no-cache"
    ];

    $location_response = http_get($location_url, implode("\r\n", $location_headers));

    if ($location_response) {
        // Request successful, parse the JSON response
        $location_data = json_decode($location_response, true);
        // echo 'Location data: ', print_r($location_data, true);

        // Assuming $location_data is the variable containing the JSON data
        $locations = $location_data["data"];

        // Initialize empty arrays to store extracted values
        $location_ids = [];
        $addresses = [];

        // Iterate through each location
        foreach ($locations as $location) {
            // Extract locationId and addressLine1
            $location_id = $location["locationId"];
            $address_line1 = $location["address"]["addressLine1"];

            // Append values to the arrays
            echo "$location_id, $address_line1\n";
        }
    } else {
        echo 'Error:', $location_response;
    }
}

// Function to make a POST request
function http_post($url, $data, $headers) {
    $context = stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => $headers,
            'content' => $data,
        ]
    ]);

    return file_get_contents($url, false, $context);
}

// Function to make a GET request
function http_get($url, $headers) {
    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'header' => $headers,
        ]
    ]);

    return file_get_contents($url, false, $context);
}

// Get the zipcode from the JavaScript side
$zipcode = $_POST['zipcode'];

// Run the function with the provided zipcode
getLocations($zipcode);
?>
