from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Create a FastAPI app
app = FastAPI()

# Try to connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['job_recommendation_db']
    jobs_collection = db['jobs']
    print("Connected to MongoDB successfully!")
except ConnectionFailure:
    print("Failed to connect to MongoDB")
    db = None
    jobs_collection = None

# Define the structure of a user profile
class UserProfile(BaseModel):
    name: str
    skills: List[str]
    experience_level: str
    preferences: Dict[str, List[str]]

# Function to insert mock job data into the database
def insert_mock_jobs():
    if jobs_collection is None:
        print("Cannot insert mock jobs: MongoDB is not connected.")
        return
    
    # Delete existing jobs
    deleted_count = jobs_collection.delete_many({}).deleted_count
    print(f"Deleted {deleted_count} existing job documents.")

    # Mock job data
    mock_jobs = [
        {
            "job_id": 1,
            "job_title": "Software Engineer",
            "company": "Tech Solutions Inc.",
            "required_skills": ["JavaScript", "React", "Node.js"],
            "location": "San Francisco",
            "job_type": "Full-Time",
            "experience_level": "Intermediate"
        },
        {
            "job_id": 2,
            "job_title": "Data Scientist",
            "company": "Data Analytics Corp.",
            "required_skills": ["Python", "Data Analysis", "Machine Learning"],
            "location": "Remote",
            "job_type": "Full-Time",
            "experience_level": "Intermediate"
        },
        {
            "job_id": 3,
            "job_title": "Frontend Developer",
            "company": "Creative Designs LLC",
            "required_skills": ["HTML", "CSS", "JavaScript", "Vue.js"],
            "location": "New York",
            "job_type": "Part-Time",
            "experience_level": "Junior"
        },
        {
            "job_id": 4,
            "job_title": "Backend Developer",
            "company": "Web Services Co.",
            "required_skills": ["Python", "Django", "REST APIs"],
            "location": "Chicago",
            "job_type": "Full-Time",
            "experience_level": "Senior"
        },
        {
            "job_id": 5,
            "job_title": "Machine Learning Engineer",
            "company": "AI Innovations",
            "required_skills": ["Python", "Machine Learning", "TensorFlow"],
            "location": "Boston",
            "job_type": "Full-Time",
            "experience_level": "Intermediate"
        },
        {
            "job_id": 6,
            "job_title": "DevOps Engineer",
            "company": "Cloud Networks",
            "required_skills": ["AWS", "Docker", "Kubernetes"],
            "location": "Seattle",
            "job_type": "Full-Time",
            "experience_level": "Senior"
        },
        {
            "job_id": 7,
            "job_title": "Full Stack Developer",
            "company": "Startup Hub",
            "required_skills": ["JavaScript", "Node.js", "Angular", "MongoDB"],
            "location": "Austin",
            "job_type": "Full-Time",
            "experience_level": "Intermediate"
        },
        {
            "job_id": 8,
            "job_title": "Data Analyst",
            "company": "Finance Analytics",
            "required_skills": ["SQL", "Python", "Tableau"],
            "location": "New York",
            "job_type": "Full-Time",
            "experience_level": "Junior"
        },
        {
            "job_id": 9,
            "job_title": "Quality Assurance Engineer",
            "company": "Reliable Software",
            "required_skills": ["Selenium", "Java", "Testing"],
            "location": "San Francisco",
            "job_type": "Contract",
            "experience_level": "Intermediate"
        },
        {
            "job_id": 10,
            "job_title": "Systems Administrator",
            "company": "Enterprise Solutions",
            "required_skills": ["Linux", "Networking", "Shell Scripting"],
            "location": "Remote",
            "job_type": "Full-Time",
            "experience_level": "Senior"
        }
    ]
    
    # Insert the mock jobs into the database
    try:
        result = jobs_collection.insert_many(mock_jobs)
        print(f"Mock jobs inserted successfully! Inserted {len(result.inserted_ids)} documents.")
        for job in mock_jobs:
            print(f"Inserted job: {job['job_id']} - {job['job_title']}")
    except Exception as e:
        print(f"Error inserting mock jobs: {e}")

    # Verify the number of documents in the collection
    doc_count = jobs_collection.count_documents({})
    print(f"Total number of documents in the collection after insertion: {doc_count}")

# Function to recommend jobs based on user profile
def recommend_jobs(user_profile: UserProfile):
    if jobs_collection is None:
        raise HTTPException(status_code=503, detail="Database is not available")

    # Extract user information
    user_skills = set(user_profile.skills)
    user_experience = user_profile.experience_level
    user_preferences = user_profile.preferences

    # Create a more flexible query to find matching jobs
    query = {
        '$and': [
            {'job_type': {'$in': user_preferences['job_type']}},
            {'$or': [
                {'location': {'$in': user_preferences['locations']}},
                {'job_title': {'$in': user_preferences['desired_roles']}}
            ]},
            {'experience_level': user_experience}
        ]
    }
    print(f"MongoDB query: {query}")

    # Find potential jobs
    potential_jobs = list(jobs_collection.find(query))
    print(f"Number of potential jobs found: {len(potential_jobs)}")

    # Score jobs based on skill match and location/role preference
    scored_jobs = []
    for job in potential_jobs:
        required_skills = set(job['required_skills'])
        skill_match = len(user_skills.intersection(required_skills)) / len(required_skills)
        
        # Boost score if location or job title matches preferences
        location_match = 1 if job['location'] in user_preferences['locations'] else 0
        role_match = 1 if job['job_title'] in user_preferences['desired_roles'] else 0
        
        total_score = skill_match + 0.5 * (location_match + role_match)
        scored_jobs.append((job, total_score))

    # Sort jobs by total score
    scored_jobs.sort(key=lambda x: x[1], reverse=True)

    # Prepare recommendations
    recommendations = []
    for job, score in scored_jobs[:5]:  # Limit to top 5 recommendations
        recommendations.append({
            "job_title": job['job_title'],
            "company": job['company'],
            "location": job['location'],
            "job_type": job['job_type'],
            "required_skills": job['required_skills'],
            "experience_level": job['experience_level']
        })
    
    return recommendations

# API endpoint to get job recommendations
@app.post("/recommend")
async def get_job_recommendations(user_profile: UserProfile):
    print(f"Received user profile: {user_profile}")
    recommendations = recommend_jobs(user_profile)
    print(f"Recommendations: {recommendations}")
    return recommendations

# Run this when the app starts
@app.on_event("startup")
async def startup_event():
    insert_mock_jobs()

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)