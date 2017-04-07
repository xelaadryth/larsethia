from commands.command import Command
from typeclasses.scripts import Script
from utils.constants import TAG_CATEGORY_BUILDING


class CmdSpawner(Command):
    """
    Creates a spawner script that respawns specified objects in a configurable way.

    Usage:
      @spawner
      @spawner <spawner #>
      @spawner <obj name>[, <obj2 name>...] = <class path>[, <class2 path>...]
      @spawner/all
      @spawner/del <spawner #>
      @spawner/set <spawner #>/<attr> = <value>
    Example:
      @spawner
      @spawner 1
      @spawner a savage orc = world.npcs.orc.Orc
      @spawner/all
      @spawner/del 0
      @spawner/set 1/name = a brutal orc
      @spawner/set 0/interval = 5

    @spawner - lists all spawner scripts in the current location.
    @spawner <obj name> = <class path> - Creates a spawner that immediately starts spawning objects.
    @spawner/all - lists all spawners in the game and their locations.
    @spawner/set - removes all idle text from an object.
    TODO: List out all the things you can set on a spawner
    """
    key = "@spawner"
    aliases = ["@spawners"]
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        # TODO: All code flows and switches
        if not self.args:
            # Display all spawners in this room
            return

        caller.execute_cmd("@create {}:systems.spawner.Spawner".format(self.args))
        # TODO: Set what the spawner makes only if creation was successful


class Spawner(Script):
    @staticmethod
    def get_key(obj):
        # Spawners are attached to their locations. This key is not unique (multiple spawners may have the same
        # key if they are in the same location) which is fine since true equality is by script dbref
        return "spawner_{}".format(obj.id)

    def at_script_creation(self):
        # This script should always be attached to a location (or container) that we will spawn things in
        self.key = self.get_key(self.obj)
        self.desc = "Respawns things automatically."
        # Don't message right off the bat
        self.start_delay = True
        self.interval = 5
        self.persistent = True

    def at_repeat(self):
        pass