"""
Test Cloudinary Integration

This script tests the Cloudinary file upload integration.
Before running, set these environment variables:
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.file_service import file_storage_service
from app.config import settings
import asyncio


async def test_cloudinary():
    print("\n" + "="*60)
    print("Cloudinary Integration Test")
    print("="*60)
    
    # Check configuration
    print("\n1. Configuration Check:")
    print(f"   - Cloudinary Cloud Name: {settings.CLOUDINARY_CLOUD_NAME or '❌ Not Set'}")
    print(f"   - Cloudinary API Key: {'✓ Set' if settings.CLOUDINARY_API_KEY else '❌ Not Set'}")
    print(f"   - Cloudinary API Secret: {'✓ Set' if settings.CLOUDINARY_API_SECRET else '❌ Not Set'}")
    print(f"   - Cloudinary Enabled: {'✓ Yes' if file_storage_service.cloudinary_enabled else '❌ No'}")
    
    # Test with a sample file
    print("\n2. File Upload Test:")
    
    # Create a simple test image (1x1 PNG)
    test_image = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    print(f"   - Test file: test_upload.png ({len(test_image)} bytes)")
    
    result = await file_storage_service.upload_file(
        file_content=test_image,
        filename="test_upload.png",
        folder="test_folder",
        user_id=1
    )
    
    if result.get("success"):
        print(f"   ✓ Upload successful!")
        print(f"   - Storage Type: {result.get('storage_type')}")
        print(f"   - URL: {result.get('url')[:80]}..." if len(result.get('url', '')) > 80 else f"   - URL: {result.get('url')}")
        if result.get('public_id'):
            print(f"   - Public ID: {result.get('public_id')}")
    else:
        print(f"   ❌ Upload failed: {result.get('error')}")
    
    print("\n3. Storage Logic:")
    print("   - Files < 100KB: Base64 in database")
    print("   - Images/PDFs (jpg, jpeg, png, pdf): Cloudinary (if enabled)")
    print("   - Other files: Local storage (uploads/ folder)")
    print("   - Fallback: Local storage if Cloudinary fails")
    
    print("\n" + "="*60)
    print("How to Configure Cloudinary:")
    print("="*60)
    print("\n1. Sign up at https://cloudinary.com (free tier: 25GB storage)")
    print("2. Get your credentials from the dashboard")
    print("3. Set environment variables:")
    print("   - CLOUDINARY_CLOUD_NAME=your_cloud_name")
    print("   - CLOUDINARY_API_KEY=your_api_key")
    print("   - CLOUDINARY_API_SECRET=your_api_secret")
    print("4. Or add them to your .env file")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_cloudinary())
