from commands.command import Command
from datetime import datetime, timedelta
from evennia.scripts.models import ScriptDB
from evennia.utils.create import create_object, create_script
from evennia.utils.evtable import EvTable
from evennia.utils.search import search_script_tag
from evennia.utils.utils import class_from_module
from systems.command_overrides import CmdCreate
from typeclasses.scripts import Script
from utils.constants import RESPAWN_RATE_DEFAULT, RESPAWN_TICK_RATE, TAG_CATEGORY_BUILDING


SPAWNER_PREFIX = "spawner_"
SPAWNER_TAG = "spawner"


class CmdSpawner(Command):
    """
    Creates a spawner script that respawns specified objects in a configurable way.
    You can reference spawners by script # or by spawn target name.

    Usage:
      @spawner
        lists all spawner scripts in the current location
      @spawner <obj name>[;alias1;alias2] = <class path>
        creates a spawner that immediately starts respawning objects (together)
      @spawner/all
        lists all spawners in the game and their locations.
      @spawner/spawn <script #>
        forces a spawner to immediately spawn
      @spawner/del <script #>
        deletes a spawner by its script id
      @spawner/name <script #> = <obj name>[;alias1;alias2;...]
        rename the things a spawner spawns
      @spawner/alias <script #> = <alias1, alias2>
        add aliases for the things a spawner spawns
      @spawner/type <script #> = <class path>
        change the type of the things a spawner spawns
      @spawner/rate <script #> = <num seconds>
        set the number of seconds it takes for something to respawn, 0 for instant
      @spawner/set <script #>/<attr>[ = <value>]
        set or unset what attributes should be present on spawned objects
      @spawner/setclear <script #>
        clears all attributes that would be set on spawned objects
      @spawner/lock <script #> = <lockstring>
        set what locks should be present on spawned objects
      @spawner/lockdel <script #>/<access type>
        delete locks that would otherwise be present on spawned objects
    Examples:
      @spawner
      @spawner a savage orc;orc;savage = world.npcs.orc.Orc
      @spawner/all
      @spawner/del #23
      @spawner/name #23 = a brutal orc;orc;brute
      @spawner/alias #23 = orc,brute
      @spawner/type #23 = world.npcs.orc.BrutalOrc
      @spawner/rate #23 = 60
      @spawner/set #23/desc = "A brutal orc stands here."
      @spawner/setclear #23
      @spawner/lock #23 = view:quest(lost kitten, 1)
      @spawner/lockdel #23/view
    """
    key = "@spawner"
    aliases = ["@spawners"]
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def find_spawner(self, id):
        scripts = ScriptDB.objects.get_all_scripts(key=id)
        if not scripts:
            # Try to see if they're searching by name
            scripts = ScriptDB.objects.get_all_scripts(key=Spawner.get_key(id))

        spawners = []
        for script in scripts:
            if isinstance(script, Spawner):
                spawners.append(script)

        if len(spawners) < 1:
            self.caller.msg("Spawner {} not found, please specify using \"#<dbref>\".".format(id))
            return None
        elif len(spawners) > 1:
            self.caller.msg("Aborting, multiple spawners matched query: {}".format(id))
            return None

        return spawners[0]

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

        if not self.rhs:
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

        if not self.switches:
            try:
                class_from_module(self.rhs)
            except ImportError:
                caller.msg("{} is not a valid class path.\n"
                           "Usage: @spawner <obj name>[;alias1;alias2] = <class path>".format(self.rhs))
                return

            aliases = self.lhs.split(';')
            spawn_name = aliases.pop(0)
            # Force all aliases to be in lowercase
            aliases = [alias.lower() for alias in aliases]
            spawner = create_script(typeclass=Spawner,
                                    key=Spawner.get_key(spawn_name),
                                    obj=caller.location,
                                    interval=RESPAWN_TICK_RATE,
                                    start_delay=True,
                                    persistent=True,
                                    autostart=False,
                                    desc="Respawns target on a cadence if target is missing.")
            spawner.tags.add(SPAWNER_TAG, TAG_CATEGORY_BUILDING)
            spawner.db.spawn_name = spawn_name
            spawner.db.aliases = aliases
            spawner.db.spawn_type = self.rhs

            spawner.start()
            caller.msg("Successfully started spawner {}({})".format(spawner.db.spawn_name, spawner.dbref))
            return

        # We're performing some action on an existing script, make sure it exists so we can use it
        spawner = self.find_spawner(self.lhs)
        if not spawner:
            return

        if "spawn" in self.switches:
            spawned = spawner.spawn_target()
            caller.msg("Force spawned {} from spawner {}".format(spawned.get_display_name(caller), spawner.dbref))
            return
        elif "del" in self.switches:
            spawner_name = spawner.name
            spawner_dbref = spawner.dbref
            spawner.stop()
            caller.msg("Stopped spawner {}({})".format(spawner_name, spawner_dbref))
            return
        elif "name" in self.switches:
            if not self.rhs:
                caller.msg("@spawner/name <script #> = <obj name>[;alias1;alias2;...]")
                return

            aliases = self.rhs.split(';')
            spawn_name = aliases.pop(0)
            # Force all aliases to be in lowercase
            aliases = [alias.lower().strip() for alias in aliases]
            spawner.db.aliases.extend(aliases)
            # Remove duplicates
            spawner.db.aliases = list(set(spawner.db.aliases))

            spawner.db.spawn_name = spawn_name
            spawner.key = Spawner.get_key(spawn_name)

            caller.msg("Renamed spawn target for spawner {} to be {}".format(spawner.dbref, spawn_name))
        elif "alias" in self.switches:
            if not self.rhs:
                spawner.db.aliases = []
                caller.msg("Cleared aliases on spawner {}({})".format(spawner.db.spawn_name, spawner.dbref))
                return

            aliases = self.rhs.split(',')
            # Force all aliases to be in lowercase
            aliases = [alias.lower().strip() for alias in aliases]
            spawner.db.aliases.extend(aliases)
            # Remove duplicates
            spawner.db.aliases = list(set(spawner.db.aliases))

            caller.msg("New alias list for spawner {}({}): {}".format(
                spawner.db.spawn_name, spawner.dbref, ','.join(spawner.db.aliases)))
            return
        elif "type" in self.switches:
            if not self.rhs:
                caller.msg("@spawner/type <script #> = <class path>")
                return

            try:
                spawn_class = class_from_module(self.rhs)
            except ImportError:
                caller.msg("{} is not a valid class path, not changing spawn class.".format(self.rhs))
                return

            spawner.db.spawn_type = self.rhs
            spawner.ndb.spawn_class = spawn_class

            caller.msg("Changed spawner class for {}({}) to be {}".format(
                spawner.db.spawn_name, spawner.dbref, self.rhs))
            return
        elif "rate" in self.switches:
            spawner.respawn_rate = int(self.rhs)
            caller.msg("Changed respawn rate for {}({}) to be {} seconds.".format(
                spawner.db.spawn_name, spawner.dbref, spawner.respawn_rate))
        elif "set" in self.switches:
            caller.msg("TODO: Set db attributes on spawned objects.")
        elif "setclear" in self.switches:
            caller.msg("TODO: Clear all db attributes for spawned objects.")
        elif "lock" in self.switches:
            caller.msg("TODO: Lock functionality on spawned objects.")
        elif "lockdel" in self.switches:
            caller.msg("TODO: Delete lock functionality on spawned objects.")
        else:
            caller.msg("Invalid switch. Type \"help @spawner\" for a list of valid switches.")
            return

