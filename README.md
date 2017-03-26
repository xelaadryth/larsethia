# Welcome to Larsethia!
## Set-up Instructions
1. Start an EC2 instance on AWS with web access to port 80, TCP to port 4000
2. `sudo git clone https://github.com/xelaadryth/larsethia.git /usr/src/larsethia`
2. Generate an OAuth access token on GitHub with repository read permissions and put it in `git_access_token.txt` at the top-level
3. Set the environment variables listed in `set_env_vars.sh` and run `source set_env_vars.sh` both locally and on EC2. Do NOT put secrets into the script or it will be synced to GitHub
4. Locally execute `scp.sh` to `scp` necessary files over to EC2
5. Install dependencies (`docker`, `docker-compose (v1)`)
6. `sudo docker-compose up`

## To Do
- Come up with a to-do list
