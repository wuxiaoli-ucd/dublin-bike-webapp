# Dublin Bike Web App
A web application that displays Dublin bike station information, including availability, location, and journey planning features.

## Project Overview
This project collects real-time bike station data from the JCDecaux API, stores it in a database, and provides a web interface for users to:

- View station locations
- Check available bikes and stands
- See weather information
- See historical occupancy
- See predicted occupany
- Plan journeys between locations

## Tech Stack
- Python
- Flask
- MySQL
- HTML / CSS / JavaScript

## Project Structure
```
dublin-bike-webapp
│
├── app/                         # Main Flask application
│   ├── routes/                  # API routes & page endpoints
│   ├── services/                # Business logic & data access layer
│   ├── templates/               # HTML templates (Jinja2)
│   ├── static/                  # Frontend assets
│   │   ├── js/                  # JavaScript (map, charts, API calls)
│   │   ├── css/                 # Styling
│   │   └── images/              # Icons and UI images
│   └── utils/                   # Helper functions (geo, time, etc.)
│
├── jcdecaux_scraper/            # JCDecaux bike data scraping scripts
├── weather_scraper/             # Weather data processing scripts
│
├── models/                      # Machine learning notebooks
├── docs/                        # Project documentation & report materials
│
├── tests/                       # Testing files (external - see note below)
│
├── run.py                       # Flask application entry point
├── environment.yml              # Environment dependencies
├── .gitignore
└── README.md
```

## Folder Details

### app/routes/

Defines Flask routes and API endpoints:

- `pages.py` – renders the main webpage  
- `stations_api.py` – returns real-time station data  
- `stations_history_api.py` – returns historical data for charts  
- `routing.py` – handles route planning using Google Routes API  
- `predictions.py` – provides bike and dock availability predictions  
- `weather.py` – provides weather data endpoints  

---

### app/services/

Handles backend logic and integrations:

- `db.py` – database connection (SQLAlchemy)  
- `stations_repo.py` – fetch latest station availability  
- `stations_history_repo.py` – fetch aggregated historical data  
- `google_routes.py` – integration with Google Routes API  
- `prediction_service.py` – machine learning prediction logic  
- `weather_service.py` – weather API integration with caching  

---

### app/static/

Frontend resources:

- `js/` – map interaction, API calls, charts, predictions  
- `css/` – UI styling  
- `images/` – icons and UI images  

---

### app/templates/

- `index.html` – main user interface  

---

### jcdecaux_scraper/

Scripts for collecting and processing Dublin Bikes data from the JCDecaux API.

- `s01_get_station.py` – test script for fetching station data from the JCDecaux API  
- `s02_create_db.py` – creates the MySQL database used for storing bike station data  
- `s03_create_tables.py` – creates database tables for storing station and availability data  
- `s04_jcdecaux_local_download.py` – downloads and stores API data locally  
- `s05_load_stations.py` – loads station metadata into the database  
- `s06_availability_scraper.py` – collects real-time bike availability data for periodic scraping  

- `bike_data_0214.sql` – SQL dump for database setup  
- `stations_snapshot.json` – sample snapshot of station data  

- `dbinfo.py` – database configuration helper  
- `__init__.py` – package initialization file  

---

### weather_scraper/

Scripts for collecting and storing weather data from the OpenWeather API.

- `s01_get_weather.py` – fetches weather data and saves raw JSON locally  
- `s02_create_db_tables_openweather.py` – creates the database and weather table  
- `s03_openweather_extract_info_from_json.py` – inspects JSON structure and key fields  
- `s04_openweather_text_to_db.py` – extracts and loads weather data into the database  
- `s05_queries.py` – runs queries to verify stored data  

- `openweather_dump.sql` – SQL dump for database setup  
- `dbinfo.py` – database configuration helper  

---

### models/

Contains machine learning notebooks used for prediction.

---

### docs/

Contains project documentation and supporting materials:

- `diagrams/` – system architecture and design diagrams  
  - overall architecture diagram  
  - backend class diagram  
  - frontend component diagram  
  - sequence diagram  

- `mockups/` – UI wireframes and interface designs  
  - multiple versions of UI mockups (`mockup1.png` – `mockup6.png`)  

- `requirements_elicitation/` – requirements gathering and analysis  
  - `interview_scripts.md` – stakeholder interview notes  
  - `personas.md` – user personas  
  - `user_stories.md` – user stories and acceptance criteria  
  - `system_market_analysis.docx` – market and system analysis  

- `screenshots/` – application screenshots and demo visuals  
  - overview dashboard  
  - station details view  
  - weather-based departure view  
  - route planning (bike / walk)  

---

### tests/

Due to GitHub storage limitations, the full testing files are not included in this repository.

Please refer to the project report for complete testing details.



## Installation

### Clone the repository:

```bash
git clone https://github.com/wuxiaoli-ucd/dublin-bike-webapp.git
cd dublin-bike-webapp
```

### Install Dependencies

```bash
conda env create -f environment.yml
conda activate <your-env-name>
```

## Project Management
- Product Backlog → [View on Google Docs](https://docs.google.com/spreadsheets/d/1DY_0ggsqlPJSaJ-rkWWOccIhjW6koIHUWy71u4fS_ps/edit?gid=1973710968)
- Sprint Backlog → [View on Google Docs](https://docs.google.com/spreadsheets/d/1DY_0ggsqlPJSaJ-rkWWOccIhjW6koIHUWy71u4fS_ps/edit?gid=0)
- Report → [View on Google Docs]https://docs.google.com/document/d/1onx3V0C9gPn-Cyhx1asdoLPOHtVmtyF5zU2nTiUUNnU/edit?tab=t.0
## Team Members
- Xiaoli Wu
- Andrew Mitchell
- Conor Walsh

