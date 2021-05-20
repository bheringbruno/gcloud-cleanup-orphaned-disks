import sys, json, argparse, os
import subprocess as sp
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def check_args(parser):
    parser.add_argument("--project", help="a valid project name", type = str.lower )
    parser.add_argument("--channel", help="slack channel id", type = str)
    parser.add_argument("--slack-token", help="slack bot token", type = str)
    parser.add_argument("--days-ago", help="removes snapshots created before 'days ago' (Default: 10)", type=int, default=10 )
    parser.add_argument("--dry-run", help="print the command without run", action='store_true')
    args = parser.parse_args()
    return args

# Add label for zone orphaned disks 
def add_pending_delete(diskname,zone):
    pending_delete.append(diskname)
    label_zone = 'gcloud compute disks add-labels ' + diskname + ' --zone='+ zone +' --labels=deleted_status=pending_delete'
    if args.dry_run:
        print('DRY-RUN | Pending delete disk: '+ diskname)
    else:
        print('Updating label '+ diskname)
        os.system(label_zone)

# Add label for regional orphaned disks 
def add_pending_region_delete(diskname,region):
    pending_delete.append(diskname)
    label_region = 'gcloud compute disks add-labels ' + diskname + ' --region='+ region +' --labels=deleted_status=pending_delete'
    if args.dry_run:
        print('DRY-RUN | Pending delete disk: '+ diskname)
    else:
        print('Updating label '+ diskname)
        os.system(label_region)

# Delete zone orphaned disks
def delete_orphaned_disks(diskname,zone):
    deleted_disks.append(diskname)
    snapshot_zone = 'gcloud compute disks snapshot '+ diskname +' --zone='+ zone +'  --snapshot-names='+ diskname +'  --labels=status='+snap_label
    delete_zone = 'gcloud compute disks delete ' + diskname +' --zone='+ zone +' --quiet'
    if args.dry_run:
        print('DRY-RUN | Snapshot and Delete disk: '+ diskname)
    else:
        print('Snapshoting and Deleting '+ diskname +' on zone ' +zone)
        os.system(snapshot_zone)
        os.system(delete_zone)

# Delete regional orphaned disks
def delete_orphaned_region_disks(diskname,region):
    deleted_disks.append(diskname)
    snapshot_region = 'gcloud compute disks snapshot '+ diskname +' --region='+ region +'  --snapshot-names='+ diskname +'  --labels=status='+snap_label
    delete_region = 'gcloud compute disks delete ' + diskname +' --region='+ region +' --quiet'
    if args.dry_run:
        print('DRY-RUN | Disk to be snapshot and delete: '+ diskname)
    else:
        print('Snapshoting and Deleting '+ diskname +' on zone ' +region)
        os.system(snapshot_region)
        os.system(delete_region)

# Send slack message with label and delete orphaned disks 
def slack_msg():
    if args.dry_run:
        print("DRY-RUN | Slack message is disabled on dry-run")
    else:
        if len(pending_delete) > 0:
            msg = json.dumps([{"text":separator.join(pending_delete),"color":"warning"}])
            response = client.chat_postMessage(channel=args.channel, text='*Pending Delete Orphaned Disks - ('+args.project+')*\nPlease check and delete them.', attachments=msg)
        if len(deleted_disks) > 0:
            msg = json.dumps([{"text":separator.join(deleted_disks),"color":"danger"}])
            response = client.chat_postMessage(channel=args.channel, text='*Deleted Orpahaned Disks - ('+args.project+')*\nSnapshot created for all deleted disks and stored for '+str(args.days_ago)+' days.\n', attachments=msg)

# Delete old snapshots (older than N_DAYS_AGO)
def delete_old_snapshots():
    command = sp.getoutput('gcloud compute snapshots list --filter="labels.status:('+snap_label+')" --format=json')
    try:
        s = json.loads(command)
        for i in s:
            d1 = i['creationTimestamp'].split('.')
            d2 = datetime.strptime(d1[0], "%Y-%m-%dT%H:%M:%S")
            if d2 < n_days_ago:
                if args.dry_run:
                    print('DRY-RUN | SNAPSHOT WILL BE DELETED: '+i['name'])
                else:
                    print('Deleting Snapshot: '+i['name'])
                    os.system('gcloud compute snapshots delete '+ i['name'])
    except:
        print("\nThere isnt snapshot to cleanup.")

# Find orphaned disks without labels and pending delete ones
def main():
    x = json.loads(cmd)
    for i in x:
        try:
             if i['labels']:
                for k,v in i['labels'].items():
                    if k == "deleted_status":
                        if v == "pending_delete":  
                            try:
                                delete_orphaned_disks(i['name'],i['zone'].rpartition('/')[2])
                            except KeyError: 
                                delete_orphaned_region_disks(i['name'],i['region'].rpartition('/')[2])
        except KeyError:
            try:
                add_pending_delete(i['name'],i['zone'].rpartition('/')[2])
            except KeyError:
                add_pending_region_delete(i['name'],i['region'].rpartition('/')[2])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = check_args(parser)
    login = sp.getoutput('gcloud config set project '+args.project)
    cmd = sp.getoutput('gcloud compute disks list --format=json --filter="users:(NULL)"  --sort-by=name')
    client = WebClient(token=args.slack_token)
    pending_delete = []
    deleted_disks = []
    separator = '\n'
    today = datetime.now()
    N_DAYS_AGO = args.days_ago
    n_days_ago = today - timedelta(days=N_DAYS_AGO)
    timestamp = today.strftime("%d%m%Y%H%M%S")
    snap_label = "orphaned"
    # log_file = '/tmp/'+args.project+'-'+timestamp+'.log'
    # log = open(log_file, "a")
    # sys.stdout = log
    # sys.stderr = log
    main()
    delete_old_snapshots()
    slack_msg()
    # log.close()
    # upload_file = sp.getoutput('gsutil cp '+log_file+' gs://gcloud-cleanup-logs/cleanup-orphaned-disks')