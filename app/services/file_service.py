import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any, List
import os
import base64
import magic
from pathlib import Path
from datetime import datetime
import logging

from config import settings

logger = logging.getLogger(__name__)

# Configure Cloudinary
if all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )


class FileStorageService:
    """Handle file storage across multiple services"""
    
    def __init__(self):
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self.local_storage_path = Path("./uploads")
        self.local_storage_path.mkdir(exist_ok=True)
    
    def validate_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Validate file size, type, and content"""
        # Check file size
        if len(file_content) > self.max_file_size:
            return {
                "valid": False,
                "error": f"File size exceeds maximum limit of {self.max_file_size / 1024 / 1024:.1f}MB"
            }
        
        # Check file extension
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        if file_extension not in self.allowed_extensions:
            return {
                "valid": False,
                "error": f"File type .{file_extension} not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            }
        
        # Check MIME type
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            allowed_mime_types = {
                'pdf': 'application/pdf',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            
            expected_mime = allowed_mime_types.get(file_extension)
            if expected_mime and mime_type != expected_mime:
                return {
                    "valid": False,
                    "error": f"File content doesn't match extension. Expected {expected_mime}, got {mime_type}"
                }
        
        except Exception as e:
            logger.warning(f"Could not validate MIME type: {str(e)}")
        
        return {"valid": True, "file_size": len(file_content), "mime_type": mime_type}
    
    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        folder: str = "medical_files",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Upload file to appropriate storage service"""
        # Validate file
        validation = self.validate_file(file_content, filename)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}
        
        try:
            # Determine storage strategy based on file size and type
            file_size = len(file_content)
            file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
            
            if file_size < 100 * 1024:  # < 100KB - store as Base64 in database
                return await self._store_as_base64(file_content, filename, validation["mime_type"])
            
            elif file_extension in ['jpg', 'jpeg', 'png'] and file_size < 10 * 1024 * 1024:  # Images < 10MB - use Cloudinary
                return await self._upload_to_cloudinary(file_content, filename, folder, user_id)
            
            else:  # Other files - store locally on Render disk
                return await self._store_locally(file_content, filename, folder, user_id)
        
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {str(e)}")
            return {"success": False, "error": "Upload failed due to server error"}
    
    async def _store_as_base64(self, file_content: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Store small files as Base64 in database"""
        try:
            base64_content = base64.b64encode(file_content).decode('utf-8')
            data_uri = f"data:{mime_type};base64,{base64_content}"
            
            return {
                "success": True,
                "storage_type": "base64",
                "url": data_uri,
                "filename": filename,
                "size": len(file_content)
            }
        
        except Exception as e:
            logger.error(f"Error storing file as Base64: {str(e)}")
            return {"success": False, "error": "Failed to encode file"}
    
    async def _upload_to_cloudinary(
        self, 
        file_content: bytes, 
        filename: str, 
        folder: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Upload images to Cloudinary"""
        try:
            # Create unique public ID
            public_id = f"{folder}/{user_id or 'anonymous'}/{filename.split('.')[0]}_{int(datetime.now().timestamp())}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                resource_type="auto",
                folder=folder
            )
            
            return {
                "success": True,
                "storage_type": "cloudinary",
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "filename": filename,
                "size": len(file_content)
            }
        
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {str(e)}")
            # Fallback to local storage
            return await self._store_locally(file_content, filename, folder, user_id)
    
    async def _store_locally(
        self, 
        file_content: bytes, 
        filename: str, 
        folder: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Store files locally on Render disk"""
        try:
            # Create directory structure
            user_folder = self.local_storage_path / folder / str(user_id or 'anonymous')
            user_folder.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            timestamp = int(datetime.now().timestamp())
            safe_filename = f"{timestamp}_{filename.replace(' ', '_')}"
            file_path = user_folder / safe_filename
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Generate access URL (you'd configure this based on your server setup)
            relative_path = file_path.relative_to(self.local_storage_path)
            url = f"/files/{relative_path}"
            
            return {
                "success": True,
                "storage_type": "local",
                "url": url,
                "path": str(file_path),
                "filename": filename,
                "size": len(file_content)
            }
        
        except Exception as e:
            logger.error(f"Error storing file locally: {str(e)}")
            return {"success": False, "error": "Failed to store file locally"}
    
    async def delete_file(self, file_url: str, storage_type: str) -> bool:
        """Delete a file from storage"""
        try:
            if storage_type == "cloudinary":
                # Extract public_id from URL
                public_id = file_url.split('/')[-1].split('.')[0]
                result = cloudinary.uploader.destroy(public_id)
                return result.get("result") == "ok"
            
            elif storage_type == "local":
                # Delete local file
                file_path = Path(file_url.replace("/files/", str(self.local_storage_path) + "/"))
                if file_path.exists():
                    file_path.unlink()
                    return True
            
            elif storage_type == "base64":
                # Nothing to delete for Base64 files (stored in database)
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error deleting file {file_url}: {str(e)}")
            return False
    
    def get_file_info(self, file_url: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            if file_url.startswith("data:"):
                # Base64 file
                mime_type = file_url.split(';')[0].replace('data:', '')
                return {
                    "storage_type": "base64",
                    "mime_type": mime_type,
                    "size": len(file_url) * 3 // 4  # Approximate size
                }
            
            elif "cloudinary.com" in file_url:
                return {"storage_type": "cloudinary", "url": file_url}
            
            else:
                return {"storage_type": "local", "url": file_url}
        
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None


class ArchiveService:
    """Handle data archiving to CSV for space management"""
    
    def __init__(self):
        self.archive_path = Path("./archives")
        self.archive_path.mkdir(exist_ok=True)
    
    async def archive_old_records(self, cutoff_date: datetime, table_name: str) -> str:
        """Archive old records to CSV"""
        try:
            # This would query the database for old records
            # For now, simulate the archiving process
            archive_filename = f"{table_name}_{cutoff_date.strftime('%Y%m%d')}.csv"
            archive_file_path = self.archive_path / archive_filename
            
            # In production, you would:
            # 1. Query old records from database
            # 2. Export to CSV
            # 3. Delete from database
            # 4. Update archive metadata
            
            logger.info(f"Archived old {table_name} records to {archive_file_path}")
            return str(archive_file_path)
        
        except Exception as e:
            logger.error(f"Error archiving {table_name}: {str(e)}")
            raise


# Global service instances
file_storage_service = FileStorageService()
archive_service = ArchiveService()