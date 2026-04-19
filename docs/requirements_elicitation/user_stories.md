**List of User Stories and Acceptance Criteria**



**User Story 1 (Display Interactive Map):**  
As a user, I want to see an interactive map when I open the application, so that I can explore the Dublin area visually.

AC1 — Map Page Loads Successfully (Backend)

* Given the Flask server is running  
* When the user sends a request to the home page (e.g., GET /)  
* Then the system shall return the map page HTML successfully (HTTP 200).  
* Implementation: Flask route in app.py using @app.route(""/"") and render\_template(""map.html"")

AC2 – Deploy Flask App on EC2 (Backend)

* Given the Flask application is deployed on an AWS EC2 instance  
* When a client sends a request to the public API endpoint  
* Then the system shall respond with valid JSON data from the production database.


AC3 — Map Container is Displayed (Frontend)

* Given the user opens the map page  
* When the HTML is rendered in the browser  
* Then the system shall display a visible map container element (e.g., \<div id=""map""\>) on the page.  
* Implementation: map.html (HTML \+ CSS)

AC4 — Google Map Renders on Page Load (Frontend)

* Given the user has successfully opened the map page  
* When the Google Maps JavaScript API loads and the map initialization function is executed  
* Then the system shall render an interactive Google Map within the map container.  
* Implementation: map.html (Google Maps API script \+ JavaScript initialization function)

AC5 — Map Has a Default Initial View (Frontend)

* Given the map has been initialized  
* When the map is first displayed to the user  
* Then the system shall center the map on Dublin and apply a predefined default zoom level.  
* Implementation: JavaScript configuration inside the map initialization function (e.g., center and zoom settings in new google.maps.Map())

AC6 — Map Supports User Interaction (Frontend)

* Given the interactive map is displayed  
* When the user pans or zooms the map  
* Then the system shall update the visible map area accordingly without reloading the page.  
* Implementation: Google Maps built-in interaction (JavaScript in map.html)

**User Story 2 (Display current station data on a google map):**   
As a user, I want to see DublinBikes station markers on the map with up-to-date availability info, so that I can quickly find stations with bikes nearby.

AC1 — Station Data Is Collected and Stored Every 5 Minutes (Backend)

* Given the data collection service is running  
* When 5 minutes have elapsed since the last successful execution  
* Then the system shall fetch the latest station availability data and store it in the project database.  
* Implementation: Scheduled background script (e.g., cron job) \+ database insert/update logic.

AC2 — Stations Within Current Map Bounds Are Returned as JSON (Backend)

* Given the database contains station availability records  
* When the client requests station data with map bounds parameters (north, south, east, west)  
* Then the system shall return a JSON list of stations located within those bounds, including at least station id, name, latitude, longitude, available bikes, available stands, and last updated time.  
* Implementation: Flask route (e.g., GET /api/stations?north=...\&south=...\&east=...\&west=...) querying the database and returning jsonify(...).

AC3 — Single Station Detail Is Returned on Request (Backend)

* Given the database contains station availability records  
* When the client requests data for a specific station id，which means clicking on a station marker  
* Then the system shall return the latest available bikes and available stands for that station in JSON format.  
* Implementation: Flask route (e.g., GET /api/station/\<id\>) querying the database and returning jsonify(...).

AC4 — Backend Service Is Deployed and Accessible via EC2(Backend)

* Given the Flask application is deployed on an AWS EC2 instance  
* When a client sends a request to the public API endpoint  
* Then the system shall respond with valid JSON data from the production database.

AC5 — Markers Are Rendered on Initial Map Load (Frontend)

* Given the user opens the map page and the map is displayed  
* When the map becomes ready and its visible bounds are available  
* Then the system shall request station data for the current viewport and render markers for the returned stations at the correct latitude and longitude.  
* Implementation: JavaScript in map.html using map.getBounds() and fetch('/api/stations?...') followed by new google.maps.Marker(...).

AC6 — Marker Displays Available Bikes Count (Frontend)

* Given station data has been received  
* When a station marker is created  
* Then the system shall display the available bikes count on the marker.  
* Implementation: JavaScript marker label or custom marker rendering in map.html.

AC7 — Marker Color Indicates Availability Using Two-Level Threshold (Frontend)

* Given the available bikes count is known for a station  
* When the station marker is rendered  
* Then the system shall apply a visual indicator such that:  
* the marker is green when available\_bikes ≥ 2  
* the marker is yellow when available\_bikes \< 2  
* Implementation: JavaScript logic in map.html selecting marker icon or color based on the defined threshold.

AC8 — Markers Reload When the Map View Changes (Frontend)

