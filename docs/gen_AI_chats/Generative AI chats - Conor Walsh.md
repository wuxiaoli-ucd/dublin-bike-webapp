**Generative AI chats \- Conor Walsh**

I used ChatGPT as a tool to understand some unfamiliar concepts encountered during the project, where I was unable to sufficiently learn about them in other ways.

Curl command

- How curl command works and how it could be used to test Flask API endpoints directly from the command line before we had a working frontend. This was used to test station and weather endpoints in Sprint 1\. 

Project structure and backend organisation 

- Learned about best practices for structuring a Flask-based application i.e., what should go in app/services and app/routes

Routing logic for journey planner

- Assisted in reasoning through complex routing scenarios where walk and cycle segments were combined 

Rendering routes using Google Maps encoded polylines

- Learned how to decode and render encoded polylines returned from the Google Routes API

Google API integration details

- Clarified the use of required headers (e.g., X-Goog-Api-Key) and request formatting for interacting with Google Maps

Frontend architecture

- How to structure a large [index.js](http://index.js) file, i.e., defining functions and calling them in initMap()

Handling date and time inputs

- For learning to implement “Depart At” functionality, working with date/time inputs and formatting for backend requests

Using localStorage in JS

- How localStorage can save simple user metrics across refreshes in the browser. This was used in the dropdown menu. 

Setting up cron on EC2

- How cron could be used to collect weather data for multiple days on an instance of EC2

Asynchronous data fetching and error handling

- How to structure async/await calls and handle API errors in the frontend

Chart rendering with [Chart.js](http://Chart.js)

- Structuring data and updating chart dynamically for predicted availability

Small UI improvements

- Was used to learn about ways to implement a custom hover tooltip for each station 

