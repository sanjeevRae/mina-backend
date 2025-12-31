# 🚀 Mina Backend - Render Free Tier Deployment Guide

## Memory Optimization for Render Free Tier (512MB RAM)

This guide will help you deploy your telemedicine backend to Render's free tier successfully.

## ✅ What's Been Optimized

### 1. **Minimal Startup Memory Usage**
- ❌ Removed immediate ML model loading (loads on first request)
- ❌ Removed heavy background tasks on startup
- ❌ Removed immediate database initialization
- ✅ Only essential directories created

### 2. **Reduced Dependencies**
**REMOVED HEAVY PACKAGES:**
- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2` (Firebase)
- `aiohttp` (replaced with lightweight `httpx`)
- `alembic` (database migrations - not needed for free tier)
- `psycopg2-binary`, `asyncpg` (PostgreSQL drivers)
- `aioredis` (using basic `redis`)
- `cloudinary` (using local file storage)
- `pytest`, `pytest-asyncio` (testing not needed in production)

**KEPT ESSENTIAL PACKAGES:**
- `fastapi`, `uvicorn`, `pydantic`
- `sqlalchemy` (SQLite only)
- `scikit-learn`, `pandas`, `numpy`, `joblib` (ML - optimized)
- `redis` (basic client)
- `python-jose`, `passlib` (auth)

### 3. **Database Optimization**
- ✅ Using SQLite instead of PostgreSQL (no additional memory)
- ✅ Database initialized on-demand, not on startup
- ✅ No connection pooling overhead

### 4. **Memory Monitoring**
- ✅ Health check endpoint now shows memory usage
- ✅ Automatic optimization status reporting

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository
```bash
# Make sure you have these optimized files:
- requirements.txt (minimized dependencies)
- render.yaml (SQLite configuration)
- app/main.py (memory optimized)
- app/services/ml_service.py (lazy loading)
```

### Step 2: Set Up Render Account
1. Go to [render.com](https://render.com)
2. Sign up for free account
3. Connect your GitHub repository

### Step 3: Deploy Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repo
3. Configure build settings:

**Build Settings:**
```
Runtime: Python 3.11.4
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: python start_server.py
```

**Environment Variables:**
```
SECRET_KEY: [Generate Random] (Render will auto-generate)
DEBUG: false
DATABASE_URL: sqlite:///./telemedicine_dev.db
REDIS_URL: redis://red-d58fpluuk2gs73djegfg:PY5FJC6eNkCY6Vjiuj7dJ9jgUd4DjbyN@singapore-keyvalue.render.com:6379
ENABLE_ML_FEATURES: true
ENABLE_VIDEO_CALLS: true
ENABLE_PUSH_NOTIFICATIONS: false
ENABLE_EMAIL_NOTIFICATIONS: true
```

### Step 4: Initial Database Setup
After deployment, run the database setup:
```bash
# SSH into your Render instance or use the shell
python setup_db.py
```

### Step 5: Verify Deployment
1. Check the health endpoint: `https://your-app-name.onrender.com/health`
2. Should show memory usage under 400MB
3. Test basic endpoints

## 📊 Memory Usage Monitoring

### Health Check Response
```json
{
  "status": "healthy",
  "memory_usage_mb": 156.32,
  "memory_percent": 30.5,
  "render_free_tier_limit": "512 MB",
  "optimization_status": "memory_optimized"
}
```

### Memory Optimization Status
- 🟢 `memory_optimized`: < 400MB usage
- 🟡 `high_memory_usage`: 400-500MB usage
- 🔴 `critical_memory`: > 500MB usage

## 🔧 Troubleshooting

### Memory Issues
If you still get memory errors:

1. **Check ML Model Loading:**
   - ML models load on first `/api/v1/ml/symptom-checker` request
   - Monitor memory after first ML request

2. **Reduce Concurrent Connections:**
   - WebSocket connections consume memory
   - Consider limiting concurrent users

3. **Database Optimization:**
   - SQLite handles concurrent connections poorly
   - Keep database operations minimal

### Common Issues

**Issue: "Build failed - memory limit exceeded"**
```
Solution: Check that heavy dependencies were removed from requirements.txt
```

**Issue: "Application crashed after deployment"**
```
Solution: Check Render logs for specific error messages
```

**Issue: "ML model not working"**
```
Solution: Models load lazily - first request will take longer but subsequent will be fast
```

## 🏗️ Architecture Overview

### Free Tier Optimized Stack:
```
Frontend (Your App) ↔️ FastAPI (Render Free) ↔️ SQLite (Local)
                     ↔️ Redis (External)
                     ↔️ File Storage (Local)
```

### What's Working:
- ✅ JWT Authentication
- ✅ User Management
- ✅ Appointments (CRUD)
- ✅ Medical Records
- ✅ ML Symptom Checker (lazy loaded)
- ✅ Real-time Chat (WebSocket)
- ✅ File Upload (local storage)
- ✅ Email Notifications

### Limitations on Free Tier:
- ⚠️ No push notifications (Firebase removed)
- ⚠️ No cloud file storage (Cloudinary removed)
- ⚠️ SQLite instead of PostgreSQL
- ⚠️ Limited concurrent users

## 🚀 Scaling Up (Future)

When you need more resources:

### Starter Plan ($7/month):
- 1 GB RAM (2x memory)
- PostgreSQL database
- More concurrent connections

### Standard Plan ($25/month):
- 2 GB RAM (4x memory)
- Advanced features
- Better performance

## 📈 Performance Tips

### For Free Tier:
1. **Lazy Loading:** Keep ML models unloaded until needed
2. **Minimal Background Tasks:** Only run essential tasks
3. **Efficient Queries:** Use database indexes
4. **Memory Cleanup:** Use `gc.collect()` in memory-intensive operations

### Monitoring:
- Check `/health` endpoint regularly
- Monitor memory usage trends
- Watch for 512MB limit warnings

## 🔐 Security Notes

**REMOVED FOR FREE TIER:**
- Firebase push notifications (too heavy)
- Cloudinary file storage (external API calls)

**STILL SECURE:**
- JWT authentication
- Password hashing
- Input validation
- Rate limiting
- CORS protection

## 📞 Support

If you encounter issues:
1. Check Render deployment logs
2. Monitor memory usage via `/health` endpoint
3. Ensure all heavy dependencies are removed
4. Test endpoints individually

## ✅ Success Checklist

- [ ] Repository pushed with optimized files
- [ ] Render web service created
- [ ] Environment variables set
- [ ] Database initialized
- [ ] Health check shows < 400MB memory usage
- [ ] Basic endpoints working
- [ ] ML symptom checker loads on demand

---

**🎉 Your telemedicine backend is now optimized for Render's free tier!**

Memory usage should be well under 512MB with these optimizations, allowing successful deployment and operation.
