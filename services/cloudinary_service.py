import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import cloudinary
import cloudinary.uploader
import cloudinary.api

def is_cloudinary_configured():
    cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME')
    api_key = current_app.config.get('CLOUDINARY_API_KEY')
    api_secret = current_app.config.get('CLOUDINARY_API_SECRET')
    return bool(cloud_name and api_key and api_secret)

def init_cloudinary():
    if is_cloudinary_configured():
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET'],
            secure=True
        )

def upload_file(file_obj, seller_id, folder_type='gallery'):
    """
    Uploads file to Cloudinary or falls back to local disk storage.
    folder_type can be: 'logo', 'cover', 'products', 'gallery', 'certificates'
    Returns dict: {'url': ..., 'public_id': ...}
    """
    if not file_obj or not file_obj.filename:
        return None

    # Check Cloudinary configuration
    if is_cloudinary_configured():
        init_cloudinary()
        folder_path = f"sellers/{seller_id}/{folder_type}"
        resource_type = "auto"
        
        try:
            upload_result = cloudinary.uploader.upload(
                file_obj,
                folder=folder_path,
                resource_type=resource_type
            )
            return {
                'url': upload_result.get('secure_url', upload_result.get('url')),
                'public_id': upload_result.get('public_id')
            }
        except Exception as e:
            print(f"[Cloudinary Warning] Upload failed: {str(e)}. Using local fallback.")

    # Local Disk Fallback
    filename = secure_filename(file_obj.filename)
    ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    local_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'sellers', str(seller_id), folder_type)
    os.makedirs(local_dir, exist_ok=True)
    
    file_path = os.path.join(local_dir, unique_filename)
    file_obj.save(file_path)
    
    relative_url = f"/static/uploads/sellers/{seller_id}/{folder_type}/{unique_filename}"
    public_id = f"local_{seller_id}_{folder_type}_{unique_filename}"
    
    return {
        'url': relative_url,
        'public_id': public_id
    }

def delete_file(public_id):
    """
    Deletes file from Cloudinary or local disk based on public_id.
    """
    if not public_id:
        return False

    if public_id.startswith('local_'):
        parts = public_id.split('_', 3)
        if len(parts) >= 4:
            seller_id = parts[1]
            folder_type = parts[2]
            filename = parts[3]
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'sellers', seller_id, folder_type, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    return True
                except Exception as e:
                    print(f"[Local Storage Error] Could not delete {file_path}: {e}")
        return False

    if is_cloudinary_configured():
        init_cloudinary()
        try:
            cloudinary.uploader.destroy(public_id)
            return True
        except Exception as e:
            print(f"[Cloudinary Error] Delete failed for {public_id}: {e}")
            return False

    return False
