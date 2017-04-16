from commands.command import Command
from datetime import datetime, timedelta
from evennia.commands.default.building import _convert_from_string
from evennia.locks.lockhandler import LockHandler
from evennia.scripts.models import ScriptDB
from evennia.utils.create import create_object, create_script
from evennia.utils.evtable import EvTable
from evennia.utils.search import search_script_tag
from evennia.utils.utils import class_from_module
import re
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
        lists detailed info for all spawner scripts in the current location
      @spawner <obj name>[;alias1;alias2] = <class path>
        creates a spawner that immediately starts respawning objects
      @spawner/all
        lists all spawners in the game and their locations.
      @spawner/spawn <script #>
        forces a spawner to immediately spawn
      @spawner/del <script #>
        deletes a spawner by its script id
      @spawner/name <script #> = <obj name>[;alias1;alias2;...]
        rename the things a spawner spawns, which also renames the spawner script itself to match
      @spawner/alias <script #> = <alias1, alias2>
        add aliases for the things a spawner spawns
      @spawner/type <script #> = <class path>
        change the type of the things a spawner spawns
      @spawner/rate <script #> = <num seconds>
        set the number of seconds it takes for something to respawn, 0 for instant
      @spawner/set <script #>/<attr>[ = <value>]
        view, set, or unset what attributes should be present on spawned objects
      @spawner/setclear <script #>
        clears all attributes that would be set on spawned objects
      @spawner/lock <script #> = <lockstring>
        set what locks should be present on spawned objects
      @spawner/lockdel <script #>/<lock type>
        delete locks that would otherwise be present on spawned objects
      @spawner/lockreset <script #>
        reset locks back to default on spawned objects
    Examples:
      @spawner a savage orc;orc;savage = typeclasses.npcs.orcs.SavageOrc
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
            spawner_dbrefs = ', '.join([spawner.dbref for spawner in spawners])
            self.caller.msg("Aborting, multiple spawners matched query {}: {}".format(id, spawner_dbrefs))
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

        if not self.switches:
            if not self.rhs:
                # List out details for all spawners in the current room
                spawners = []
                for script in caller.location.scripts.all():
                    if isinstance(script, Spawner):
                        spawners.append(script)

                if len(spawners) == 0:
                    self.caller.msg("No spawners are present in this location.")
                    return

                separator = "\n{}".format("-" * 60)
                output = "|wSpawners in this location:|n"
                for spawner in spawners:
                    output += separator
                    output += "\nScript Name: {} ({})".format(spawner.key, spawner.dbref)
                    output += "\nSpawn Target: {} ({})".format(spawner.db.spawn_name, spawner.db.spawn_type)
                    output += "\nAliases: {}".format(','.join(spawner.db.aliases))
                    output += "\nRespawn Timer: {}".format(spawner.respawn_timer())
                    output += "\nSpawned Attributes:"
                    if not spawner.db.attributes:
                        output += " None"
                    else:
                        for key, value in spawner.db.attributes.items():
                            output += "\n    {}: {}".format(key, value)
                    output += "\nLocks: {}".format(spawner.db.lockstring)
                self.caller.msg(output)

                return

            # Create a new spawner
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

        # Parse switches off the spawner search params and find it
        split_left = self.lhs.split('/', 1)
        spawner = self.find_spawner(split_left.pop(0))
        if not spawner:
            return

        if "spawn" in self.switches:
            spawned = spawner.spawn_target()
            caller.msg("Force spawned {} from spawner {}".format(spawned.get_display_name(caller), spawner.dbref))
            return
        if "del" in self.switches:
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
            return
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
            return
        elif "set" in self.switches:
            # Check if we chose an attribute; there should be one more element left in split_left
            if len(split_left) != 1:
                caller.msg("Usage: @spawner/set <script #>/<attr>[ = <value>]")
                return
            attr = split_left[0]

            # Trying to clear an attribute if present
            if not self.rhs:
                if attr in spawner.db.attributes:
                    del spawner.db.attributes[attr]
                    caller.msg("Removed attribute {} from appearing on spawned objects on {}({})".format(
                        attr, spawner.db.spawn_name, spawner.dbref))
                    return
                else:
                    caller.msg("No attribute {} set for spawner {}({})".format(
                        attr, spawner.db.spawn_name, spawner.dbref))
                    return

            # We are setting or overwriting an attribute to be placed on spawned objects
            value = _convert_from_string(self, self.rhs)
            spawner.db.attributes[attr] = value

            caller.msg("Set attribute {} = {} to appear on objects spawned from {}({})".format(
                attr, self.rhs, spawner.db.spawn_name, spawner.dbref))
            return
        elif "setclear" in self.switches:
            spawner.db.attributes = {}

            caller.msg("Cleared all attributes from appearing on objects spawned from {}({})".format(
                spawner.db.spawn_name, spawner.dbref))
            return
        elif "lock" in self.switches:
            spawner.add_lock(self.rhs)
            caller.msg("Added lock {} to spawner {}({})".format(self.rhs, spawner.db.spawn_name, spawner.dbref))
            return
        elif "lockdel" in self.switches:
            if self.rhs or len(split_left) != 1:
                caller.msg("Usage: @spawner/lockdel <script #>/<lock type>")
            lock_type = split_left[0]
            spawner.remove_lock(lock_type)
            caller.msg("Deleted lock {} to spawner {}({})".format(lock_type, spawner.db.spawn_name, spawner.dbref))
            return
        elif "lockreset" in self.switches:
            spawner.reset_locks()
            caller.msg("Reset locks to default on spawner {}({})".format(spawner.db.spawn_name, spawner.dbref))
            return
        else:
            caller.msg("Invalid switch. Type \"help @spawner\" for a list of valid switches.")
            return

class Spawner(Script):
    class LockHolder(object):
        """
        An empty object to hold the LockHandler used to compute locks for spawned objects.
        """
        def __init__(self, lockstring):
            self.lock_storage = ""
            self.locks = LockHandler(self)
            self.locks.add(lockstring)

    def add_lock(self, lockstring):
        # OVERRIDE: evennia.commands.default.building.CmdLock.func
        lockstring = re.sub(r"\'|\"", "", lockstring)
        self.ndb.lock_holder.locks.add(lockstring)
        self.db.lockstring = str(self.ndb.lock_holder.locks)

    def remove_lock(self, lock_type):
        self.ndb.lock_holder.locks.remove(lock_type)
        self.db.lockstring = str(self.ndb.lock_holder.locks)

    def reset_locks(self):
        self.db.lockstring = CmdCreate.new_obj_lockstring
        self.ndb.lock_holder.locks.clear()
        self.ndb.lock_holder.locks.add(self.db.lockstring)

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
        if not self.db.attributes:
            self.db.attributes = {}
        if not self.db.lockstring:
            self.db.lockstring = CmdCreate.new_obj_lockstring

        # If this isn't set here, then it's set when self.db.spawn_type is set
        if self.db.spawn_type:
            self.ndb.spawn_class = class_from_module(self.db.spawn_type)

        self.ndb.lock_holder = Spawner.LockHolder(self.db.lockstring)

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
                                locks=self.db.lockstring)

        # Set attributes on the new object
        for attr, value in self.db.attributes.items():
            setattr(spawned.db, attr, value)

        # Copy locks from the lock holder
        spawned.locks.add(str(self.ndb.lock_holder.locks))

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
                self.obj and self.db.spawn_type and self.db.spawn_name and self.db.aliases is not None and
                self.db.attributes is not None and self.db.lockstring is not None)
