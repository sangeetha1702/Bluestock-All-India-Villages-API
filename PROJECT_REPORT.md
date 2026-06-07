# All India Villages API Platform - Project Report

## 1. Project Overview

All India Villages API Platform is a REST API based project developed to provide structured village-level geographical data for India. The platform allows users and businesses to search village names and get standardized address details including village, sub-district, district, state, and country.

This project includes data cleaning, database creation, backend API development, API key authentication, admin dashboard, API documentation, and frontend demo client.

## 2. Project Objective

The main objective of this project is to build a centralized API platform for Indian village-level address data. This API can be used by businesses for address dropdowns, autocomplete, and standardized address selection in web applications.

## 3. Problem Statement

Businesses working in e-commerce, logistics, finance, and customer registration platforms often require accurate village-level address data. Managing this data manually is difficult because village data is large, hierarchical, and needs proper standardization.

## 4. Proposed Solution

The proposed solution is to create a REST API platform that stores India’s geographical hierarchy in a structured database and provides API endpoints for searching and retrieving data.

The hierarchy used in this project is:

Country → State → District → Sub-District → Village

## 5. Tools and Technologies Used

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

## 6. Dataset Description

The dataset contains India village-level geographical data in Excel and ODS format. The important columns used in the project are:

* State Code
* State Name
* District Code
* District Name
* Sub-District Code
* Sub-District Name
* Village Code
* Village Name

## 7. Data Cleaning

Raw Excel and ODS files were cleaned using Python and Pandas. Duplicate rows were removed, column names were standardized, and separate CSV files were created for each hierarchy level.

Cleaned output files:

* country.csv
* states.csv
* districts.csv
* subdistricts.csv
* villages.csv
* village_master.csv

## 8. Database Design

SQLite database was created with the following tables:

* countries
* states
* districts
* subdistricts
* villages
* users
* api_keys
* api_logs

The database stores village hierarchy data along with API users, API keys, and API usage logs.

## 9. Backend API Development

The backend was developed using Flask. API endpoints were created to retrieve states, districts, sub-districts, villages, search results, autocomplete suggestions, and admin statistics.

Main API endpoints:

* GET /api/v1/states
* GET /api/v1/states/{state_code}/districts
* GET /api/v1/districts/{district_code}/subdistricts
* GET /api/v1/subdistricts/{subdistrict_code}/villages
* GET /api/v1/search?q=Manibeli
* GET /api/v1/autocomplete?q=Man
* GET /api/v1/admin/stats

## 10. Authentication

API key authentication was implemented to protect the API endpoints.

Demo API Key:

X-API-Key: ak_demo_123456789

## 11. Frontend Demo Client

A frontend demo form was created using HTML, CSS, and JavaScript. The form allows users to type a village name and select a suggestion. After selection, sub-district, district, state, and country are automatically filled.

## 12. Admin Dashboard

The admin dashboard displays live project statistics such as total countries, states, districts, sub-districts, villages, users, API keys, and API logs.

## 13. API Documentation

An API documentation page was created to explain the base URL, authentication method, available endpoints, sample requests, and sample responses.

## 14. Project Data Coverage

* Countries: 1
* States: 30
* Districts: 586
* Sub-Districts: 5,764
* Villages: 619,246
* Users: 2
* API Keys: 1
* API Logs: 1

## 15. Sample Output

Search query:

/api/v1/search?q=Manibeli

Sample result:

Manibeli, Akkalkuwa, Nandurbar, MAHARASHTRA, India

## 16. Final Result

The project successfully provides a working village search API, address autocomplete demo form, admin dashboard, and API documentation page. This project demonstrates data cleaning, database management, backend API development, API authentication, and frontend integration.
