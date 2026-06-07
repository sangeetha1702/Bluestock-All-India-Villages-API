# All India Villages API Platform

## Project Overview

All India Villages API Platform is a REST API based project developed to provide structured village-level geographical data for India. The platform helps businesses use standardized address data for dropdown menus, village search, and address autocomplete functionality.

This project includes data cleaning, database creation, backend API development, API key authentication, admin dashboard, API documentation, and a demo client form.

## Problem Statement

Businesses building e-commerce, logistics, service, and customer registration platforms need reliable village-level address data. Maintaining local geographical databases is difficult and time-consuming. This project solves the problem by providing a centralized API for India’s village, sub-district, district, and state data.

## Solution

The solution provides a searchable API platform with the following hierarchy:

Country → State → District → Sub-District → Village

Users can search villages and receive standardized address output including village name, sub-district, district, state, and country.

## Tools and Technologies Used

* Python
* Pandas
* SQLite
* Flask
* Flask-CORS
* HTML
* CSS
* JavaScript
* PyCharm
* REST API
* API Key Authentication

## Project Modules

### 1. Data Cleaning

Raw Excel and ODS village data files were cleaned using Python and Pandas. The cleaned data was converted into structured CSV files.

Output files:

* country.csv
* states.csv
* districts.csv
* subdistricts.csv
* villages.csv
* village_master.csv

### 2. Database Creation

SQLite database was created with the following tables:

* countries
* states
* districts
* subdistricts
* villages
* users
* api_keys
* api_logs

### 3. Backend API

Flask REST API was created to access village data through different endpoints.

Main API endpoints:

* GET /api/v1/states
* GET /api/v1/states/{state_code}/districts
* GET /api/v1/districts/{district_code}/subdistricts
* GET /api/v1/subdistricts/{subdistrict_code}/villages
* GET /api/v1/search?q=Manibeli
* GET /api/v1/autocomplete?q=Man
* GET /api/v1/admin/stats

### 4. Authentication

API key authentication was added to protect API endpoints.

Demo API Key:

X-API-Key: ak_demo_123456789

### 5. Demo Client

A frontend demo form was created using HTML, CSS, and JavaScript. The form allows users to type a village name and automatically fills sub-district, district, state, and country details.

### 6. Admin Dashboard

Admin dashboard displays project statistics such as total countries, states, districts, sub-districts, villages, users, API keys, and API logs.

### 7. API Documentation

API documentation page was created to explain API base URL, authentication, endpoints, sample request, and sample response.

## Project Data Coverage

* Countries: 1
* States: 30
* Districts: 586
* Sub-Districts: 5,764
* Villages: 619,246
* Users: 2
* API Keys: 1
* API Logs: 1

## Sample Village Search Output

Example search query:

/api/v1/search?q=Manibeli

Sample result:

Manibeli, Akkalkuwa, Nandurbar, MAHARASHTRA, India

## How to Run the Project

1. Open the project in PyCharm.
2. Install required packages.
3. Run the data cleaning script.
4. Run the database creation script.
5. Run the Flask backend server.
6. Open the demo client, admin dashboard, and API documentation pages in browser.

## Python Packages Required

* pandas
* xlrd
* openpyxl
* odfpy
* flask
* flask-cors

## Final Output

The project successfully provides a working village search API, address autocomplete demo form, admin dashboard, and API documentation.