* Given station markers are displayed on the map  
* When the user pans or zooms the map and the map becomes idle  
* Then the system shall request updated station data for the new visible area and refresh the displayed markers without reloading the page.  
* Implementation: JavaScript event listener for Google Maps idle event \+ marker refresh logic.

AC9 — Marker Availability Updates Automatically While Page Is Open (Frontend)

* Given the user keeps the map page open  
* When a defined refresh interval elapses (e.g., every 60 seconds)  
* Then the system shall request the latest station data for the current viewport and update marker labels and colors without reloading the page.  
* Implementation: JavaScript setInterval() calling the stations API and updating existing markers.

AC10 — Clicking a Marker Opens the Station Detail Panel (Frontend)

* Given station markers are displayed on the map  
* When the user clicks on a station marker  
* Then the system shall open a side panel or popup for station details.  
* Implementation: JavaScript marker click listener updating the DOM.

AC11 — Station Detail Panel Displays Latest Bikes and Stands (Frontend)

* Given the station detail panel is open for a selected station  
* When the frontend receives station detail data from the backend  
* Then the system shall display the selected station’s available bikes and available stands in the panel.  
* Implementation: JavaScript fetch('/api/station/\<id\>') and DOM update logic in map.html.

**User Story 3 (Display Current Weather and Weather Forecast):**   
As a user, I want to see the current weather and temperature on the map page and view a short hourly forecast on demand, so that I can make better travel decisions.

AC1 — Current weather and hourly forecast are stored hourly and expired forecast data is removed (Backend)

* Given the scheduled weather collection script is running  
* When 1 hour has elapsed since the last successful execution  
* Then the system shall:  
* fetch current weather data from the weather API and store/update it in the RDS database, and  
* fetch hourly forecast data from the weather API and store/update only the next 3 forecast hours (+1h, \+2h, \+3h) in the RDS database, and  
* delete any stored hourly forecast records that are no longer within the required future window (i.e., expired forecast times), so the database does not grow unnecessarily.  
* Implementation: Python scheduled script (cron/EC2) \+ DB upsert \+ delete expired rows

AC2 — Latest current weather is returned as JSON (Backend)

* Given the database contains stored current weather records  
* When the client requests the latest current weather data  
* Then the system shall return the most recent current weather record in JSON format including at least:  
  * time\_local  
  * weather\_description  
  * temperature\_c (°C)  
  * wind\_kmh (km/h)  
  * precip\_probability\_pct (%)  
  * icon\_code (for weather icon rendering)  
* Implementation: Flask route GET /api/weather/latest querying DB and returning jsonify(...)

AC3 — Next 3 hourly forecast entries are returned as JSON (Backend)

* Given the database contains stored hourly forecast records  
* When the client requests the hourly forecast  
* Then the system shall return exactly 3 forecast items in JSON format representing \+1h, \+2h, \+3h, and each item shall include at least:  
  * forecast\_time\_local  
  * Weather\_description  
  * temperature\_c (°C)  
  * wind\_kmh (km/h)  
  * precip\_probability\_pct (%)  
  * icon\_code  
* Implementation: Flask route GET /api/weather/forecast/hourly?count=3 querying DB and returning jsonify(...)

AC4 — Backend Service Is Deployed and Accessible via EC2(Backend)

* Given the Flask application is deployed on an AWS EC2 instance  
* When a client sends a request to the public API endpoint  
* Then the system shall respond with valid JSON data from the production database.

AC5 — Current weather summary with icon is displayed in the top-right (Frontend)

* Given the user opens the map page  
* When the page loads and the latest current weather data is available  
* Then the system shall display a weather summary in the top-right corner including:  
* a weather icon  
* Weather: \<description\>  
* Temperature: \<value\>°C  
* Implementation: map.html JavaScript fetch /api/weather/latest and render icon \+ summary

AC6 — Clicking the weather summary opens the forecast module (Frontend)

* Given the weather summary is displayed in the top-right corner  
* When the user clicks the weather summary area  
* Then the system shall show the weather forecast module in the left panel (bottom-left section).  
* Implementation: map.html JavaScript click handler \+ DOM show/hide

AC7 — Forecast module displays 4 complete weather entries (Frontend)

* Given the forecast module is visible  
* When the frontend receives current weather data and hourly forecast data  
* Then the system shall display exactly 4 entries labelled Now, \+1h, \+2h, \+3h, where:  
*   
* Now uses data from the current weather endpoint  
* \+1h, \+2h, \+3h use data from the hourly forecast endpoint  
* and each entry shall display:  
  * local time label  
  * weather icon \+ description  
  * temperature in °C  
  * wind speed in km/h  
  * precipitation probability in %  
* Implementation: map.html JavaScript fetch both endpoints and render 4 structured entries.

