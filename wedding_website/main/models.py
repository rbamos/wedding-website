from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import hashlib
from . import qr_code_utils
import os
import random
import re
from wedding_website import settings
import boto3
import logging
from wedding_website import settings

class PartyManager(BaseUserManager):
    def create_user(self, name, email, password=None, **extra_fields):
        if not name:
            raise ValueError('The Name field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(name, "admin", password, **extra_fields)

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    about = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.name}"


class MealOption(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='meals')

    def __str__(self):
        return f"{self.name}"

class Party(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name_plural = "Parties"
        indexes = [
            models.Index(fields=["authentication_token_hash"])
        ]

    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    # Tokens are high entropy, random strings. No salt needed
    authentication_token_hash = models.CharField(max_length=64, unique=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    events = models.ManyToManyField(Event, related_name='invitees')
    suggestion = models.CharField(max_length=1000, blank=True, null=True)  # New field for music suggestions

    USERNAME_FIELD = 'name'

    objects = PartyManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission."""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Check if user has permissions to view the app `app_label`."""
        return self.is_superuser

    @classmethod
    def get_token_hash(_cls, auth_token):
        return hashlib.sha256(auth_token.encode('utf-8')).hexdigest()

# Guest model
class Guest(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=100)
    attending = models.BooleanField(default=False)
    dietary_restrictions = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({'Attending' if self.attending else 'Not Attending'})"
    
class GalleryPhoto(models.Model):
    url = models.CharField(max_length=200)
    thumbnail_url = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000)

    def default_order() -> int:
        return random.randint(1, 1000000)

    order = models.IntegerField(default=default_order)

    
    def delete(self, *args, **kwargs) -> None:
        """
        Delete the associated files from S3 when a GalleryPhoto object is deleted.
        """
        logger = logging.getLogger(__name__)

        # Pattern to match the file key from the URL
        pattern = r'^https://{}/(gallery_photos/.*)$'.format(
            re.escape(settings.CLOUDFRONT_DOMAIN)
        )

        # Configure S3 client
        s3 = boto3.client('s3')
        bucket_name = settings.GALLERY_BUCKET

        # Delete main file
        if self.url:
            match = re.match(pattern, self.url)
            if match:
                file_key = match.group(1)
                try:
                    s3.delete_object(Bucket=bucket_name, Key=file_key)
                except Exception as e:
                    logger.error(f"Error deleting file from S3: {e}")

        # Delete thumbnail file
        if self.thumbnail_url:
            match = re.match(pattern, self.thumbnail_url)
            if match:
                thumbnail_key = match.group(1)
                try:
                    s3.delete_object(Bucket=bucket_name, Key=thumbnail_key)
                except Exception as e:
                    logger.error(f"Error deleting thumbnail from S3: {e}")

        # Call the superclass delete method
        super().delete(*args, **kwargs)

class EventInvite(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='event_invites')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_invites', null=True)
    attending = models.BooleanField(default=False)
    meal = models.ForeignKey(MealOption, on_delete=models.PROTECT, null=True)
    
    def __str__(self) -> str:
        guest_name = self.guest.name if hasattr(self, 'guest') else None
        event_name = self.event.name if hasattr(self, 'event') and self.event is not None else None
        return f"{guest_name} - {event_name}: {self.attending} / {self.meal}"

class QRCode(models.Model):
    party = models.OneToOneField(Party, on_delete=models.CASCADE, related_name='qr_code')
    file = models.CharField(max_length=300, default=None)

    def save(self, *args, **kwargs) -> None:
        """"
        Generate QR code and set the file path before saving
        """
        if not self.file:
            email = self.party.email
            self.file = qr_code_utils.create_auth_qr(hostname=settings.HOSTNAME,email=email)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """"
        Delete the associated file when the QRCode object is deleted
        """
        if self.file and os.path.exists(self.file):
            os.remove(self.file)
        super().delete(*args, **kwargs)


