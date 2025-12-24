<<<<<<< HEAD
# Comprehensive Telemedicine Backend

A fully functional, production-ready telemedicine backend built with FastAPI that remains completely free indefinitely by leveraging Render's free tier and other free services strategically.

## 🏗️ Architecture Overview

This system uses a modern, scalable architecture designed to run entirely on free-tier services:

- **FastAPI**: High-performance async API with automatic OpenAPI documentation
- **PostgreSQL**: 1GB free storage on Render (permanent, not a trial)
- **Redis**: 30MB free cache for sessions and rate limiting
- **Cloudinary**: 25GB free image storage
- **Render Disk**: Free file storage for documents
- **EmailJS**: Free email notifications
- **Firebase**: Free push notifications
- **Scikit-learn**: Free ML models for symptom checking

## 🚀 Features

### Core Medical Features
- ✅ **User Management**: Patients, doctors, and admins with role-based access
- ✅ **Appointment Booking**: Schedule video calls, in-person, or chat consultations
- ✅ **Medical Records**: Comprehensive patient history with file attachments
- ✅ **Prescriptions**: Digital prescription management
- ✅ **Real-time Chat**: WebSocket-powered messaging between patients and doctors
- ✅ **Video Consultations**: WebRTC-based video calling system
- ✅ **File Upload**: Multi-service file storage (Cloudinary + local + Base64)
- ✅ **Notifications**: Email and push notifications for appointments and updates

### AI-Powered Features
- 🤖 **AI Symptom Checker**: Custom ML models trained on synthetic medical data
- 📊 **Condition Prediction**: Random Forest classifier for condition diagnosis
- ⚡ **Urgency Assessment**: Gradient Boosting for medical urgency classification
- 🔄 **Continuous Learning**: Models retrain weekly with user feedback
- 📈 **Decision Trees**: Adaptive questioning system for better diagnosis

### Technical Features
- 🔐 **JWT Authentication**: Secure token-based authentication with refresh tokens
- 🛡️ **Rate Limiting**: Redis-powered request rate limiting
- 📝 **Automatic Documentation**: OpenAPI/Swagger docs
- 🗄️ **Database Migrations**: Alembic for schema management
- 🧪 **Comprehensive Tests**: Unit and integration tests
- 🐳 **Docker Support**: Full containerization
- 📱 **WebSocket Support**: Real-time bidirectional communication
- 📊 **Health Monitoring**: Built-in health checks and metrics

## 💰 Cost Analysis: Always Free

| Service | Free Tier | Usage | Annual Cost |
|---------|-----------|--------|------------|
| **Render Web Service** | 750 hours/month | 24/7 operation | $0 |
| **Render PostgreSQL** | 1GB permanent | Database storage | $0 |
| **Render Redis** | 30MB | Caching & sessions | $0 |
| **Cloudinary** | 25GB | Image storage | $0 |
| **EmailJS** | 200 emails/month | Notifications | $0 |
| **Firebase** | Unlimited | Push notifications | $0 |
| **GitHub** | Unlimited | Code repository | $0 |
| **Domain** | Render subdomain | yourappp.onrender.com | $0 |
| **SSL Certificate** | Auto-generated | HTTPS encryption | $0 |
| ****Total Annual Cost** | | | **$0** |

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/telemedicine-backend.git
cd telemedicine-backend
```

2. **Set up environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
```

4. **Initialize database**
```bash
# Run database setup
python setup_db.py
```

5. **Start the server**
```bash
# Development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Access the application**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Using Docker

1. **Start with Docker Compose**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web
```

