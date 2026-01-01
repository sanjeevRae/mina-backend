"""
Test Document Upload API with Cloudinary Integration
"""

import requests
import io
from PIL import Image

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
UPLOAD_URL = f"{BASE_URL}/documents/upload"
STORAGE_INFO_URL = f"{BASE_URL}/documents/storage-info"

# Test credentials (use existing user or create one)
TEST_USER = {
    "email": "test@example.com",
    "password": "Test123!@#"
}


def get_auth_token():
    """Login and get JWT token"""
    print("\n1. Authenticating...")
    response = requests.post(
        LOGIN_URL,
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("   ✓ Authentication successful")
        return token
    else:
        print(f"   ❌ Authentication failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_storage_info(token):
    """Get storage configuration info"""
    print("\n2. Getting Storage Configuration...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(STORAGE_INFO_URL, headers=headers)
    
    if response.status_code == 200:
        info = response.json()
        print(f"   ✓ Storage info retrieved")
        print(f"   - Cloudinary Enabled: {info['cloudinary_enabled']}")
        print(f"   - Max File Size: {info['max_file_size']}")
        print(f"   - Allowed Extensions: {', '.join(info['allowed_extensions'])}")
        return info
    else:
        print(f"   ❌ Failed to get storage info: {response.status_code}")
        return None


def create_test_image(size_kb=150):
    """Create a test image of specified size"""
    # Create a simple image
    img = Image.new('RGB', (800, 600), color='blue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes


def test_small_file_upload(token):
    """Test uploading a small file (should use Base64)"""
    print("\n3. Testing Small File Upload (< 100KB)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a tiny test image
    img = Image.new('RGB', (50, 50), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    files = {
        'file': ('small_test.png', img_bytes, 'image/png')
    }
    data = {
        'folder': 'test_uploads',
        'description': 'Small test image'
    }
    
    response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Upload successful")
        print(f"   - Storage Type: {result['file']['storage_type']}")
        print(f"   - Size: {result['file']['size']} bytes")
        if result['file']['storage_type'] == 'base64':
            print(f"   - URL: {result['file']['url'][:50]}...")
        else:
            print(f"   - URL: {result['file']['url']}")
        return result
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_large_image_upload(token):
    """Test uploading a larger image (should use Cloudinary if enabled)"""
    print("\n4. Testing Large Image Upload (> 100KB)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a larger test image
    img = Image.new('RGB', (1200, 900), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', quality=95)
    img_bytes.seek(0)
    
    file_size = len(img_bytes.getvalue())
    print(f"   - File size: {file_size / 1024:.1f} KB")
    
    files = {
        'file': ('large_medical_scan.png', img_bytes, 'image/png')
    }
    data = {
        'folder': 'medical_scans',
        'description': 'Large medical scan test'
    }
    
    response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Upload successful")
        print(f"   - Storage Type: {result['file']['storage_type']}")
        print(f"   - Size: {result['file']['size'] / 1024:.1f} KB")
        print(f"   - URL: {result['file']['url'][:80]}...")
        
        if result['file']['storage_type'] == 'cloudinary':
            print("\n   🎉 Cloudinary Upload Successful!")
        elif result['file']['storage_type'] == 'local':
            print("\n   📁 Local Storage Used (Cloudinary disabled or fallback)")
        
        return result
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_pdf_upload(token):
    """Test uploading a PDF document"""
    print("\n5. Testing PDF Upload...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple PDF-like content (for testing)
    pdf_content = b'%PDF-1.4\n%Test PDF\n' + (b'0' * 150000)  # 150KB
    
    files = {
        'file': ('medical_report.pdf', io.BytesIO(pdf_content), 'application/pdf')
    }
    data = {
        'folder': 'medical_reports',
        'description': 'Test medical report'
    }
    
    response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Upload successful")
        print(f"   - Storage Type: {result['file']['storage_type']}")
        print(f"   - Size: {result['file']['size'] / 1024:.1f} KB")
        print(f"   - URL: {result['file']['url'][:80]}...")
        return result
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def main():
    print("="*70)
    print("Document Upload API Test with Cloudinary Integration")
    print("="*70)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        print("\nMake sure you have a test user created:")
        print("   Email: test@example.com")
        print("   Password: Test123!@#")
        return
    
    # Get storage info
    storage_info = test_storage_info(token)
    
    # Test different upload scenarios
    test_small_file_upload(token)
    test_large_image_upload(token)
    test_pdf_upload(token)
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("\n✅ All upload tests completed!")
    print("\nStorage Strategy:")
    print("   - Small files (< 100KB): Base64 in database")
    print("   - Images & PDFs: Cloudinary (if configured) or local storage")
    print("   - Other files: Local storage")
    print("\nCloudinary Configuration:")
    if storage_info and storage_info.get('cloudinary_enabled'):
        print("   ✓ Cloudinary is ENABLED")
        print("   - Check uploaded files in your Cloudinary dashboard")
    else:
        print("   ⚠️  Cloudinary is DISABLED")
        print("   - Files are stored locally in uploads/ folder")
        print("   - See CLOUDINARY_SETUP.md for configuration instructions")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
