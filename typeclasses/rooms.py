"""
Room

Rooms are simple containers that has no location of their own.

"""

from typeclasses.objects import Object


class DefaultRoom(Object):
    """
    This is the base room object. It's just like any Object except its
    location is always `None`.
    """
    def basetype_setup(self):
        """
        Simple room setup setting locks to make sure the room
        cannot be picked up.

        """

        super(DefaultRoom, self).basetype_setup()
        self.locks.add(";".join(["get:false()",
                                 "puppet:false()"])) # would be weird to puppet a room ...
        self.location = None
