# Stock Index Performance

This project demonstrates how the FastAPI backend provides API endpoints for handling **index performance** and **composition data**, while the Streamlit frontend allows users to interact with and visualize this data.

The application also supports **Excel** and **PDF** exports of the index performance and composition data using a factory pattern.

## Table of Contents
- [Installation](#installation)
- [Accessing the Application](#accessing-the-application)
- [Future Enhancements](#future-enhancements)

---

## Installation
Running first time
```bash
docker-compose up --build
```
Otherwise
```bash
docker-compose up
```

## Accessing the Application

Once the containers are up and running, you can access the applications through the following URLs:

FastAPI API docs: http://localhost:8000/docs
Streamlit Dashboard: http://localhost:8501
FastAPI provides the API endpoints, while Streamlit serves as the frontend to interact with the data and visualize it.

## Future Enhancements

1. Custom Export Options:

Add additional file formats (CSV, JSON, etc.).
Allow users to customize the format of the data (e.g., column selection, filters).

2. UI Improvements in Streamlit:

Add charts for additional data insights (e.g., performance over time).
Allow users to upload data (CSV, Excel) for real-time processing.

3. Background Tasks:

Implement background tasks for processing data asynchronously using Celery and Redis.

4. Add Tests:

Add more tests.
