<?php
// Check if the request is a POST request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Define the URL and authorization token
    $url = 'YOUR_PYTHON_HOST_WEBSITE_ENDPOINT';
    $auth_token = 'YOUR_API_KEY_FOR_YOUR_PYTHON_FLASK_SERVER_API'; // Replace with your actual token

    // Get the JSON data sent in the request
    $json_data = file_get_contents('php://input');
    $data = json_decode($json_data);

    if ($data !== null && isset($data->locationId)) {
        // Define the request headers
        $headers = array(
            'Authorization: Bearer ' . $auth_token,
            'Content-Type: application/json' // Specify JSON content type
        );

        // Create the data array with the locationId
        $apiData = array('location' => $data->locationId);

        // Initialize cURL session
        $ch = curl_init($url);

        // Set cURL options
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($apiData)); // Encode the data as JSON

        // Execute the cURL session
        $response = curl_exec($ch);

        // Close the cURL session
        curl_close($ch);

        // Check if the request was successful
        if ($response !== false) {
            // Display the response data
            echo $response;
        } else {
            // Handle errors here
            echo 'Error occurred. No idea why.';
        }
    } else {
        echo 'Invalid data received. This is another issue I have no idea what means. Something went wrong do it again.';
    }
} else {
    // Handle non-POST requests (optional)
    echo 'Invalid request method. Not a POST but I dont know how to fix this on user side.';
}
?>
