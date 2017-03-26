#!/bin/sh
git_access_token=`cat git_access_token.txt`
git_user=xelaadryth
git_repo=larsethia
git_branch=origin/master
target_db=server/evennia.db3
backup_dir=server/backups

# Set up Git
echo Setting Git configurations.
git config --global user.name "auto_puller"
git remote set-url origin https://${git_user}:${git_access_token}@github.com/${git_user}/${git_repo}.git
# Pull branch info
git fetch
git branch --set-upstream-to=${git_branch}

last_datestamp=`date +"%Y%m%d%H%M%S"`

while true
do
    echo Starting polling.
    datestamp=`date +"%Y%m%d%H%M%S"`

    git reset HEAD --hard
    # If the GitHub repo changed at all or a day has passed, backup the db
    if test `git pull -f | wc -l` -gt 1 || test ${datestamp} -gt `expr ${last_datestamp} + 1000000`
    then
        echo Backing up database at ${datestamp}.
        sqlite3 ${target_db} ".backup ${backup_dir}/${datestamp}-evennia.db3.bak"
        last_datestamp=${datestamp}
    else
        echo No backup necessary.
    fi
    sleep 10
done