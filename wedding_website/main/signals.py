from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Party, Guest, EventInvite, Event
import logging
import boto3
from wedding_website import settings

logger = logging.getLogger(__name__)

@receiver(m2m_changed, sender=Party.events.through)
def create_event_invites(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        guests = Guest.objects.filter(party=instance)
        for event_id in pk_set:
            event = Event.objects.get(id=event_id)
            for guest in guests:
                EventInvite.objects.create(guest=guest, event=event)
    elif action == "post_remove":
        # Removing events from the party
        guests = Guest.objects.filter(party=instance)
        for event_id in pk_set:
            event = Event.objects.get(id=event_id)
            EventInvite.objects.filter(guest__in=guests, event=event).delete()

@receiver(post_save, sender=EventInvite)
def update_guest_attending(sender, instance, created, raw, using, update_fields, **kwargs):
    guest = instance.guest
    attending_any_event = guest.event_invites.filter(attending=True).exists()
    
    # Only update if there is a change to reduce database hits
    if guest.attending != attending_any_event:
        guest.attending = attending_any_event
        guest.save()

    attending_mod = "" if instance.attending else "not "
    logger.info(f"{guest} is {attending_mod}attending {instance.event.name}")

    # The backup bucket is only used in production
    if settings.DEBUG:
        return

    # Upload a json file with the EventInvite and Guest information to S3
    s3 = boto3.client('s3')
    bucket_name = settings.SQLITE_BACKUP_BUCKET

    filename = f"rsvp/{instance.id}.json"
    data = {
        "guest": guest.name,
        "event": instance.event.name,
        "attending": instance.attending,
        "meal": instance.meal.name if instance.meal else None
    }
    s3.put_object(Bucket=bucket_name, Key=filename, Body=str(data).encode())
    