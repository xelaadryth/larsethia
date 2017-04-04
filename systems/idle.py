import random
from commands.command import Command
from evennia.utils import logger
from typeclasses.scripts import Script
from utils.constants import IDLE_INTERVAL


class CmdIdle(Command):
    """
    Checks, adds, or deletes idle text onto an object. Every time the idle script on the player ticks,
    there's a chance it will display a message.

    Usage:
      @idle
      @idle <objname>
      @idle <objname> = <avg seconds>, <idle text>
      @idle/del <objname> = <idle id>
    Example:
      @idle children
      @idle here = 60, Echoes fill the cavern as a droplet of water falls from the ceiling into a murky puddle.
      @idle/del here = 0

    @idle - lists all idle objects in the current location
    @idle <objname> - lists all idle text on an object.
    With a delete switch, removes the nth piece of idle text. Is NOT associated with a dbref.
    """
    key = "@idle"
    locks = "cmd:perm(idle) or perm(Builders)"
    help_category = "Building"

    def func(self):
        if not self.args:
            if not self.caller.location:
                self.caller.msg("No location to search for idle objects.")
                return

            idle_objs = [self.caller.location]
            for obj in self.caller.location.contents:
                if obj.db.idle:
                    idle_objs.append(obj)

            if len(idle_objs) == 0:
                self.caller.msg("No objects with idle lines are present in {}.".format(self.caller.location.name))
                return

            output = "Objects with idle lines:"
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
            output = "ID||Avg Sec||Message\n---+-------+-------"
            for i, (idle_time, idle_line) in enumerate(idle_list):
                output += "\n{}||{}||{}".format(str(i).rjust(2), str(idle_time).rjust(7), idle_line)

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
            # Iterate over the room's contents in random order
            for obj in random.sample(self.obj.location.contents, len(self.obj.location.contents)):
                if obj != self.obj and obj.db.idle and obj.access(self.obj, "idle", default=True):
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
