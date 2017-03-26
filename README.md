# Welcome to Larsethia!
## EC2 Set-up Instructions
1. Clone this repo as a submodule of `evennia/evennia`
2. Start the Evennia server locally with `evennia.bat migrate` and `evennia.bat start` to create the initial db superuser and server settings file.
3. Start an EC2 instance on AWS with web access to port 80, TCP to port 4000 (for Telnet)
4. `sudo git clone https://github.com/xelaadryth/larsethia.git /usr/src/larsethia`
5. Generate an OAuth access token on GitHub with repository read permissions and put it in `git_access_token.txt` at the top-level
6. Locally execute `push_db.sh` and `push_settings.sh` to `scp` necessary files over to EC2
7. Install dependencies (`docker`, `docker-compose (v1)`)
8. `sudo docker-compose up`

## To Do
- Come up with a to-do list
