#!/bin/bash
git_user=xelaadryth
git_repo=larsethia
git_branch=origin/master
target_db=server/evennia.db3
backup_dir=server/backups
base_dir=/usr/src/larsethia

if [ -z "${poll_git_backup}" ]
then
    echo Local run detected, not auto-pulling from Git.
    exit 0
fi
echo Server run detected, will auto-pull from Git.

git_access_token=`cat git_access_token.txt`

cd ${base_dir}

# Set up Git
echo Setting Git configurations.
git config --global user.name "auto_puller"
git remote set-url origin https://${git_user}:${git_access_token}@github.com/${git_user}/${git_repo}.git
# Pull branch info
git fetch
git branch --set-upstream-to=${git_branch}

last_datestamp=`date +"%Y%m%d%H%M%S"`

echo Git configured. Starting polling.
while true
do
    datestamp=`date +"%Y%m%d%H%M%S"`

    git reset HEAD --hard
    # If the GitHub repo changed at all or a day has passed, backup the db
    if test `git pull -f | wc -l` -gt 1
    then
        echo Changes detected, backing up database at ${datestamp}.
        sqlite3 ${target_db} ".backup ${backup_dir}/${datestamp}-evennia.db3"
        last_datestamp=${datestamp}
    elif test ${datestamp} -gt `expr ${last_datestamp} + 1000000`
    then
        echo Time elapsed, backing up database at ${datestamp}.
        sqlite3 ${target_db} ".backup ${backup_dir}/${datestamp}-evennia.db3"
        last_datestamp=${datestamp}
    else
        echo No backup necessary.
    fi
    sleep 10
done