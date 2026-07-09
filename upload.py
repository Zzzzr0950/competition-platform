"""File upload handling: validation, saving, thumbnail generation."""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, THUMBNAIL_FOLDER


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image(file_storage):
    """Validate image by checking file header bytes (magic bytes)."""
    header = file_storage.read(8)
    file_storage.seek(0)  # Reset for later reading

    # JPEG: FF D8 FF
    if header[:3] == b'\xff\xd8\xff':
        return True
    # PNG: 89 50 4E 47
    if header[:4] == b'\x89PNG':
        return True
    # PDF: 25 50 44 46
    if header[:4] == b'%PDF':
        return True

    return False


def save_upload(file_storage):
    """Save uploaded file with UUID name, return (relative_path, thumbnail_path)."""
    if not file_storage or not allowed_file(file_storage.filename):
        raise ValueError('不支持的文件格式，仅支持 JPG、PNG、PDF')

    if not validate_image(file_storage):
        raise ValueError('文件内容校验失败，请上传真实的图片或 PDF 文件')

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(filepath)

    # Generate thumbnail if image
    thumb_filename = None
    if ext in ('jpg', 'jpeg', 'png'):
        thumb_filename = create_thumbnail(filepath, filename)

    return f"certificates/{filename}", thumb_filename


def create_thumbnail(filepath, original_filename):
    """Create a thumbnail (400px wide) for certificate preview."""
    try:
        img = Image.open(filepath)
        # Convert to RGB if necessary (for PNG with alpha)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Resize to 400px wide maintaining aspect ratio
        w, h = img.size
        if w > 400:
            new_h = int(h * 400 / w)
            img = img.resize((400, new_h), Image.LANCZOS)

        thumb_name = f"thumb_{original_filename.rsplit('.', 1)[0]}.jpg"
        thumb_path = os.path.join(THUMBNAIL_FOLDER, thumb_name)
        img.save(thumb_path, 'JPEG', quality=80, optimize=True)

        return f"thumbnails/{thumb_name}"
    except Exception:
        # If thumbnail fails, return None (original will be used)
        return None


def save_uploads(file_list):
    """Save multiple uploaded files, return comma-separated relative paths."""
    paths = []
    for f in file_list:
        if f and f.filename:
            try:
                cert_path, _ = save_upload(f)
                paths.append(cert_path)
            except ValueError:
                pass  # skip invalid files
    return ','.join(paths)


def parse_certificate_images(value):
    """Parse certificate_image field into list of paths."""
    if not value:
        return []
    return [p.strip() for p in value.split(',') if p.strip()]


def get_image_url(relative_path):
    """Convert a relative path to a URL for templates."""
    if not relative_path:
        return None
    return f"/uploads/{relative_path}"
