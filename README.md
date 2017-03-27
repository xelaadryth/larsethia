# Welcome to Larsethia!
## How to Play
Just connect to the game at http://ec2-34-208-236-184.us-west-2.compute.amazonaws.com/ by hitting the "Play Online" tab at the top. To log out, go back to the main page and click "Log Out" in the top-right.

## How to Dev
1. Follow the instructions to install https://github.com/evennia/evennia
2. At the base directory of the Evennia repo, git clone this one (and add it to your Evennia `.gitignore`)
3. `cd` into the new `larsethia` directory and start the Evennia server locally with `evennia.bat --initsettings`, `evennia.bat migrate`, and `evennia.bat start` to create the server settings file, initial db, and create a superuser (admin). Make sure to do this with a TTY-enabled terminal, for instance `cmd.exe` or using `winpty` if using `bash` on Windows
4. With this you can get started in your local sandbox environment, or message me and I can figure out how to get the most up-to-date `settings.py` and `evennia.db3` files to you
5. Any changes pushed to this Git repo get cloned to the production server every 10 seconds and backs up the DB, you just need to call `@reload` in the game to propagate code changes

## EC2 Set-up Instructions
1. Start an EC2 instance on AWS with web access to port 80, TCP to port 4000 (for Telnet)
2. `sudo git clone https://github.com/xelaadryth/larsethia.git /usr/src/larsethia`
3. Generate an OAuth access token on GitHub with repository read permissions and put it in `git_access_token.txt` at the top-level
4. Locally execute `push_db.sh` and `push_settings.sh` to `scp` your `evennia.db3` and `settings.py` over to EC2, and then move them to their respective locations manually
5. Install dependencies
6. Set environment variable `poll_git_backup=true`
7. `sudo docker-compose up -d`

## To Do
- Consider undoing inheritance from Object and using a shared function instead
- Command to build exits to existing rooms with the same syntax as `@dig`
- Containers as locks
