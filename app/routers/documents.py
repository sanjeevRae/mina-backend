"""
Document Upload Router
Handles medical document and report uploads with Cloudinary integration
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.auth import get_current_active_user
from app.models.user import User
from app.services.file_service import file_storage_service

router = APIRouter(prefix="/documents", tags=["Document Upload"])
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload (PDF, images, DOCX)"),
    folder: str = Form("medical_files", description="Storage folder category"),
    description: Optional[str] = Form(None, description="Optional file description"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a medical document or report
    
    Supported formats: PDF, JPG, JPEG, PNG, DOC, DOCX
    Max file size: 10MB
    
    Files are automatically routed to:
    - Cloudinary: Preferred for supported uploads when configured
    - Local storage: Fallback when Cloudinary is unavailable or fails
    - Base64 in database: Reserved for generic small-file flows that do not request Cloudinary
    """
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Upload to Cloudinary or local storage
        result = await file_storage_service.upload_file(
            file_content=content,
            filename=file.filename,
            folder=folder,
            user_id=current_user.id,
            prefer_cloudinary=True
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Upload failed"))
        
        # Log upload
        logger.info(f"User {current_user.id} uploaded {file.filename} via {result.get('storage_type')}")
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": {
                "filename": result.get("filename"),
                "url": result.get("url"),
                "storage_type": result.get("storage_type"),
                "public_id": result.get("public_id"),
                "size": result.get("size"),
                "uploaded_by": current_user.id,
                "description": description
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")


@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: list[UploadFile] = File(..., description="Multiple documents to upload"),
    folder: str = Form("medical_files"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload multiple medical documents at once
    
    Max 10 files per request
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request")
    
    results = []
    errors = []
    
    for file in files:
        try:
            content = await file.read()
            
            result = await file_storage_service.upload_file(
                file_content=content,
                filename=file.filename,
                folder=folder,
                user_id=current_user.id,
                prefer_cloudinary=True
            )
            
            if result.get("success"):
                results.append({
                    "filename": result.get("filename"),
                    "url": result.get("url"),
                    "storage_type": result.get("storage_type"),
                    "public_id": result.get("public_id"),
                    "size": result.get("size")
                })
            else:
                errors.append({
                    "filename": file.filename,
                    "error": result.get("error")
                })
        
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(results) > 0,
        "uploaded": len(results),
        "failed": len(errors),
        "files": results,
        "errors": errors if errors else None
    }


@router.get("/storage-info")
async def get_storage_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get information about storage configuration
    """
    return {
        "cloudinary_enabled": file_storage_service.cloudinary_enabled,
        "storage_strategy": {
            "profile_images_and_documents": "Cloudinary preferred when enabled, with local storage fallback",
            "small_generic_files": "Base64 in database (< 100KB) when Cloudinary preference is not requested",
            "other_files": "Local storage",
            "fallback": "Local storage if Cloudinary fails"
        },
        "allowed_extensions": file_storage_service.allowed_extensions,
        "max_file_size": f"{file_storage_service.max_file_size / 1024 / 1024:.1f} MB",
        "cloudinary_free_tier": {
            "storage": "25 GB",
            "transformations": "25,000/month",
            "bandwidth": "25 GB/month"
        }
    }


@router.delete("/delete")
async def delete_document(
    file_url: str,
    storage_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a document from storage
    
    Requires:
    - file_url: The URL of the file to delete
    - storage_type: 'cloudinary', 'local', or 'base64'
    """
    try:
        # TODO: Add database check to verify user owns this file
        
        success = await file_storage_service.delete_file(file_url, storage_type)
        
        if success:
            return {"success": True, "message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete file")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during deletion")
