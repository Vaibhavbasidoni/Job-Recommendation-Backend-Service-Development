# Job Recommendation API

This project implements a job recommendation API using FastAPI and MongoDB. It provides personalized job recommendations based on a user's profile, skills, and preferences.

## Setup Instructions

1. Prerequisites:
   - Python 3.7 or higher
   - MongoDB

2. Clone the repository:
   ```
   git clone <repository-url>
   cd job-recommendation-api
   ```

3. Install dependencies:
   ```
   pip install fastapi uvicorn pymongo
   ```

4. Ensure MongoDB is running on localhost:27017

5. Start the FastAPI application:
   ```
   python -m uvicorn main:app --reload
   ```

6. Access the API documentation at `http://127.0.0.1:8000/docs`

## API Usage

Use the `/recommend` endpoint to get job recommendations:

POST `/recommend`
