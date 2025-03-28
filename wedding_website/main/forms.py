from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Party, Guest, EventInvite, GalleryPhoto
from PIL import Image, ExifTags
from io import BytesIO
import boto3
from wedding_website import settings
import uuid
import random
import sys

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except:
    sys.stderr.write("HEIF support not available.")

class GalleryPhotoForm(forms.ModelForm):
    file = forms.FileField(required=False, label="Upload File")  # New file upload field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['order'].initial = random.randint(1, 1000000)

    class Meta:
        model = GalleryPhoto
        fields = ['file', 'description', 'order']

    def save(self, commit:bool=True) -> GalleryPhoto:
        instance = super().save(commit=False)
        uploaded_file = self.cleaned_data.get('file')

        if uploaded_file:
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
                pass

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
            instance.url = f"https://{cloudfront_domain}/{original_file_key}"

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
            instance.thumbnail_url = f"https://{cloudfront_domain}/{thumbnail_file_key}"

        if commit:
            instance.save()
        return instance

class PartyCreationForm(UserCreationForm):
    class Meta:
        model = Party
        fields = ('name', 'email')

class PartyChangeForm(UserChangeForm):
    class Meta:
        model = Party
        fields = ('name', 'email', 'is_active', 'is_staff')

class PartySuggestionForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['suggestion']
        labels = {
            'suggestion': 'Do you have a song suggestion or any other notes?'
        }
        widgets = {
            'suggestion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class GuestUpdateForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['dietary_restrictions']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['dietary_restrictions'].widget.attrs.update({'class': 'form-control'})

class EventInviteForm(forms.ModelForm):
    class Meta:
        model = EventInvite
        fields = ['attending', 'meal']

    def __init__(self, *args, **kwargs) -> None:
        super(EventInviteForm, self).__init__(*args, **kwargs)
        event_invite = kwargs.get('instance', None)  # Get the instance if provided
        
        self.fields['meal'].required = False  # Make meal not required

        if event_invite and event_invite.event:
            # Set meal choices to those available for this event
            self.fields['meal'].queryset = event_invite.event.meals.all()
        else:
            # Optionally, disable the meal field if there is no event associated or no meals
            self.fields['meal'].disabled = True
            self.fields['meal'].help_text = 'No meal options available.'

        # Add Bootstrap classes
        self.fields['attending'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['meal'].widget.attrs.update({'class': 'form-select'})