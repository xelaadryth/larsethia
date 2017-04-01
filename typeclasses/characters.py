"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from typeclasses.objects import SharedObject
from utils.constants import QUEST_COMPLETE


class Character(SharedObject, DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(player) -  when Player disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Player has disconnected" 
                    to the room.
    at_pre_puppet - Just before Player re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "PlayerName has entered the game" to the room.

    """
    def at_object_creation(self):
        if not self.db.quests:
            self.db.quests = {}

    def at_server_reload(self):
        if not self.db.quests:
            self.db.quests = {}

    def quest_status(self, quest_name):
        """
        Check what stage of a quest the character is on
        """
        return self.db.quests.get(quest_name, None)

    def quest_advance(self, quest_name, stage):
        """
        Set what stage of a quest the character is on
        """
        self.db.quests[quest_name] = stage

    def quest_complete(self, quest_name):
        """
        Mark a quest as completed.
        """
        self.db.quests[quest_name] = QUEST_COMPLETE
