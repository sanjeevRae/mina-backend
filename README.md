# Telemedicine Backend

A fully functional, production-ready telemedicine backend built with FastAPI, designed to run on Render's free tier and other free services.

## ✨ Features
- 👥 User management (patients, doctors, admins)
- 📅 Appointment booking (video, in-person, chat)
- 📋 Medical records and prescriptions
- 💬 Real-time chat and video consultations
- 📁 File upload and storage
- 📧 Email and push notifications
- **🤖 AI-powered symptom checker (NEW!)** - LightGBM-based condition prediction
- 🔐 JWT authentication and rate limiting
- 📖 Automatic API documentation
- 🐳 Docker and cloud-ready

## 🤖 AI Symptom Checker
**NEW:** Lightweight AI system that analyzes symptoms and provides wellness recommendations
- **98.9% accuracy** on 15 common conditions
- **2.7 MB model** - Ultra-lightweight LightGBM
- **180 MB memory** - Perfect for Render free tier
- **78 symptoms** recognized
- **NOT medical prescriptions** - General wellness advice only

See [SYMPTOM_CHECKER_README.md](SYMPTOM_CHECKER_README.md) for details.

## Quick Start
1. Clone the repository
2. Set up your environment variables in `.env`
3. Install dependencies: `pip install -r requirements.txt`
4. Initialize the database: `python setup_db.py`
5. Start the server: `python start_server.py`

`start_server.py` respects the configured `PORT` value and automatically falls back to an open local port if the preferred one is already in use.

## Deployment
See the Render and Docker instructions in this README for deploying to the cloud or running locally with Docker Compose.

## License
MIT License

