import random
from commands.command import Command
from evennia.utils import evtable, logger, search
from typeclasses.scripts import Script
from utils.constants import IDLE_INTERVAL, TAG_CATEGORY_BUILDING


IDLE_TAG = "idle"


class CmdIdle(Command):
    """
    Checks, adds, or deletes idle text onto an object. Every time the idle
    script on the player ticks, there's a chance it will display a message.

    Usage:
      @idle
        lists all idle objects in the current location
      @idle <objname>
        lists all idle text on an object, each with an idle id
      @idle <objname> = <avg seconds>, <idle text>
        creates new idle text on an object that procs with the given rate and text
      @idle/all
        lists all objects with idle text in the game and their locations
      @idle/del <objname> = <idle id>
        removes the nth piece of idle text by idle id. Is NOT associated with a dbref
      @idle/clear <objname>
        removes all idle text from an object
    Examples:
      @idle
      @idle children
      @idle here = 60, A droplet of water falls from the ceiling into a murky puddle.
      @idle/all
      @idle/del here = 0
      @idle/clear children
    """
    key = "@idle"
    locks = "cmd:perm(idle) or perm(Builders)"
    help_category = "Building"

    def func(self):
        if "all" in self.switches:
            idle_objs = search.search_object_by_tag(IDLE_TAG, TAG_CATEGORY_BUILDING)

            if len(idle_objs) == 0:
                self.caller.msg("No objects with idle lines exist.")
                return

            table = evtable.EvTable("Obj #", "Object", "Loc #", "Location")
            for obj in idle_objs:
                if obj.location:
                    location_dbref = obj.location.dbref
                    location_key = obj.location.key
                else:
                    location_dbref = "N/A"
                    location_key = "No Location"
                table.add_row(obj.dbref, obj.key, location_dbref, location_key)
            output = "|wObjects with idle lines by location:|n\n{}".format(table)
            self.caller.msg(output)

            return

        if not self.args:
            if not self.caller.location:
                self.caller.msg("No location to search for idle objects.")
                return

            idle_objs = []
            # The location may also have idle lines
            if self.caller.location.db.idle:
                idle_objs.append(self.caller.location)
            for obj in self.caller.location.contents:
                if obj.db.idle:
                    idle_objs.append(obj)

            if len(idle_objs) == 0:
                self.caller.msg("No objects with idle lines are present in {}.".format(self.caller.location.name))
                return

            output = "Objects with idle lines in this room:"
            for obj in idle_objs:
                output += "\n(#{}) {}".format(obj.id, obj.name)
            self.caller.msg(output)
            return

        target = self.caller.search(self.lhs)
        if not target:
            return

        # Clear all idle messages from an object
        if "clear" in self.switches:
            if target.db.idle:
                del target.db.idle
                self.caller.msg("All idle lines cleared from {}.".format(target.name))
            else:
                self.caller.msg("{} had no idle lines to clear.".format(target.name))
            return

        # Delete specified message
        if "del" in self.switches:
            if not self.rhs:
                self.caller.msg("Usage: @idle/del <objname> = <idle id>")
                return

            try:
                idle_id = int(self.rhs)
            except ValueError:
                self.caller.msg("Usage: @idle/del <objname> = <idle id>")
                return
            except Exception as e:
                logger.log_warn("Unexpected exception casting idle_id on object {}: {}".format(target.id, e))
                return

            idle_list = target.db.idle
            if not idle_list or idle_id >= len(idle_list):
                self.caller.msg("Idle list's largest element is {}.".format(len(idle_list)-1))
                return

            # Remove the nth element
            _, idle_line = target.db.idle.pop(idle_id)
            self.caller.msg("Removed from {}: {}".format(target.name, idle_line))
            return

        # Check idle messages on an object
        if not self.rhs:
            idle_list = target.db.idle
            if not idle_list:
                self.caller.msg("No idle messages on {}.".format(target.name))
                return
            # ID only looks good up to 99, but it will still function after that
            table = evtable.EvTable("ID", "Avg Sec", "Message")
            for i, (idle_time, idle_line) in enumerate(idle_list):
                table.add_row(i, idle_time, idle_line)

            output = "|wIdle messages on {}:|n\n{}".format(target.name, table)
            self.caller.msg(output)
            return

        # Add new idle line
        rhs_split = self.rhs.split(",", 1)
        if len(rhs_split) != 2:
            self.caller.msg("Usage: @idle <objname> = <avg seconds>, <idle id>")
            return
        idle_time, idle_line = rhs_split
        try:
            idle_time = int(idle_time)
        except ValueError:
            self.caller.msg("Usage: @idle <objname> = <avg seconds>, <idle id>")
            return
        except Exception as e:
            logger.log_warn("Unexpected exception casting idle_time on object {}: {}".format(target.id, e))
            return
        idle_line = idle_line.strip()

        if not target.db.idle:
            target.db.idle = [(idle_time, idle_line)]
        else:
            target.db.idle.append((idle_time, idle_line))

        target.tags.add(IDLE_TAG, TAG_CATEGORY_BUILDING)

        self.caller.msg("Added new idle message to {}.".format(target.name))


class IdleScript(Script):
    """
    Check for things with idle messages in the room and display them at random intervals.
    """

    @staticmethod
    def get_key(obj):
        return "idle_{}".format(obj.id)

    def at_script_creation(self):
        self.key = self.get_key(self.obj)
        self.desc = "Polls for idle messages in attached owner's location."
        # Don't message right off the bat
        self.start_delay = True
        self.interval = IDLE_INTERVAL
        self.persistent = True

    def at_repeat(self):
        """
        This gets called every self.obj.db.idle_interval seconds.
        """
        if self.obj.location:
            # Random percentage chance of an idle message proccing
            remaining_chance = random.random()
            # Iterate over the room and its contents in random order
            possible_idle_objs = self.obj.location.contents[:]
            possible_idle_objs.append(self.obj.location)
            for obj in random.sample(possible_idle_objs, len(possible_idle_objs)):
                if (obj != self.obj and obj.db.idle and obj.access(self.obj, "view")
                        and obj.access(self.obj, "idle", default=True)):
                    # Randomly pick a line
                    for idle_time, idle_line in random.sample(obj.db.idle, len(obj.db.idle)):
                        # If it's not a valid number, just always display it
                        if idle_time <= 0:
                            idle_time = IDLE_INTERVAL
                        # Following expected value, convert this to a probability per 5 seconds
                        remaining_chance -= IDLE_INTERVAL / idle_time
                        # Only one object at a time can display its idle message to avoid spam
                        if remaining_chance <= 0:
                            # Note that we only message the player, so idle messages are NOT broadcasted to everyone
                            # This means players with a higher perception skill for instance can artificially boost
                            # their chance of seeing idle messages
                            self.obj.msg(idle_line)
                            return
        else:
            logger.log_warn("IdleScript on object {} still running without a location".format(self.obj.id))
