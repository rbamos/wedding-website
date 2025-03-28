#!/bin/bash

source /etc/secrets

# Fetch the current instance ID dynamically
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

setup_zone() {
    # Fetch the public IP address of the current instance
    PUBLICIP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)

    if [ -z "$PUBLICIP" ]; then
        echo "Error: Unable to retrieve the public IP address."
        exit 1
    fi

    # Check if the public IP is already set in the hosted zone
    aws route53 list-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID | grep "$PUBLICIP" &> /dev/null
    if [ $? == 0 ]; then
        echo "Public IP $PUBLICIP is already set for $HOSTNAME."
        exit 0
    fi

    # Create the JSON payload for the Route 53 API
    cat << EOF > /tmp/dns.json
{
  "Comment": "Update IP address for $HOSTNAME",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "$HOSTNAME",
        "Type": "A",
        "TTL": 30,
        "ResourceRecords": [
          {
            "Value": "$PUBLICIP"
          }
        ]
      }
    }
  ]
}
EOF

    # Update the Route 53 hosted zone
    aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file:///tmp/dns.json
    if [ $? == 0 ]; then
        echo "Successfully updated $HOSTNAME to $PUBLICIP."
    else
        echo "Error: Failed to update the Route 53 record."
        exit 1
    fi

    # Clean up the temporary JSON file
    rm -f /tmp/dns.json
}

# Execute the function
setup_zone
