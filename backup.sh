#!/bin/sh
git_access_token=`cat git_access_token.txt`
git_user=xelaadryth
git_repo=larsethia
git_branch=origin/master

# Set up Git
git config --global user.name "auto_puller"
git remote set-url origin https://${git_user}:${git_access_token}@github.com/${git_user}/${git_repo}.git
# Let the remote get added
git fetch
git branch --set-upstream-to=${git_branch}

last_datestamp=`date +"%Y%m%d%H%M%S"`

while true
do
    datestamp=`date +"%Y%m%d%H%M%S"`

    cd ${update_dir}
    git reset HEAD --hard
    # If the GitHub repo changed at all or a day has passed, backup the db
    if test `git pull -f | wc -l` -gt 1 || test ${datestamp} -gt `expr ${last_datestamp} + 1000000`
    then
        echo Backing up database at ${datestamp}.
        sqlite3 ${target_file} ".backup ${backup_directory}/${datestamp}-evennia.db3.bak"
        cd ${backup_dir}
        git add .
        git commit -m "Backing up database at ${datestamp}."
        git push origin master -f
        last_datestamp=${datestamp}
    else
        echo No backup necessary.
    fi
    sleep 10
done