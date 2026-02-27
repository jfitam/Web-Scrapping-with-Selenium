# Haramain Railway Web Scraper

This project implements a **web scraper for the Haramain High Speed Railway (HHR)** booking website.  
It automatically retrieves **train services, schedules, and fares** for different station pairs and stores the information in a PostgreSQL database.

The scraper is designed to support **data analysis and demand forecasting** by collecting structured data about train availability and ticket prices.

---

# Overview

The Haramain High Speed Railway website provides train schedules and fares through an interactive interface that requires browser interaction.

This project uses **Selenium** to simulate user actions in the website and extract:

- train numbers
- departure and arrival times
- origin and destination stations
- fare classes
- ticket prices
- availability (including sold-out trains)

The data is then stored in a **PostgreSQL database** for further analysis.

---

# Features

- Automated navigation of the HHR booking website
- Extraction of train schedules for all station combinations
- Optional scraping of ticket prices (slower but more detailed)
- Detection of **sold-out services**
- Retry logic to handle timeouts and unstable website responses
- Daily data refresh in the database
- Storage of results in a structured relational table

---

# Data Collected

For each train service the scraper collects:

- timestamp of extraction
- departure date
- train number
- origin station
- destination station
- departure time
- arrival time
- fare class
- fare type
- ticket price

This information enables later analysis of:

- price evolution
- service availability
- demand patterns
- forecasting models

---

# Technologies Used

- Python
- Selenium
- Pandas
- PostgreSQL
- SQLAlchemy
- Psycopg2
- WebDriver Manager

---

# Workflow

The scraper follows the following process:
1. Open HHR website
2. Select origin station
3. Select destination station
4. Select travel date
5. Load search results
6. Extract train information
7. (Optional) extract fare prices
8. Store results in PostgreSQL


For each day in the selected date range the script:

1. Queries all possible **station pairs**
2. Extracts available train services
3. Retrieves fare information when requested
4. Inserts the results into the database

Before inserting new data for a given day, the script deletes previous records for that date to avoid duplication.

---

# Stations Covered

The scraper collects data for all combinations between the following stations:

- Makkah
- Jeddah (Al-Sulimaniyah)
- Jeddah Airport
- King Abdullah Economic City (KAEC)
- Madinah

