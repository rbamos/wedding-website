#!/bin/bash

# Source the secrets
source /etc/secrets

# Define the database path and backup file name
DB_PATH="/var/www/WeddingWebsite/wedding_website/db.sqlite3"
BACKUP_FILE="/tmp/hourly_db_backup_$(date +%Y%m%d%H%M%S).sqlite3"

# Vacuum the database and create a backup
sqlite3 $DB_PATH "VACUUM INTO '$BACKUP_FILE';"

# Upload the backup to the S3 bucket
aws s3 cp $BACKUP_FILE s3://$SQLITE_BACKUP_BUCKET/backups/

# Remove the local backup file
rm $BACKUP_FILE

# Retention strategy:
# We retain the newest and oldest backup from the last day
# Once the oldest backup is a day old, we change the prefix to daily
# We delete any daily backups that are neither the oldest nor newest
# We retain the newest and oldest backup from the last week
# Once the oldest backup is a week old, we delete it
# We delete any weekly backups that are neither the oldest nor newest

# Define the S3 bucket and prefixes
S3_BUCKET="s3://$SQLITE_BACKUP_BUCKET/backups"
HOURLY_PREFIX="hourly_db_backup_"
DAILY_PREFIX="daily_db_backup_"
WEEKLY_PREFIX="weekly_db_backup_"

# Get the list of backups from S3
BACKUPS=$(aws s3 ls $S3_BUCKET/ | awk '{print $4}')

# Function to get the timestamp from the backup filename
get_timestamp() {
    echo $1 | grep -oP '\d{14}'
}

# Function to convert the timestamp to a format recognized by the date command
convert_timestamp() {
    local timestamp=$1
    echo "${timestamp:0:4}-${timestamp:4:2}-${timestamp:6:2} ${timestamp:8:2}:${timestamp:10:2}:${timestamp:12:2}"
}

# Function to move a backup to a new prefix
move_backup() {
    local old_prefix=$1
    local new_prefix=$2
    local backup=$3
    aws s3 mv "$S3_BUCKET/$backup" "$S3_BUCKET/${backup/$old_prefix/$new_prefix}"
}

# Function to delete a backup
delete_backup() {
    local backup=$1
    aws s3 rm "$S3_BUCKET/$backup"
}

# Process hourly backups
hourly_backups=($(echo "$BACKUPS" | grep "$HOURLY_PREFIX"))
if [ ${#hourly_backups[@]} -gt 0 ]; then
    oldest_hourly_backup=${hourly_backups[0]}
    newest_hourly_backup=${hourly_backups[-1]}
    for backup in "${hourly_backups[@]}"; do
        if [ "$backup" != "$oldest_hourly_backup" ] && [ "$backup" != "$newest_hourly_backup" ]; then
            delete_backup "$backup"
        fi
    done
    oldest_hourly_timestamp=$(convert_timestamp "$(get_timestamp $oldest_hourly_backup)")
    if [ $(($(date +%s) - $(date +%s -d "$oldest_hourly_timestamp"))) -ge 86400 ]; then
        move_backup "$HOURLY_PREFIX" "$DAILY_PREFIX" "$oldest_hourly_backup"
    fi
fi

# Process daily backups
daily_backups=($(echo "$BACKUPS" | grep "$DAILY_PREFIX"))
if [ ${#daily_backups[@]} -gt 0 ]; then
    oldest_daily_backup=${daily_backups[0]}
    newest_daily_backup=${daily_backups[-1]}
    for backup in "${daily_backups[@]}"; do
        if [ "$backup" != "$oldest_daily_backup" ] && [ "$backup" != "$newest_daily_backup" ]; then
            delete_backup "$backup"
        fi
    done
    oldest_daily_timestamp=$(convert_timestamp "$(get_timestamp $oldest_daily_backup)")
    if [ $(($(date +%s) - $(date +%s -d "$oldest_daily_timestamp"))) -ge 604800 ]; then
        move_backup "$DAILY_PREFIX" "$WEEKLY_PREFIX" "$oldest_daily_backup"
    fi
fi

# Process weekly backups
weekly_backups=($(echo "$BACKUPS" | grep "$WEEKLY_PREFIX"))
if [ ${#weekly_backups[@]} -gt 0 ]; then
    oldest_weekly_backup=${weekly_backups[0]}
    newest_weekly_backup=${weekly_backups[-1]}
    for backup in "${weekly_backups[@]}"; do
        if [ "$backup" != "$oldest_weekly_backup" ] && [ "$backup" != "$newest_weekly_backup" ]; then
            delete_backup "$backup"
        fi
    done
fi
