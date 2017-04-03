import random
from evennia.utils import logger
from typeclasses.scripts import Script
from utils.constants import IDLE_INTERVAL

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
            #self.obj.location.msg_contents(self.obj.id)
            pass
        else:
            logger.log_warn("IdleScript on object {} still running without a location".format(self.obj.id))