**User Story 4 (View Historical Occupancy):**  
As a user, I want to see hourly or daily occupancy data in a bar chart when I click on a station, so that I can understand usage patterns.

AC1 — Hourly historical occupancy for the last 8 hours is returned as aggregated data (Backend)

* Given the database contains stored station availability records  
* When the client requests hourly historical data for a selected station  
* Then the system shall return aggregated availability data for the past 8 hours, where:  
* each data point represents the average available bikes for one hour  
* exactly 8 data points are returned  
* the data is ordered chronologically  
* Implementation: Flask route (e.g., GET /api/station/\<id\>/history/hourly)  
* Database query using GROUP BY hour and AVG(available\_bikes)

AC2 — Daily historical occupancy for the last 7 days is returned as aggregated data (Backend)

* Given the database contains stored station availability records  
* When the client requests daily historical data for a selected station  
* Then the system shall return aggregated availability data for the past 7 days, where:  
* each data point represents the average available bikes for one day  
* exactly 7 data points are returned  
* the data is ordered chronologically  
* Implementation: Flask route (e.g., GET /api/station/\<id\>/history/daily)  
* Database query using GROUP BY date and AVG(available\_bikes)

AC3 — Backend Service Is Deployed and Accessible via EC2(Backend)

* Given the Flask application is deployed on an AWS EC2 instance  
* When a client sends a request to the public API endpoint  
* Then the system shall respond with valid JSON data from the production database.

AC4 — Daily historical chart is displayed by default (Frontend)

* Given the user clicks on a station marker and the station detail panel is opened  
* When the historical occupancy section is loaded  
* Then the system shall display the daily chart (last 7 days) by default.  
* Implementation: map.html JavaScript fetch daily API and render bar chart

AC5 — User can toggle between Hourly and Daily views (Frontend)

* Given the historical occupancy chart is displayed  
* When the user clicks the toggle button (Hourly / Daily)  
* Then the system shall update the chart to display the selected time range without reloading the page.  
* Implementation: map.html JavaScript button event listener \+ API fetch \+ chart re-render

AC6 — Hourly chart displays 8 bars representing last 8 hours (Frontend)

* Given the Hourly view is selected  
* When hourly historical data is received  
* Then the system shall display a bar chart with exactly 8 bars, each representing one hour of average available bikes.  
* Implementation: Chart rendering logic (e.g., Chart.js) in map.html

AC7 — Daily chart displays 7 bars representing last 7 days (Frontend)

* Given the Daily view is selected  
* When daily historical data is received  
* Then the system shall display a bar chart with exactly 7 bars, each representing one day of average available bikes.  
* Implementation: Chart rendering logic in map.html

AC8 — Chart displays an average reference line (Frontend)

* Given the historical occupancy chart is displayed  
* When the data is rendered  
* Then the system shall display a horizontal reference line representing the mean availability over the selected period (8 hours or 7 days).  
*   
* Implementation: Chart configuration including calculated mean value overlay

**User Story 5 (Predict Future Occupancy):**  
As a user, I want to see predicted bike availability for the next few hours, so that I can better plan my trip.

AC1 — Prediction API returns next 8 hours of predicted availability (Backend)

* Given the prediction service and required input data are available in the system  
* When the client requests prediction data for a specific station  
* Then the system shall return predicted availability for the next 8 hours, including:  
  * Station\_id  
  * forecast\_time\_local (8 future hourly timestamps)  
  * predicted\_available\_bikes (one value per hour)  
  * generated\_at timestamp  
* and the results shall be ordered chronologically.  
* Implementation: Flask route (e.g., GET /api/station/\<id\>/predict) calling the prediction component and returning JSON.

AC2 — Prediction uses the latest available input data (Backend)

* Given the prediction endpoint is called  
* When the system generates prediction results  
* Then the system shall use the most recent available input data stored in the database (e.g., latest station availability and weather data, if applicable).  
*   
* Implementation: Prediction service retrieves latest required records from the database before generating predictions.

AC3 — Prediction request failures are handled gracefully (Backend)

* Given a prediction request is made  
* When prediction cannot be generated (e.g., missing data, model unavailable, internal error)  
* Then the system shall return an appropriate HTTP status code and a structured error message in JSON format.  
*   
* Implementation: Flask error handling within the prediction route.

AC4 — Backend Service Is Deployed and Accessible via EC2(Backend)

* Given the Flask application is deployed on an AWS EC2 instance  
* When a client sends a request to the public API endpoint  
* Then the system shall respond with valid JSON data from the production database.

AC5 — Predicted occupancy bar chart for next 8 hours is displayed (Frontend)

