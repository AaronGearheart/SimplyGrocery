<?php
// Check if the request is a POST request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Define the URL and authorization token
    $url = 'YOUR_PYTHON_HOST_WEBSITE_ENDPOINT';
    $auth_token = 'YOUR_API_KEY_FOR_YOUR_PYTHON_FLASK_SERVER_API'; // Replace with your actual token

    // Define the request headers
    $headers = array(
        'Authorization: Bearer ' . $auth_token,
        'Content-Type: application/json' // Assuming you are sending JSON data
    );

    // Define the data to send in the request (if needed)
    $requestData = array(); // You can add data here if required

    // Initialize cURL session
    $ch = curl_init($url);

    // Set cURL options
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($requestData)); // You can adjust this as needed

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
        echo 'Error occurred.';
    }
} else {
    // Handle non-POST requests (optional)
    echo 'Invalid request method';
}
?>
