# Telemedicine Backend

A fully functional, production-ready telemedicine backend built with FastAPI, designed to run on Render's free tier and other free services.

## Features
- User management (patients, doctors, admins)
- Appointment booking (video, in-person, chat)
- Medical records and prescriptions
- Real-time chat and video consultations
- File upload and storage
- Email and push notifications
- AI-powered symptom checker
- JWT authentication and rate limiting
- Automatic API documentation
- Docker and cloud-ready

## Quick Start
1. Clone the repository
2. Set up your environment variables in `.env`
3. Install dependencies: `pip install -r requirements.txt`
4. Initialize the database: `python setup_db.py`
5. Start the server: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## Deployment
See the Render and Docker instructions in this README for deploying to the cloud or running locally with Docker Compose.

## License
MIT License

