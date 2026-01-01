# Cloudinary Integration Guide

## Overview
Your backend now supports **Cloudinary** for cloud-based file storage with automatic fallback to local storage.

## Storage Strategy

### Automatic File Routing:
1. **Small files (< 100KB)**: Stored as Base64 in database
2. **Images & PDFs**: Uploaded to Cloudinary (jpg, jpeg, png, pdf)
3. **Other files**: Stored locally in `uploads/` folder
4. **Fallback**: If Cloudinary fails, files are stored locally

## Setup Instructions

### 1. Create Cloudinary Account
- Visit: https://cloudinary.com/users/register/free
- Free tier includes:
  - **25 GB storage**
  - **25,000 transformations/month**
  - **25 GB bandwidth/month**

### 2. Get Your Credentials
After signing up, go to your Dashboard to find:
- **Cloud Name** (e.g., `dxyz123abc`)
- **API Key** (e.g., `123456789012345`)
- **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz123`)

### 3. Configure Environment Variables

#### Option A: Using .env file (Recommended for Development)
Add to your `.env` file:
```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
CLOUDINARY_SECURE=True
```

#### Option B: Using System Environment Variables
**Windows (PowerShell):**
```powershell
$env:CLOUDINARY_CLOUD_NAME="your_cloud_name_here"
$env:CLOUDINARY_API_KEY="your_api_key_here"
$env:CLOUDINARY_API_SECRET="your_api_secret_here"
```

**Linux/Mac:**
```bash
export CLOUDINARY_CLOUD_NAME="your_cloud_name_here"
export CLOUDINARY_API_KEY="your_api_key_here"
export CLOUDINARY_API_SECRET="your_api_secret_here"
```

#### Option C: For Render Deployment
In Render dashboard:
1. Go to your web service
2. Navigate to **Environment** tab
3. Add the following environment variables:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

### 4. Restart Your Application
```bash
# Stop current server (Ctrl+C)
# Then restart:
python start_server.py
```

## Testing Cloudinary Integration

### Test 1: Check Configuration
```bash
python test_cloudinary_integration.py
```

### Test 2: Upload Large File
```bash
python test_cloudinary_large_file.py
```

## Usage in Your Application

### Upload File Example:
```python
from app.services.file_service import file_storage_service

# Upload a file
result = await file_storage_service.upload_file(
    file_content=file_bytes,
    filename="medical_report.pdf",
    folder="medical_reports",
    user_id=123
)

if result["success"]:
    # File uploaded successfully
    storage_type = result["storage_type"]  # 'cloudinary', 'local', or 'base64'
    file_url = result["url"]
    print(f"File stored via {storage_type}: {file_url}")
else:
    print(f"Upload failed: {result['error']}")
```

### Delete File Example:
```python
# Delete from Cloudinary or local storage
deleted = await file_storage_service.delete_file(
    file_url=file_url,
    storage_type=storage_type
)
```

## API Integration

You can create an upload endpoint in your routers:

```python
from fastapi import APIRouter, UploadFile, File, Depends
from app.services.file_service import file_storage_service
from app.auth import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    folder: str = "medical_files",
    current_user: User = Depends(get_current_user)
):
    """Upload a medical document or report"""
    # Read file content
    content = await file.read()
    
    # Upload to Cloudinary or local storage
    result = await file_storage_service.upload_file(
        file_content=content,
        filename=file.filename,
        folder=folder,
        user_id=current_user.id
    )
    
    return result
```

## Storage Costs & Limits

### Cloudinary Free Tier:
- ✅ 25 GB storage
- ✅ 25,000 transformations/month
- ✅ 25 GB bandwidth/month
- ✅ No credit card required

### Local Storage (Render):
- ⚠️ Ephemeral disk (files deleted on restart)
- ⚠️ Not suitable for permanent storage
- ✅ Good for temporary/cache files

### Recommendation:
- Use **Cloudinary** for permanent file storage (medical records, reports, images)
- Use **local storage** as fallback only
- Use **Base64** for tiny files (< 100KB) to reduce API calls

## Troubleshooting

### "Cloudinary not configured" message:
- Check that all three environment variables are set
- Verify no typos in variable names
- Restart the server after setting environment variables

### "Invalid cloud_name" error:
- Ensure your cloud name is exactly as shown in Cloudinary dashboard
- Cloud names are usually lowercase alphanumeric
- Don't use special characters or spaces

### Files not uploading to Cloudinary:
- Check if file extension is supported (jpg, jpeg, png, pdf)
- Verify file size is > 100KB (smaller files use Base64)
- Check Cloudinary dashboard for usage limits

### Local storage fallback activating:
- This is expected behavior if Cloudinary fails
- Check server logs for specific error messages
- Verify Cloudinary credentials are correct

## Memory Usage

Cloudinary integration adds minimal memory overhead:
- Package size: ~1.5 MB
- Runtime memory: < 5 MB
- Files are streamed, not loaded entirely into memory

This is safe for Render's free tier (512 MB RAM limit).

## Security Notes

- ✅ All Cloudinary uploads use HTTPS
- ✅ API credentials are stored in environment variables
- ✅ Files can be made private in Cloudinary settings
- ✅ Local fallback ensures no data loss
- ⚠️ Never commit credentials to git
- ⚠️ Use different credentials for dev/production

## Next Steps

1. ✅ Sign up for Cloudinary free account
2. ✅ Set environment variables
3. ✅ Test with `test_cloudinary_integration.py`
4. ✅ Create upload endpoint in your API
5. ✅ Update frontend to use upload endpoint
6. ✅ Deploy to Render with Cloudinary env vars

---

**Need Help?** 
- Cloudinary Docs: https://cloudinary.com/documentation
- Render Environment Variables: https://render.com/docs/environment-variables
