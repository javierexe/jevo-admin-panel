import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
import cloudinary
import cloudinary.uploader
from app.core.config import settings


# Configure Cloudinary if credentials are provided
if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )


async def upload_file(file: UploadFile) -> Optional[str]:
    """
    Upload a file to either Cloudinary or local storage based on configuration.
    Returns the URL/path of the uploaded file.
    """
    if not file:
        return None
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    if settings.UPLOAD_STORAGE == "cloudinary":
        return await upload_to_cloudinary(file, contents)
    else:
        return await upload_to_local(file, contents)


async def upload_to_cloudinary(file: UploadFile, contents: bytes) -> str:
    """Upload file to Cloudinary"""
    try:
        # Determine resource type based on file content type
        resource_type = "auto"
        if file.content_type and file.content_type.startswith("video/"):
            resource_type = "video"
        elif file.content_type and file.content_type.startswith("image/"):
            resource_type = "image"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            resource_type=resource_type,
            folder="jevo_incidents"
        )
        return result.get("secure_url")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to Cloudinary: {str(e)}"
        )


async def upload_to_local(file: UploadFile, contents: bytes) -> str:
    """Upload file to local storage"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Return relative path or URL
        return f"/{file_path}"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to local storage: {str(e)}"
        )


async def delete_file(file_url: Optional[str]) -> bool:
    """
    Delete a file from either Cloudinary or local storage.
    Returns True if successful, False otherwise.
    """
    if not file_url:
        return False
    
    try:
        if settings.UPLOAD_STORAGE == "cloudinary":
            # Extract public_id from Cloudinary URL
            # Format: https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{format}
            if "cloudinary.com" in file_url:
                parts = file_url.split("/")
                public_id_with_ext = "/".join(parts[parts.index("upload") + 2:])
                public_id = os.path.splitext(public_id_with_ext)[0]
                cloudinary.uploader.destroy(public_id)
                return True
        else:
            # Delete from local storage
            if file_url.startswith("/"):
                file_url = file_url[1:]
            if os.path.exists(file_url):
                os.remove(file_url)
                return True
    except Exception:
        # Log error in production
        pass
    
    return False
