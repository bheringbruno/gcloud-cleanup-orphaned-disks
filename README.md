## Gcloud Delete Orphaned Disks

This repository creates a CronJob on Kubernetes to check all orphaned disks twice a week (tue and thu) and add labels based on severity, sending a notification to a channel and remove them. 
There are 2 (two) steps, after the last one all orphaned disks that remain will be removed.

### label:

{
    "deleted_status" : "pending_delete" 
}

### Steps:
**1 - pending_delete: **
All orphaned disks without labels will be labeled with "pending_delete" value. 
Also will send a notify to a Slack Channel. The Team should check and delete them to save costs.
#

**2 - deleted: **
On the next execution all orphaned disks remain will be created a snapshot and then remove it. Also a new notification with deleted orphaned disks will be sending to a Slack Channel

#
### Snapshots:
All Snaphots name will be the disk name with label {"status": "orphaned"} and stored for 10 days (Default).

## Usage:
#

```
python3 main.py --help

usage: main.py [-h] [--project PROJECT] [--channel CHANNEL] [--slack-token SLACK_TOKEN] [--days-ago DAYS_AGO] [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  --project PROJECT     a valid project name
  --channel CHANNEL     slack channel id
  --slack-token SLACK_TOKEN
                        slack bot token
  --days-ago DAYS_AGO   removes snapshots created before 'days ago' (Default: 10)
  --dry-run             print the command without run
```

### Default:  
#
```
python3 main.py --slack-token $SLACK_API_TOKEN --channel $CHANNEL_ID  --project tvg-network
```

## Slack Config:
#
```
Default Channel: #gcloud-cleanup
Default bot user: gcloud-bot-ops
```