2. **Initialize database**
```bash
# Run setup inside container
docker-compose exec web python setup_db.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | SQLite file | No |
| `REDIS_URL` | Redis connection string | localhost:6379 | No |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `CLOUDINARY_*` | Cloudinary credentials | - | No |
| `EMAILJS_*` | EmailJS configuration | - | No |
| `FIREBASE_*` | Firebase credentials | - | No |

### Free Service Setup

#### 1. Render (Hosting & Database)
1. Connect GitHub repo to Render
2. Create PostgreSQL database (1GB free)
3. Create Redis instance (30MB free)
4. Deploy web service (750 hours/month free)

#### 2. Cloudinary (Image Storage)
1. Sign up at cloudinary.com
2. Get free 25GB storage
3. Add credentials to environment

#### 3. EmailJS (Email Notifications)
1. Create account at emailjs.com
2. Set up email service
3. Get service ID and template ID

#### 4. Firebase (Push Notifications)
1. Create Firebase project
2. Enable Cloud Messaging
3. Download service account key

## 📊 API Documentation

### Authentication Endpoints
```
POST /api/v1/auth/register     # Register new user
POST /api/v1/auth/login        # Login user
POST /api/v1/auth/refresh      # Refresh token
GET  /api/v1/auth/me          # Get current user
PUT  /api/v1/auth/me          # Update profile
POST /api/v1/auth/logout       # Logout user
```

### Appointment Endpoints
```
POST /api/v1/appointments/         # Create appointment
GET  /api/v1/appointments/         # List appointments
GET  /api/v1/appointments/{id}     # Get appointment
PUT  /api/v1/appointments/{id}     # Update appointment
PATCH /api/v1/appointments/{id}/status  # Update status
```

### Medical Record Endpoints
```
POST /api/v1/medical/records       # Create medical record
GET  /api/v1/medical/records       # List records
GET  /api/v1/medical/records/{id}  # Get record
PUT  /api/v1/medical/records/{id}  # Update record
POST /api/v1/medical/records/{id}/upload  # Upload file
```

### AI Symptom Checker Endpoints
```
POST /api/v1/ml/symptom-checker/start      # Start diagnosis
POST /api/v1/ml/symptom-checker/continue   # Continue with follow-up
POST /api/v1/ml/symptom-checker/feedback   # Submit feedback
GET  /api/v1/ml/symptom-checker/history    # Get history
```

### WebSocket Endpoints
```
WS /api/v1/ws/{token}                 # Main WebSocket connection
WS /api/v1/ws/video/{room_id}/{token} # Video call WebSocket
```

## 🤖 AI Symptom Checker

### How It Works

1. **Data Generation**: Creates 10,000+ synthetic patient cases based on medical probability tables
2. **Feature Engineering**: Processes symptoms, patient demographics, and medical history
3. **Model Training**: Uses Random Forest for condition prediction and Gradient Boosting for urgency
4. **Real-time Inference**: Provides instant diagnosis with confidence scores
5. **Continuous Learning**: Retrains weekly with user feedback

### Medical Knowledge Base

The system includes conditions such as:
- Common Cold, Influenza, Migraine
- Pneumonia, Hypertension, Diabetes
- Anxiety Disorders, and more

Each condition includes:
- Symptom probabilities
- Urgency levels (1-5)
- Specialist recommendations
- Age and gender prevalence

### Usage Example

```python
# Start symptom checker
{
  "initial_symptoms": [
    {"symptom": "fever", "severity": 7, "duration_days": 2},
    {"symptom": "cough", "severity": 5, "duration_days": 3}
  ],
  "patient_info": {
    "age": 35,
    "gender": "female"
  }
}

# Response
{
  "predicted_conditions": [
    {
      "condition_name": "Influenza", 
      "probability": 0.85,
      "urgency_level": 2,
      "specialist_recommended": "general_practitioner"
    }
  ],
  "urgency_score": 0.4,
  "recommendations": ["Contact your doctor within the next few days"]
}
```

## 🎥 Real-time Features

### WebSocket Communication

The system provides real-time features through WebSocket connections:

#### Chat Messages
```javascript
// Send message
{
  "type": "chat_message",
  "data": {
    "receiver_id": 123,
    "content": "Hello doctor",
    "message_type": "text"
  }
}
```

#### Video Calls
```javascript
// Join video call
{
  "type": "join_video_call",
  "data": {
    "room_id": "room_abc123"
  }
}