class Spawner(Script):
    @property
    def respawn_rate(self):
        if self.db.respawn_rate is None:
            self.db.respawn_rate = RESPAWN_RATE_DEFAULT
        return self.db.respawn_rate

    @respawn_rate.setter
    def respawn_rate(self, value):
        if value < 0:
            raise Exception("Negative respawn rate {} on {}({})".format(value, self.db.spawn_type, self.dbref))

        self.db.respawn_rate = value
        if self.db.respawn_at:
            new_respawn = datetime.now() + timedelta(seconds=value)
            if new_respawn < self.db.respawn_at:
                self.db.respawn_at = new_respawn

    @staticmethod
    def get_key(obj_name):
        # Name a spawner based on what it outputs (might not be unique)
        return "{}{}".format(SPAWNER_PREFIX, obj_name)

    def at_start(self):
        if self.db.spawn_type:
            self.ndb.spawn_class = class_from_module(self.db.spawn_type)
        if not self.db.attributes:
            self.db.attributes = {}

    def find_target(self):
        room_contents = self.obj.contents_get()

        for obj in room_contents:
            if obj.name == self.db.spawn_name and isinstance(obj, self.ndb.spawn_class):
                return obj

        return None

    def respawn_timer(self):
        total_respawn = timedelta(seconds=self.respawn_rate)
        total_respawn = total_respawn - timedelta(microseconds=total_respawn.microseconds)

        respawn_indicator = "{}".format(total_respawn)
        if self.db.respawn_at:
            remaining_respawn = (self.db.respawn_at - datetime.now())
            remaining_respawn = remaining_respawn - timedelta(microseconds=remaining_respawn.microseconds)

            # Only show remaining respawn if it's not in the past
            if remaining_respawn.total_seconds() >= 0:
                respawn_indicator = "{}/{}".format(remaining_respawn, total_respawn)

        return respawn_indicator

    def spawn_target(self):
        spawned = create_object(typeclass=self.db.spawn_type,
                                key=self.db.spawn_name,
                                location=self.obj,
                                home=self.obj,
                                aliases=self.db.aliases,
                                locks=CmdCreate.new_obj_lockstring)

        self.db.respawn_at = None

        return spawned

    def at_repeat(self):
        if self.find_target():
            self.db.respawn_at = None
        else:
            if self.respawn_rate == 0:
                self.spawn_target()
            elif self.db.respawn_at:
                if datetime.now() >= self.db.respawn_at:
                    self.spawn_target()
            else:
                self.db.respawn_at = datetime.now() + timedelta(seconds=self.respawn_rate)

    def is_valid(self):
        return (super(Spawner, self).is_valid() and (self.ndb.spawn_class or not self.is_active) and
                self.obj and self.db.spawn_type and self.db.spawn_name and self.db.aliases is not None)
