from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import GuestUpdateForm, EventInviteForm, PartySuggestionForm
from .models import Guest, Party, GalleryPhoto
from hashlib import sha256
import logging

logger = logging.getLogger(__name__)

# Set your global password here or use an environment variable for security
GLOBAL_PASSWORD = "your_global_password"

def qr_signin(request, auth_token=None):
    auth_token_hashed = Party.get_token_hash(auth_token)
    
    party = Party.objects.get(authentication_token_hash=auth_token_hashed)
    if party is not None:
        login(request, party)
        return redirect('home')  # Redirect to home or another page after login
    return render(request, 'main/signin.html', {'error': 'Invalid name or password.'})

def logout_view(request):
    request.session.flush()
    return redirect('home')

def password_reset_view(request):
    return render(request, 'main/password_reset.html')

@login_required
def home_view(request):
    return render(request, 'main/home.html')

@login_required
def settings_view(request):
    return render(request, 'main/settings.html')

@login_required
def gallery_view(request):
    photos_queryset = GalleryPhoto.objects.order_by('order')
    photos = [
        {
            "url": photo.url, 
            "thumbnail_url": photo.thumbnail_url if photo.thumbnail_url is not None else photo.url, 
            "description": photo.description
        }
        for photo in photos_queryset
    ]
    return render(request, 'main/gallery.html', {'photos': photos})
    
@login_required
def guest_list(request):
    guests = request.user.guests.all()  # Retrieve guests associated with the logged-in party
    return render(request, 'main/guest_list.html', {'guests': guests})

@login_required
def hotel_view(request):
    return render(request, 'main/hotels.html')

@login_required
def rsvp_view(request):
    guests = Guest.objects.filter(party=request.user)
    guest_forms = {}
    event_invite_forms = {}
    suggestion_form = PartySuggestionForm(instance=request.user)  # Initialize the suggestion form

    if request.method == 'POST':
        suggestion_form = PartySuggestionForm(request.POST, instance=request.user)  # Bind the suggestion form
        if suggestion_form.is_valid():
            suggestion_form.save()

        for guest in guests:
            # Handle Guest form (if exists)
            guest_form = GuestUpdateForm(request.POST, instance=guest, prefix=f"guest-{guest.id}")
            if guest_form.is_valid():
                guest_form.save()

            # Handle EventInvite forms
            event_invites = guest.event_invites.all()
            for invite in event_invites:
                form = EventInviteForm(request.POST, instance=invite, prefix=f"invite-{invite.id}")
                if form.is_valid():
                    invite = form.save(commit=False)
                    invite.guest = guest  # Ensure the guest is set
                    invite.save()
                else:
                    logger.warning(f"Form invalid {form}")
        return redirect('rsvp')
    else:
        for guest in guests:
            guest_forms[guest.id] = GuestUpdateForm(instance=guest, prefix=f"guest-{guest.id}")
            event_forms = [
                EventInviteForm(instance=invite, prefix=f"invite-{str(invite.id)}") for invite in guest.event_invites.all()
            ]
            event_invite_forms[guest.id] = event_forms

    return render(request, 'main/rsvp.html', {
        'guests': guests,
        'guest_forms': guest_forms,
        'event_invite_forms': event_invite_forms,
        'suggestion_form': suggestion_form  # Pass the suggestion form to the template
    })

@login_required
def schedule_view(request):
    events = set()
    for guest in Guest.objects.filter(party=request.user):
        for event in guest.event_invites.all():
            events.add(event.event)
    
    return render(request, 'main/schedule.html', {
        'events': events
    })
    
@login_required
def faq_view(request):
    
    return render(request, 'main/faq.html')

@login_required
def registry_view(request):
    return render(request, 'main/registry.html')
