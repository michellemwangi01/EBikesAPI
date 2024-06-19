# Distance Calculation API

This API calculates the distance between two geographic coordinates using the Google Distance Matrix API and returns the delivery price based on the calculated distance.

## Endpoint: Calculate Distance

`URL: /google_api/calculate-distance/`
Method: POST
Permissions: Open to all (AllowAny)

Request Headers
Ensure that the request contains the following headers:
Content-Type: application/json

## Body Parameters

Parameter Type Description

1. origin_lat float Latitude of the origin
2. origin_long float Longitude of the origin
3. destination_lat float Latitude of the destination
4. destination_long float Longitude of the destination

JSON
`{  "origin_lat": -1.3433182103402546,  "origin_long": 6.76600758309724,  "destination_lat": -1.3913519108241854,  "destination_long": 36.76051708309745}`

### Response

Successful Response (200 OK)
Returns the delivery price based on the calculated distance.
`{   "delivery_price": 225.0}`

### Error Responses

400 Bad Request: Missing required parameters.
`{  "error": "Missing required parameters"}`

500 Internal Server Error: Error from the Google API or invalid response structure.
` { "error": "Error from Google API"}`

` {  "error": "Invalid response from Google API"}`

## How to Use with Postman

1. Open Postman.
2. Create a new request.
3. Set the request method to POST.
4. Enter the URL: http://127.0.0.1:8000/google_api/calculate-distance/
5. Go to the Headers tab and add a new header:
   Key: Content-Type
   Value: application/json
   Go to the Body tab, select raw, and ensure JSON is selected from the dropdown.
   Enter the request body with the required parameters. (See Example Request Body)
   Send the request.
   Check the response in the Postman console.
   Example Usage
   Here is an example URL for a local development server:

`http://127.0.0.1:8000/google_api/calculate-distance/`

For example, to calculate the distance and delivery price between Point A and Point B:

`{"origin_lat": -1.3433182103402546,"origin_long": 36.6600758309724,"destination_lat": -1.3913519108241854,"destination_long": 36.76051708309745}`