* Given the user clicks on a station marker and the station detail panel is opened  
* When the predicted occupancy section is loaded and prediction data is successfully received  
* Then the system shall display a bar chart representing the next 8 hours, where:  
  * exactly 8 bars are shown  
  * each bar represents the predicted available bikes for one future hour  
  * time labels are displayed chronologically (e.g., actual local times or \+1h to \+8h)  
* Implementation: Client-side JavaScript fetches prediction API and renders a bar chart in the station detail panel."

AC6 — User-friendly message is shown when prediction is unavailable (Frontend)

* Given the predicted occupancy section is visible  
* When the prediction request fails or returns an error  
* Then the system shall display a clear message (e.g., “Prediction unavailable”) without affecting the rest of the station detail panel.  
*   
* Implementation: Client-side JavaScript error handling and UI state management.

**User Story 6 (Journey/ Directions Planner):**  
As a user, I want to find a bike, enter my end location, and receive a full journey plan including walking and cycling directions.

AC1 — Return candidate stations for journey planning (Backend)

* Given the database contains the latest station locations and availability  
* When the client requests nearby stations for a given coordinate (lat/lng)  
* Then the system shall return a JSON list of candidate stations near that coordinate including station id, name, lat, lng, and latest available bikes/stands.  
* Implementation: Flask route (e.g., GET /api/stations/nearby?lat=...\&lng=...\&k=...) querying DB and returning JSON

AC2 — Journey plan API returns a route including at least one cycling segment (Backend)

* Given the client provides valid start and destination coordinates  
* When the client requests a journey plan  
* Then the system shall return a journey plan composed of one or more route segments, where:  
  * the plan includes at least one cycling segment,  
  * each segment specifies the transport mode (walk or cycle),  
  * start and end labels,  
  * duration and distance,  
  * and polyline/coordinates for map rendering.  
* Implementation: Flask route (e.g., POST /api/journey/plan) that selects candidate stations and calls routing services (e.g., Google Directions API), then returns structured JSON."

AC3 — Backend Service Is Deployed and Accessible via EC2(Backend)

* Given the Flask application is deployed on an AWS EC2 instance  
* When a client sends a request to the public API endpoint  
* Then the system shall respond with valid JSON data from the production database.

AC4 — : Return journey plan using depart-at datetime (Backend) (Optional)

* Given the client provides a depart-at date/time  
* When the client requests a journey plan with depart-at specified  
* Then the system shall return a journey plan generated using the requested departure time, and include the depart-at value in the response metadata.  
* Implementation: Flask route POST /api/journey/plan accepts depart\_at parameter and passes it to the routing provider if supported (Optional)

AC5 — Start point input provides address suggestions (Frontend)

* Given the journey planner panel is visible  
* When the user types into the start point input  
* Then the system shall display a dropdown list of suggested addresses that match the user’s input (fuzzy matching).  
* Implementation: Client-side JavaScript using Google Places Autocomplete (or similar) to show suggestions

AC6 — Destination input provides address suggestions (Frontend)

* Given the journey planner panel is visible  
* When the user types into the destination input  
* Then the system shall display a dropdown list of suggested addresses that match the user’s input (fuzzy matching).  
* Implementation: Client-side JavaScript using Google Places Autocomplete (or similar)

AC7 — “Get Directions” requests a journey plan (Frontend)

* Given the user has selected a start address and a destination address  
* When the user clicks “Get Directions”  
* Then the system shall request a journey plan and display route details in the panel.  
* Implementation: Client-side JavaScript calls backend journey plan API and renders the returned segments

AC8 — Route details show multi-segment instructions with mode icons (Frontend)

* Given a journey plan has been returned  
* When route details are rendered  
* Then the system shall display each segment in order with:  
  * an icon indicating mode (walk or bike)  
  * instruction text (e.g., “Walk to \<station\>”, “Cycle to \<station\>”, “Walk to destination”)  
  * duration in minutes  
* Implementation: Client-side JavaScript DOM rendering for segment list \+ icon mapping"

AC9 — Routes are drawn on the map with different line styles (Frontend)

* Given a journey plan has been returned  
* When the map renders the journey plan  
* Then the system shall draw the route polylines on the map, using different visual styles to distinguish walking vs cycling (e.g., dashed vs solid).  
* Implementation: Client-side JavaScript uses Google Maps Polyline rendering with style rules per mode"

AC10 — Depart-at journey plan request uses selected date/time (Frontend)(Optional) 

* Given the user has selected a depart-at date and time  
* When the user clicks “Get Directions”  
* Then the system shall include the depart-at value in the journey plan request.  
* Implementation: Client-side JavaScript includes depart\_at in the API request payload (Optional)

