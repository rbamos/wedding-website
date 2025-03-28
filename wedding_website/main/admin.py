from django.contrib import admin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from typing import List
from .models import *
from .forms import PartyCreationForm, PartyChangeForm, GalleryPhotoForm
import os
import shutil
import zipfile
import base64
from .qr_code_utils import create_all_qr_codes, QR_CODES_DIR


@admin.register(Party)
class PartyAdmin(UserAdmin):
    model = Party
    add_form = PartyCreationForm  # Custom form for adding new users
    form = PartyChangeForm  # Custom form for changing user details
    list_display = ('name', 'email', 'is_staff', 'is_active')
    search_fields = ('name', 'email')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('name', 'email', 'password', 'events')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2'),
        }),
    )

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['name', 'party', 'attending', 'dietary_restrictions']
    list_filter = ['attending', 'party']
    search_fields = ['name', 'party__name']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location']

@admin.register(MealOption)
class MealOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'event']

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['url', 'thumbnail_url', 'description', 'order']
    if not settings.DEBUG:
        form = GalleryPhotoForm

    def delete_queryset(self, queryset):
        for obj in queryset.all():
            obj.delete()

@admin.register(EventInvite)
class EventInviteAdmin(admin.ModelAdmin):
    list_display = ['guest', 'event', 'attending', 'meal']

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    fields = ['party', 'file', 'qr_code_preview']
    list_display = ['party', 'is_qr_code_set']
    change_list_template = "admin/qr_code_tools.html"
    readonly_fields = ['file', 'qr_code_preview']

    def is_qr_code_set(self, obj: QRCode) -> bool:
        if obj.file:
            return True
        else:
            return False
    is_qr_code_set.boolean = True  # Displays a checkmark in the admin list view
    is_qr_code_set.short_description = "QR Code Set"
        
    def qr_code_preview(self, obj: QRCode) -> str:
        """Render the QR code as a blob in the detail view."""
        if obj.file and os.path.exists(obj.file):
            with open(obj.file, "rb") as f:
                image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return format_html(
                '<img src="data:image/png;base64,{}" style="height:200px; width:auto; border:1px solid #ddd; padding:5px;" alt="QR Code" />',
                base64_image
            )
        return "No QR Code Available"
    
    qr_code_preview.short_description = "QR Code Preview"

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            obj.delete()

    def get_urls(self) -> List[path]:
        urls = super().get_urls()
        custom_urls = [
            path(
                'create-all-qr-codes/',
                self.admin_site.admin_view(self.create_all_qr_codes),
                name='create_all_qr_codes'
            ),
            path(
                'download-qr-codes/',
                self.admin_site.admin_view(self.download_qr_codes),
                name='download_qr_codes'
            ),
            path(
                'delete-qr-codes/',
                self.admin_site.admin_view(self.delete_qr_codes),
                name='delete_qr_codes'
            ),
        ]
        return custom_urls + urls

    def create_all_qr_codes(self, request: HttpRequest) -> HttpResponse:
        hostname = os.getenv('HOSTNAME')
        create_all_qr_codes(hostname=hostname)
        self.message_user(request, "All QR codes have been created successfully.")
        return redirect("..")

    def download_qr_codes(self, request: HttpRequest) -> HttpResponse:
        zip_filename = "qr_codes.zip"
        if not os.path.isdir(QR_CODES_DIR):
            self.message_user(request, "QR codes directory not found.", level="error")
            return redirect("..")
        
        # Create zip file
        zip_path = os.path.join(QR_CODES_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(QR_CODES_DIR):
                for file in files:
                    if file != zip_filename and file != ".gitignore":  # Avoid re-adding the zip file itself
                        zipf.write(os.path.join(root, file), file)

        # Serve the zip file
        with open(zip_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/zip")
            response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
            return response

    def delete_qr_codes(self, request: HttpRequest) -> HttpResponse:
        if os.path.isdir(QR_CODES_DIR):
            # Iterate through the files in the directory
            for file_name in os.listdir(QR_CODES_DIR):
                file_path = os.path.join(QR_CODES_DIR, file_name)
                # Skip .gitignore file
                if file_name == ".gitignore":
                    continue
                # Remove file or directory
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            self.message_user(request, "All QR codes have been deleted.")
        else:
            self.message_user(request, "QR codes directory not found.", level="error")
        return redirect("..")