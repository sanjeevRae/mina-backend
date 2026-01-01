"""
Test Cloudinary with larger file
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.file_service import file_storage_service
import asyncio


async def test_large_file():
    print("\n" + "="*60)
    print("Testing Cloudinary with Larger File (> 100KB)")
    print("="*60)
    
    # Create a larger test PNG file (150KB)
    # Simple PNG structure with random data
    png_header = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x02\x00\x00\x00\x02\x00'
        b'\x08\x02\x00\x00\x00\x90wS\xde'
    )
    
    # Generate 150KB of data
    large_test_file = png_header + (b'\x00' * (150 * 1024))
    
    print(f"\n   Test file size: {len(large_test_file) / 1024:.1f} KB")
    print(f"   Cloudinary enabled: {file_storage_service.cloudinary_enabled}")
    
    result = await file_storage_service.upload_file(
        file_content=large_test_file,
        filename="large_test_medical_report.png",
        folder="medical_reports",
        user_id=123
    )
    
    if result.get("success"):
        print(f"\n   ✓ Upload successful!")
        print(f"   - Storage Type: {result.get('storage_type')}")
        print(f"   - Filename: {result.get('filename')}")
        print(f"   - Size: {result.get('size') / 1024:.1f} KB")
        
        url = result.get('url', '')
        if len(url) > 80:
            print(f"   - URL: {url[:80]}...")
        else:
            print(f"   - URL: {url}")
        
        if result.get('public_id'):
            print(f"   - Cloudinary Public ID: {result.get('public_id')}")
        
        if result.get('storage_type') == 'cloudinary':
            print("\n   🎉 File successfully uploaded to Cloudinary!")
        elif result.get('storage_type') == 'local':
            print("\n   📁 File stored locally (fallback or Cloudinary disabled)")
    else:
        print(f"\n   ❌ Upload failed: {result.get('error')}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_large_file())
