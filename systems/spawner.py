from commands.command import Command
from datetime import datetime, timedelta
from evennia.utils.create import create_object, create_script
from evennia.utils.utils import class_from_module
from systems.command_overrides import CmdCreate
from typeclasses.scripts import Script
from utils.constants import RESPAWN_TIME_DEFAULT, TAG_CATEGORY_BUILDING


class CmdSpawner(Command):
    """
    # TODO: Implement all of the different use cases

    Creates a spawner script that respawns specified objects in a configurable way.
    A single spawner can be associated with multiple different object types,
    in which case they will only respawn if all of the objects in the group are gone.

    Usage:
      @spawner
        lists all spawner scripts in the current location
      @spawner <spawner #>
        lists out details about the given spawner
      @spawner <obj name>[;alias1;alias2] = <class path>
        creates a spawner that immediately starts respawning objects (together)
      @spawner/all
        lists all spawners in the game and their locations.
      @spawner/del <spawner #>
        deletes a spawner by its id in the current room
      @spawner/name <spawner #> = <obj name>
        rename the things a spawner spawns
      @spawner/alias <spawner #> = <alias1, alias2>
        set aliases for the things a spawner spawns
      @spawner/type <spawner #> = <class path>
        change the type of the things a spawner spawns
      @spawner/group <spawner #> = <True/False>
        change whether the spawner waits for all named units before respawning
      @spawner/set <spawner #>/<attr>[ = <value>]
        set or unset what attributes should be present on spawned objects
      @spawner/lock <spawner #> = <lockstring>
        set what locks should be present on spawned objects
      @spawner/lockdel <spawner #>/<access type>
        delete locks that would otherwise be present on spawned objects
    Examples:
      @spawner
      @spawner 1
      @spawner a savage orc;orc;savage = world.npcs.orc.Orc
      @spawner/all
      @spawner/del 0
      @spawner/name 1 = a brutal orc
      @spawner/alias 1 = orc,brute
      @spawner/type 1 = world.npcs.orc.BrutalOrc
      @spawner/group 1 = True
      @spawner/set 1/desc = "A brutal orc stands here."
      @spawner/lock 0 = view:quest(lost kitten, 1)
      @spawner/lockdel 0/view
    """
    key = "@spawner"
    aliases = ["@spawners"]
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not caller.location:
            caller.msg("You need to be in a location to check for spawners.")
            return

        # TODO: All code flows and switches
        if not self.args:
            caller.msg("TODO: Display all spawners in this room")
            return

        # TODO: Set what the spawner makes only if creation was successful
        if not self.switches:
            if self.rhs:
                spawner = create_script(typeclass=Spawner,
                                        key=Spawner.get_key(self.lhs),
                                        obj=caller.location,
                                        interval=5,
                                        start_delay=True,
                                        persistent=True,
                                        autostart=False,
                                        desc="Respawns target on a cadence if target is missing.")
                split_left = self.lhs.split(';')
                spawner.db.spawn_name = split_left[0]
                if len(split_left) > 1:
                    spawner.db.aliases = split_left[1:]
                else:
                    spawner.db.aliases = []
                spawner.db.spawn_type = self.rhs
                spawner.start()
                caller.msg("Successfully started the spawner for: {}".format(self.lhs))
                return
            else:
                caller.msg("@spawner <obj name>[, <obj2 name>...] = <class path>[, <class2 path>...]")
                return


class Spawner(Script):
    @staticmethod
    def get_key(obj_name):
        # Name a spawner based on what it outputs (might not be unique)
        return "spawner_{}".format(obj_name)

    def at_start(self):
        self.ndb.respawn_at = None

        if self.db.spawn_type:
            self.ndb.spawn_class = class_from_module(self.db.spawn_type)
        if not self.db.respawn_time:
            self.db.respawn_time = RESPAWN_TIME_DEFAULT

    def find_target(self):
        room_contents = self.obj.contents_get()

        for obj in room_contents:
            if obj.name == self.db.spawn_name and isinstance(obj, self.ndb.spawn_class):
                return obj

        return None

    def spawn_target(self):
        spawned = create_object(typeclass=self.db.spawn_type,
                                key=self.db.spawn_name,
                                location=self.obj,
                                home=self.obj,
                                aliases=self.db.aliases,
                                locks=CmdCreate.new_obj_lockstring)

        self.ndb.respawn_at = None

    def at_repeat(self):
        if not self.find_target():
            if self.ndb.respawn_at:
                if datetime.now() >= self.ndb.respawn_at:
                    self.spawn_target()
            else:
                self.ndb.respawn_at = datetime.now() + timedelta(seconds=self.db.respawn_time)

    def is_valid(self):
        return (super(Spawner, self).is_valid() and self.ndb.spawn_class and self.db.respawn_time and self.obj and
                self.db.spawn_type and self.db.spawn_name and self.db.aliases is not None)
