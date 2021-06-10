# UOCIS322 - Project 7 #
Author: Kaetlyn Gibson

Contact Address: kaetlyng@uoregon.edu

## Overview
Brevet time calculator with AJAX, MongoDB, and a RESTful API! Adding authentication and user interface to brevet time calculator service.

### Background
What are brevets? Brevets are timed rides with controls. Controls are points where a rider must obtain proof of passage, and controle times are the minimum and maximum times by which the rider must arrive at the location.

### The Algorithm
To calculate the opening time, we divide the distance of the control point(in km) by the maximum speed(in km/hr) designated by the location of the control. To calculate the closing time, we divide the distance of the control point(in km) by the minimum speed(in km/hr) designated by the location of the control. Of course, it is slightly more complicated than this, so I recommend taking a look at the examples from here: https://rusa.org/pages/acp-brevet-control-times-calculator.

### Time Calculation
Dividing the distance in kilometers by speed of kilometers per hour results in a time
in hours. To convert into hours and minutes, subtract the whole number of hours and multiply the resulting fractional part by 60. Times are rounded to the nearest minute.

### Tasks

#### Part 1: Authenticating the services 

- POST **/register**

Registers a new user. On success a status code 201 is returned. The body of the response contains a JSON object with the newly added user. On failure status code 400 (bad request) is returned. Note: The password is hashed before it is stored in the database. Once hashed, the original password is discarded. Your database should have three fields: id (unique index), username and password for storing the credentials.

- GET **/token**

Returns a token. This request must be authenticated using a HTTP Basic Authentication (see `DockerAuth/password.py` and `DockerAuth/testToken.py`). On success a JSON object is returned with a field `token` set to the authentication token for the user and a field `duration` set to the (approximate) number of seconds the token is valid. On failure status code 401 (unauthorized) is returned.

- GET **/RESOURCE-YOU-CREATED-IN-PROJECT-6**

Return a protected <resource>, which is basically what you created in project 6. This request must be authenticated using token-based authentication only (see `DockerAuth/testToken.py`). HTTP password-based (basic) authentication is not allowed. On success a JSON object with data for the authenticated user is returned. On failure status code 401 (unauthorized) is returned.

#### Part 2: User interface

The goal of this part of the project is to create frontend/UI for Brevet app using Flask-WTF and Flask-Login introduced in lectures. You frontend/UI should use the authentication that you created above. In addition to creating UI for basic authentication and token generation, you will add three additional functionalities in your UI: a) registration, b) login, c) remember me, d) logout.

## Usage
- Build/run using docker-compose: 
  ```
  docker-compose up -d --build
  ```
- To use the brevet calculator:
  - Launch `http://7777:5000` using web browser
  - Choose a brevet distance
  - Choose begin date and time
  - Enter controle locations in km or miles
  - Submit, to submit values (message will appear if successful)
  - Display, to display values on another page
- Launch `http://7779:5000` using web browser
- Register
- Login
- To view outputs via website @ "Secret" tab:
  - Select desired from the following:
    - From APIs:
      - listAll
      - listOpenOnly
      - listCloseOnly
    - From result representation:
      - Table (extra)
      - CSV
      - JSON (default)
    - View top k results, or not
  - Submit choices using `Get Times`

## Credits

Michal Young, Ram Durairajan, Steven Walton, Joe Istas.

The algorithm, described by RUSA: https://rusa.org/pages/acp-brevet-control-times-calculator

The original calculator: https://rusa.org/octime_acp.html

Additional background: https://rusa.org/pages/rulesForRiders

