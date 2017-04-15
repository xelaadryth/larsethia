from commands.command import Command
from datetime import datetime, timedelta
from evennia.utils.create import create_object, create_script
from evennia.utils.evtable import EvTable
from evennia.utils.search import search_script_tag
from evennia.utils.utils import class_from_module
from systems.command_overrides import CmdCreate
from typeclasses.scripts import Script
from utils.constants import RESPAWN_TIME_DEFAULT, TAG_CATEGORY_BUILDING


SPAWNER_TAG = "spawner"


class CmdSpawner(Command):
    """
    # TODO: Implement all of the different use cases

    Creates a spawner script that respawns specified objects in a configurable way.
    A single spawner can be associated with multiple different object types,
    in which case they will only respawn if all of the objects in the group are gone.

    Usage:
      @spawner
        lists all spawner scripts in the current location
      @spawner <script #>
        lists out details about the given spawner
      @spawner <obj name>[;alias1;alias2] = <class path>
        creates a spawner that immediately starts respawning objects (together)
      @spawner/all
        lists all spawners in the game and their locations.
      @spawner/del <script #>
        deletes a spawner by its script id
      @spawner/name <script #> = <obj name>
        rename the things a spawner spawns
      @spawner/alias <script #> = <alias1, alias2>
        set aliases for the things a spawner spawns
      @spawner/type <script #> = <class path>
        change the type of the things a spawner spawns
      @spawner/set <script #>/<attr>[ = <value>]
        set or unset what attributes should be present on spawned objects
      @spawner/lock <script #> = <lockstring>
        set what locks should be present on spawned objects
      @spawner/lockdel <script #>/<access type>
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
      @spawner/set 1/desc = "A brutal orc stands here."
      @spawner/lock 0 = view:quest(lost kitten, 1)
      @spawner/lockdel 0/view
    """
    key = "@spawner"
    aliases = ["@spawners"]
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def func(self):
        if 'all' in self.switches:
            spawners = search_script_tag(SPAWNER_TAG, TAG_CATEGORY_BUILDING)

            if len(spawners) == 0:
                self.caller.msg("No spawners exist.")
                return

            table = EvTable("Scr #", "Spawn Name", "Loc #", "Location", "Respawn", border="cells")
            for spawner in spawners:
                if spawner.obj:
                    location_dbref = spawner.obj.dbref
                    location_key = spawner.obj.key
                else:
                    location_dbref = "N/A"
                    location_key = "No Location"
                respawn_indicator = spawner.respawn_timer()
                table.add_row(spawner.dbref, spawner.db.spawn_name, location_dbref, location_key, respawn_indicator)
            output = "|wSpawners by location:|n\n{}".format(table)
            self.caller.msg(output)

            return

        caller = self.caller
        if not caller.location:
            caller.msg("You need to be in a location to check for spawners.")
            return

        if not self.args:
            # List out details for all spawners in the current room
            spawners = []
            for script in caller.location.scripts.all():
                if isinstance(script, Spawner):
                    spawners.append(script)

            if len(spawners) == 0:
                self.caller.msg("No spawners are present in this location.")
                return

            # TODO: Add details to this view
            table = EvTable("Scr #", "Spawn Name", "Typeclass", "Aliases", "Respawn", border="cells")
            for spawner in spawners:
                respawn_indicator = spawner.respawn_timer()
                if spawner.db.aliases:
                    aliases = ",".join(spawner.db.aliases)
                else:
                    aliases = ""
                table.add_row(spawner.dbref, spawner.db.spawn_name, spawner.db.spawn_type, aliases,
                              respawn_indicator)
            output = "|wSpawners in this location:|n\n{}".format(table)
            self.caller.msg(output)

            return

        # TODO: Set what the spawner makes only if creation was successful
        if not self.switches:
            if self.rhs:
                try:
                    class_from_module(self.rhs)
                except ImportError:
                    caller.msg("{} is not a valid class path, not creating the spawner.".format(self.rhs))
                    return

                split_left = self.lhs.split(';')
                spawn_name = split_left[0]
                if len(split_left) > 1:
                    aliases = split_left[1:]
                else:
                    aliases = []
                spawner = create_script(typeclass=Spawner,
                                        key=Spawner.get_key(spawn_name),
                                        obj=caller.location,
                                        interval=5,
                                        start_delay=True,
                                        persistent=True,
                                        autostart=False,
                                        desc="Respawns target on a cadence if target is missing.")
                spawner.tags.add(SPAWNER_TAG, TAG_CATEGORY_BUILDING)
                spawner.db.spawn_name = spawn_name
                spawner.db.aliases = aliases
                spawner.db.spawn_type = self.rhs

                spawner.start()
                caller.msg("Successfully started the spawner for: {}".format(spawner.db.spawn_name))
                return
            else:
                caller.msg("@spawner <obj name>[, <obj2 name>...] = <class path>[, <class2 path>...]")
                return

        # TODO: All code flows and switches
        pass

class Spawner(Script):
    @staticmethod
    def get_key(obj_name):
        # Name a spawner based on what it outputs (might not be unique)
        return "spawner_{}".format(obj_name)

    def at_start(self):
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

    def respawn_timer(self):
        if not self.db.respawn_time:
            self.db.respawn_time = RESPAWN_TIME_DEFAULT
        total_respawn = timedelta(seconds=self.db.respawn_time)
        total_respawn = total_respawn - timedelta(microseconds=total_respawn.microseconds)
        if self.db.respawn_at:
            remaining_respawn = (self.db.respawn_at - datetime.now())
            remaining_respawn = remaining_respawn - timedelta(microseconds=remaining_respawn.microseconds)
            respawn_indicator = "{}/{}".format(remaining_respawn, total_respawn)
        else:
            respawn_indicator = "{}".format(total_respawn)

        return respawn_indicator

    def spawn_target(self):
        spawned = create_object(typeclass=self.db.spawn_type,
                                key=self.db.spawn_name,
                                location=self.obj,
                                home=self.obj,
                                aliases=self.db.aliases,
                                locks=CmdCreate.new_obj_lockstring)

        self.db.respawn_at = None

    def at_repeat(self):
        if self.find_target():
            self.db.respawn_at = None
        else:
            if self.db.respawn_at:
                if datetime.now() >= self.db.respawn_at:
                    self.spawn_target()
            else:
                self.db.respawn_at = datetime.now() + timedelta(seconds=self.db.respawn_time)

    def is_valid(self):
        return (super(Spawner, self).is_valid() and (self.ndb.spawn_class or not self.is_active) and
                self.db.respawn_time and self.obj and self.db.spawn_type and self.db.spawn_name and
                self.db.aliases is not None)
