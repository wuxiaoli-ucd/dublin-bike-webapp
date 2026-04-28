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
- SQLAlchemy
- HTML / CSS / JavaScript

## Project Structure
```
dublin-bike-webapp
├── app
│   ├── routes              # Flask route definitions
│   ├── services            # Business logic / data processing
│   ├── templates           # HTML files
│   └── static              # Static assets
│       ├── js              # JavaScript files
│       └── css             # CSS files
│
├── scraper                 # API data collection scripts
├── models                  # Database models (SQLAlchemy)
│
├── docs
│   ├── personas.md         # User personas
│   ├── stories.md          # User stories & AC
│   └── mockups             # UI mockups
│
├── tests                   # Unit tests
│
├── run.py                  # Application entry point
├── requirements.txt        # Dependencies
├── .gitignore              # Ignored files
└── README.md               # Project documentation
```

## Installation

Clone the repository:

```bash
git clone https://github.com/wuxiaoli-ucd/dublin-bike-webapp.git
cd dublin-bike-webapp
```

## Documentation
### Requirements & Design
- Personas → `docs/personas.md`
- User Stories & Acceptance Criteria → `docs/stories.md`
- UI Mockups → `docs/mockups/`

### Project Management
- Product Backlog → [View on Google Docs](https://docs.google.com/spreadsheets/d/1DY_0ggsqlPJSaJ-rkWWOccIhjW6koIHUWy71u4fS_ps/edit?gid=1973710968)
- Sprint Backlog → [View on Google Docs](https://docs.google.com/spreadsheets/d/1DY_0ggsqlPJSaJ-rkWWOccIhjW6koIHUWy71u4fS_ps/edit?gid=0)

## Team Members
- Xiaoli Wu
- Andrew Mitchell
- Conor Walsh