// WebRTC signaling
{
  "type": "video_signal",
  "data": {
    "signal_type": "offer",
    "room_id": "room_abc123",
    "signal_data": { /* WebRTC offer */ }
  }
}
```

### Notifications

Automatic notifications for:
- ⏰ Appointment reminders (24h before)
- 💊 New prescriptions
- 🔔 System updates
- 📱 Real-time chat messages

## 📁 File Storage Strategy

### Multi-Service Approach

1. **Small files (<100KB)**: Base64 encoding in database
2. **Images (<10MB)**: Cloudinary (25GB free)
3. **Documents**: Local Render disk storage (1GB free)
4. **Large files**: Chunked upload with compression

### Automatic Archiving

When approaching storage limits:
- Export old records to CSV
- Store in free cloud storage
- Update database with archive references

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

### Test Coverage
- Authentication: User registration, login, token refresh
- Appointments: CRUD operations, authorization, status updates
- Medical Records: Creation, file uploads, access control
- AI Features: Symptom checker, predictions, feedback
- WebSocket: Real-time messaging, video calls

## 🚀 Deployment

### Render Deployment

1. **Connect GitHub Repository**
   - Fork this repository
   - Connect to Render dashboard

2. **Create Services**
   ```bash
   # PostgreSQL Database
   Name: telemedicine-db
   Database: telemedicine
   User: telemedicine_user
   
   # Redis Instance
   Name: telemedicine-redis
   Max Memory: 30MB
   
   # Web Service
   Name: telemedicine-backend
   Build Command: pip install -r requirements.txt
   Start Command: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Set Environment Variables**
   ```bash
   SECRET_KEY=your-generated-secret-key
   DATABASE_URL=postgresql://user:pass@host/db  # Auto-generated
   REDIS_URL=redis://host:port  # Auto-generated
   DEBUG=false
   ```

4. **Deploy**
   - Push to main branch
   - Render automatically builds and deploys
   - Access at: https://your-app.onrender.com

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure `DATABASE_URL` for PostgreSQL
- [ ] Set `DEBUG=false`
- [ ] Configure Cloudinary credentials
- [ ] Set up EmailJS service
- [ ] Configure Firebase for push notifications
- [ ] Test all endpoints
- [ ] Monitor application health
- [ ] Set up backup strategy

## 📈 Monitoring & Maintenance

### Health Monitoring

The application includes built-in health checks:
- `/health` - Application health status
- Database connectivity
- Redis connectivity
- ML model availability

### Automatic Maintenance

- **Weekly ML Model Retraining**: Uses user feedback to improve accuracy
- **Scheduled Notifications**: Background task processes scheduled alerts
- **Data Archiving**: Automatic CSV export when approaching storage limits
- **Token Cleanup**: Expired JWT tokens cleaned from Redis

### Performance Optimization

- **Database Indexing**: Optimized queries with proper indexes
- **Redis Caching**: Frequently accessed data cached
- **Connection Pooling**: Efficient database connections
- **Async Operations**: Non-blocking I/O for better performance

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@telemedicine-backend.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/telemedicine-backend/issues)
- 📖 Documentation: [API Docs](https://your-app.onrender.com/docs)
- 💬 Discord: [Community Chat](https://discord.gg/your-invite)

## 🏆 Features in Detail

### 🔐 Security
- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Rate limiting per IP
- SQL injection prevention
- CORS protection
- Input validation

### 🎯 Scalability
- Async/await throughout
- Connection pooling
- Redis caching
- Database indexing
- Background tasks
- Horizontal scaling ready

### 🌐 Integration Ready
- REST API with OpenAPI spec
- WebSocket support
- Webhook support
- Third-party integrations
- Mobile app compatible
- Frontend framework agnostic

---

**Built with ❤️ for the healthcare community - Always free, always improving!**
=======
# mina-backend
>>>>>>> ee492ecf88feeff010fdb603430fde67087b7b25
