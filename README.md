# Welcome to Larsethia!
## How to Play
Just connect to the game at http://larsethia.themud.org/ by hitting the "Play Online" tab at the top. To log out, go back to the main page and click "Log Out" in the top-right.

## How to Dev
1. Follow the instructions to install https://github.com/evennia/evennia and get a sample initialized game server running to undertstand the flow
2. At the base directory of the Evennia repo, git clone this one (and add it to your Evennia `.gitignore`)
3. `cd` into the new `larsethia` directory and start the Evennia server locally with `evennia.bat --initsettings` (generates settings.py), `evennia.bat migrate` (initializes sqlite DB), and `evennia.bat start` to start the server and prompt creation of a superuser. Make sure to do this with a TTY-enabled terminal, for instance `cmd.exe` or using `winpty` if using `bash` on Windows
4. With this you can get started in your local sandbox environment, or message me and I can figure out how to get the most up-to-date `settings.py` and `evennia.db3` files to you
5. Any changes pushed to this Git repo get cloned to the production server every 10 seconds and backs up the DB (locally on EC2), you just need to call `@reload` in the game to propagate code changes

## EC2 Set-up Instructions
1. Start an EC2 instance on AWS with TCP to port 80 (web), TCP to port 22 (SSH), TCP to port 4000 (for Telnet), and TCP to port 8001 (webclient socket)
2. `sudo git clone https://github.com/xelaadryth/larsethia.git /usr/src/larsethia`
3. Locally execute `push_db.sh` and `push_settings.sh` to `scp` your `evennia.db3` and `settings.py` over to EC2, and then move them to their respective locations manually
4. Locally execute `push_aws_creds.sh` to `scp` your AWS credentials to EC2 (requires AWS CLI installed and `aws configure` executed with valid secrets)
5. Install dependencies
6. `sudo docker-compose -f docker-compose-server.yml up -d --build` to enable auto-pull from Git and run all of the docker containers in daemon mode
7. (Optional) `docker-compose logs -f` to show live output

## To Do
- Skills, and make Mirienne's quest increase perception skill
- Create a "map" command that crawls nearby rooms with traverse privileges and generates an ASCII map
- Create a command to list all tags used in the game
- Create a command to examine scripts
- Create a command to set attributes on scripts
- Fix bug where if you look at an object that has "view" locked, it gives you the name of the object
  - Affects anything that uses generic search since both player and admin commands use the same search
  - Player commands should only ever attempt viewable objects
- Smarter targeting
  - Should perform action if only one legal target, but on no legal targets should show error for the first illegal one
- Change the template and regexp for generic search util to use "box 1" instead of "1-box" syntax
- Standardize a process for unit tests
- Containers as locks (if lock container not set, not treated as container. If lock access is true, the player has permission to access the container's contents.) **[Jobin]**
  - "get book from chest"
  - "put book in chest"
  - Prevent people from doing "get book from That NPC"
  - Prevent people from doing "get book from Some Player"
  - Address parsing issues such as an NPC named "Lara from Briskell" and then "get book from Lara from Briskell" (splitting on first/last instance of " from " or " in " is not guaranteed)
- Combat system **[Eric]**
  - Most likely tick-based (2-3 second rounds)
  - Stats feed into a formula for base damage dealt
  - Active abilities to give options in combat
- Design a play experience (What's the main goals and focus of the game? Story-driven/combat-driven/exploration-driven?) **[Eric]**
- Come up with a storyline **[Eric]**
- Decide on game systems and then add them to the to-do list when ready to be implemented
