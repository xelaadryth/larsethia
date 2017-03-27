# Welcome to Larsethia!
## How to Play
Just connect to the game at http://ec2-34-208-236-184.us-west-2.compute.amazonaws.com/ by hitting the "Play Online" tab at the top. To log out, go back to the main page and click "Log Out" in the top-right.

## EC2 Set-up Instructions
1. Clone this repo as a submodule of `evennia/evennia`
2. Start the Evennia server locally with `evennia.bat --initsettings`, `evennia.bat migrate`, and `evennia.bat start` to create the initial db, create a superuser, and server settings file.
3. Start an EC2 instance on AWS with web access to port 80, TCP to port 4000 (for Telnet)
4. `sudo git clone https://github.com/xelaadryth/larsethia.git /usr/src/larsethia`
5. Generate an OAuth access token on GitHub with repository read permissions and put it in `git_access_token.txt` at the top-level
6. Locally execute `push_db.sh` and `push_settings.sh` to `scp` necessary files over to EC2, and then move them to their respective locations
7. Install dependencies (`docker`, `docker-compose (v1)`)
8. Set `poll_git_backup=true`
9. `sudo docker-compose up -d`

## To Do
- Consider undoing inheritance from Object and using a shared function instead
- Command to build exits to existing rooms with the same syntax as `@dig`
- Containers as locks
