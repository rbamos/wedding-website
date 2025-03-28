# A website for your wedding

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/rbamos/wedding-website">Wedding Website</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://www.ryan-b-amos.com/">Ryan Amos</a> is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC-SA 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" alt=""></a></p> 

This reposistory is intended to help you share your exciting announcement with your friends, manage dissimination of details, and collect RSVPs without having your data sold to brokers.

# Local development setup

```bash
python -m venv venv
./venv/scripts/activate
cd wedding_website
./manage.py migrate
./manage.py runserver
```

# Deployment
1. Install Terraform
2. Create an SSH key pair in AWS
3. Create an IAM Role for Terraform and create access keys 
4. Create `terraform/secrets/db_password.txt`, `terraform/secrets/django_secret_key.txt`, and `id_ed25519` (read-only
    deploy key to clone your repo)
5. Update the repository URL
6. Modify other values as appropriate
7. Deploy the infrastructure via Terraform:

```bash
cd terraform

# Create the S3 backend
# Destroying this backend will destroy your Terraform state for the rest of the infrastructure
cd backend
terraform init
terraform apply

# Create the server
cd ..
terraform init
terraform apply
```

# Updates
Infrastructure updates can be applied via `terraform apply`

Software updates can be applied via `git pull` and `systemctl restart httpd`


# Security notes
## Github private forks aren't private
Private forks of repos aren't really private. Read 
[this blog post](https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github) to learn more.

Creating a fresh repo with a full copy of the contents of this repo is recommended.

## Managing secrets
It's important to make sure you don't commit any secrets to the repository. If you need to upload additional secrets
beyond what's designed here, modify the `secrets` module in `terraform/` to do so. See the pattern for secrets like the
SSH key and Django secret key for how to load secrets off the filesystem without committing them to the repo.

##  QR Code security
The QR Code authentication option has some security tradeoffs with password authentication. The QR code is effectively a
static password; if an attacker aquires the QR code, for example by taking a picture, they will be able to impersonate
the user.

The QR code will submit a GET request -- this means a shoulder-surfer, someone who observes browser history at a later
date, or a network eavesdropper may be able to impersonate as the user. The use of TLS can help mitigate the network
eavesdropper risk.

No salt is used, since the QR codes are randomly generated; a salt is typically useful to prevent brute force or
dictionary attacks, but the tokens are of sufficient entropy that such attacks are not viable.

# Advanced setup
## Setting up Cloudfront access in local development
Update the hardcoded bucket and cloudfront domain settings in `settings.py` and add your AWS key to your environment.