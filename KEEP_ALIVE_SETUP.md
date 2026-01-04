# Keep-Alive Mechanism for Render Free Tier

## What Was Added

Your backend now includes a **self-ping mechanism** that keeps your Render free tier service awake 24/7 by automatically pinging itself every 10 minutes.

## How It Works

1. **Background Task**: A background task (`keep_alive_ping()`) starts automatically when your service launches
2. **Self-Ping**: Every 10 minutes, it sends an HTTP request to your own `/health` endpoint
3. **Prevents Sleep**: This activity prevents Render from spinning down your service due to inactivity

## Configuration Steps

### 1. Update Your .env File (Local Development)
```env
BASE_URL=https://your-service-name.onrender.com
```
Replace `your-service-name` with your actual Render service name.

### 2. Update Render Environment Variables
In your Render dashboard:
1. Go to your service
2. Navigate to **Environment** tab
3. Add a new environment variable:
   - **Key**: `BASE_URL`
   - **Value**: `https://your-service-name.onrender.com` (your actual Render URL)

### 3. Deploy
After setting the `BASE_URL`, redeploy your service. The keep-alive mechanism will start automatically.

## How to Find Your Render URL

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your service
3. Your URL is shown at the top (e.g., `https://telemedicine-backend-xxxx.onrender.com`)
4. Copy this URL and use it as your `BASE_URL`

## Verification

After deployment, check your logs in Render dashboard. You should see:
```
Keep-alive mechanism started, pinging: https://your-url.onrender.com/health every 10 minutes
✓ Keep-alive ping successful - service staying active
```

## Technical Details

- **Ping Interval**: Every 10 minutes (600 seconds)
- **Startup Delay**: Waits 1 minute after service starts before first ping
- **Endpoint Used**: `/health` (lightweight health check)
- **Timeout**: 30 seconds per request
- **Fallback**: Uses `RENDER_EXTERNAL_URL` environment variable if `BASE_URL` is not set

## Benefits

✅ Service stays online 24/7 on free tier  
✅ No external services needed  
✅ Minimal resource usage  
✅ Automatic and maintenance-free  
✅ Logs ping status for monitoring  

## Troubleshooting

### If service still goes to sleep:
1. Verify `BASE_URL` is set correctly in Render environment variables
2. Check logs to ensure keep-alive task is running
3. Make sure the URL includes `https://` and matches your Render URL exactly

### If BASE_URL is not set:
The system will try to use `RENDER_EXTERNAL_URL` (automatically provided by Render) as a fallback.

## Important Notes

- This mechanism only works **after** you deploy and set the `BASE_URL`
- The service needs to know its own public URL to ping itself
- On Render's free tier, this keeps your service active but won't prevent cold starts completely during very low traffic periods
- Each ping uses minimal resources (just a health check endpoint)
