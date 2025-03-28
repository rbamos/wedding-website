import csv
import random
import os
from main.models import Party, Guest, Event, EventInvite
from main.qr_code_utils import create_auth_qr
from django.conf import settings
import os
import tempfile
import urllib.request
import datetime
import base64

# Usage:
# Call `import_guests(input_csv, output_csv)` from the Django shell.
# Example:
# from bin.import_guests import import_guests
# import_guests('path/to/input.csv', 'path/to/output.csv')
# The input CSV file should have the following columns:
# Party Name (Login), First, Last, <event_name>, <event_name>, ...
# The output 

secure_random = random.SystemRandom()

EFF_WORDLIST_URL = "https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt"
# Create a temporary file for the wordlist
temp_dir = tempfile.gettempdir()
EFF_WORDLIST_PATH = os.path.join(temp_dir, 'eff_large_wordlist.txt')

# Download the wordlist if it doesn't exist
urllib.request.urlretrieve(EFF_WORDLIST_URL, EFF_WORDLIST_PATH)
with open(EFF_WORDLIST_PATH, 'r') as f:
    WORDLIST = [line.split()[1] for line in f.readlines()]

def generate_password():
    """Generate a 5-word random password using EFF's word list."""
    return ' '.join(WORDLIST[secure_random.randint(0, len(WORDLIST) - 1)] for _ in range(5))

def import_guests(input_csv, output_csv):
    """Import guests from a CSV file and create Party, Guest, EventInvite objects, and QR codes."""
    event_default = {
        "date": datetime.date.today(),
        "location": "TBD",
        "about": "TBD"
    }

    parties = []
    output_html = 'party_cards.html'

    with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        
        event_columns = [col for col in reader.fieldnames if col not in ['Party Name (Login)', 'First', 'Last']]
    
        events = {
            event_name: Event.objects.get_or_create(name=event_name, defaults=event_default)[0]
            for event_name in event_columns
        }

        for row in reader:
            # Check if the party exists, otherwise create it
            party, created = Party.objects.get_or_create(
                name=row['Party Name (Login)'],
                defaults={
                    'email': f"{row['Party Name (Login)']}@{settings.HOSTNAME}",
                    'password': generate_password()
                }
            )
            if created:
                
                # Generate QR code for the party
                qr_code_path = create_auth_qr(email=party.email, hostname=settings.HOSTNAME)
                
                parties.append({
                    'name': party.name,
                    'password': party.password,
                    'qr_code_url': qr_code_path,
                    'guests': []
                })

            # Create Guest
            guest = Guest.objects.create(
                party=party,
                name=f"{row['First']} {row['Last']}",
                attending=False
            )

            # Search backwards since the newest party is most likely to match
            for p in reversed(parties):
                if p['name'] == party.name:
                    p['guests'].append({'name': row['First']})
                    break

            # Create EventInvites
            for event_name, attending in events.items():
                if row[event_name].strip().lower() == 'yes':
                    EventInvite.objects.create(
                        guest=guest,
                        event=attending,
                        attending=False
                    )

    # Write the contents of the parties variable to the output CSV after processing
    with open(output_csv, 'a', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Party Name (Login)', 'Password', 'Guests', 'QR Code'])
        for party in parties:
            writer.writerow([
                party['name'], party['password'], ', '.join([guest['name'] for guest in party.get('guests')]),
                party['qr_code_url']
                ]
            )

    generate_cards_html(output_html, parties)
    return parties


def generate_cards_html(output_html, parties):
    """Generate an HTML file with cards for each party."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Party Cards</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .card {
                width: 3.5in;
                margin: 10px;
                text-align: center;
                page-break-inside: avoid;
            }
            .grid {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="grid">
    """

    for party in parties:
        with open(party['qr_code_url'], "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            data_uri = f"data:image/png;base64,{encoded_string}"
        
        guest_names = ', '.join([guest['name'] for guest in party.get('guests')])
        html_content += f"""
            <div class="card" style="flex: 0 0 calc(50% - 20px); border: none;">
            <div class="card-body">
            <h5 class="card-title mb-1"><strong>Guests:</strong> {guest_names}</h5>
            <p class="card-text mb-0"><strong>URL:</strong> {settings.HOSTNAME}</p>
            <p class="card-text mb-0"><strong>Username:</strong> {party['name']}</p>
            <p class="card-text mb-0"><strong>Password:</strong> {party['password']}</p>
            <img src="{data_uri}" alt="QR Code" width="225" class="img-fluid">
            </div>
            </div>
        """

    html_content += """
            </div>
        </div>
    </body>
    </html>
    """

    # Write the HTML content to the output file
    with open(output_html, 'w') as f:
        f.write(html_content)