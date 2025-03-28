from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.files.uploadedfile import InMemoryUploadedFile
from main.models import Party, Guest, EventInvite, GalleryPhoto
from PIL import Image, ExifTags
from io import BytesIO
import boto3
from wedding_website import settings
import uuid
import random
import os
import traceback
import logging

logger = logging.getLogger(__name__)

def upload_file(file_path, order):
    logger.info(f"Saving {file_path}")
    uploaded_file = open(file_path, "rb")
    # Configure S3
    s3 = boto3.client('s3')
    bucket_name = settings.GALLERY_BUCKET
    cloudfront_domain = settings.CLOUDFRONT_DOMAIN
    base_path = 'gallery_photos/'
    # Read the uploaded file into memory
    file_content = uploaded_file.read()
    # Check the format of the uploaded file
    image = Image.open(BytesIO(file_content))
    format = image.format  # Get the format of the image
    # Apply EXIF orientation if available
    try:
        exif = image._getexif()
        if exif:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        logger.warning(f"EXIF orientation handling failed: {e}")
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.{'jpg' if format in ['HEIC', 'HEIF'] else format.lower()}"
    # Ensure the image is converted to RGB for HEIC or images with alpha channels
    if format in ["HEIC", "HEIF"] or image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGB")  # Convert to RGB
    # Save the image to an in-memory file
    image_io = BytesIO()
    save_format = "JPEG" if format in ["HEIC", "HEIF"] else format  # Use JPEG for HEIC, retain original format otherwise
    if save_format == "JPEG":
        image.save(image_io, format=save_format, quality=100)
    else:
        image.save(image_io, format=save_format)
    image_io.seek(0)  # Reset file pointer
    # Upload the original file
    original_file_key = f"{base_path}{filename}"
    s3.upload_fileobj(image_io, bucket_name, original_file_key)
    url = f"https://{cloudfront_domain}/{original_file_key}"
    # Create the thumbnail
    image.thumbnail((400, 400))  # Resize the image for the thumbnail
    # Ensure thumbnail is in RGB mode for JPEG compatibility
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGB")  # Convert to RGB
    # Save the thumbnail as JPEG
    thumbnail_io = BytesIO()
    image.save(thumbnail_io, format="JPEG", quality=95)  # Save thumbnail as JPEG
    thumbnail_io.seek(0)
    thumbnail_file_key = f"{base_path}thumbnails/{filename}"
    s3.upload_fileobj(thumbnail_io, bucket_name, thumbnail_file_key)
    thumbnail_url = f"https://{cloudfront_domain}/{thumbnail_file_key}"
    description = os.path.basename(file_path)
    GalleryPhoto.objects.create(url=url, thumbnail_url=thumbnail_url, description=description, order=order)

folder_path = "/home/ec2-user/Photos-Wedding-Website"
filenames = os.listdir(folder_path)
filenames.sort()
for i in range(len(filenames)):
    try:
        upload_file(f"{folder_path}/{filenames[i]}", i*10)
    except:
        logger.error(f"Failed {filenames[i]}")
        logger.error(traceback.format_exc())
