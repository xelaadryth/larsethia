from commands.command import Command


class CmdNPC(Command):
    """
    Creates an NPC object.

    Usage:
      @npc <npc_name>[;alias;alias...]
    Example:
      @npc an old man
      @npc Merric;elf;guard;archer

    This command is equivalent to "@create <input>:typeclasses.npcs.NPC".
    """
    key = "@npc"
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: @npc <npc_name>[;alias;alias...]")
            return

        caller.execute_cmd("@create {}:typeclasses.npcs.NPC".format(self.args))


class CmdHide(Command):
    """
    Hides objects so they're not obvious to players by removing them from the list of room contents.

    Usage:
      @hide <objname>
    Example:
      @hide rock

    This command is equivalent to "@lock <objname> = notice:false()", which means that whatever contains it
    (usually a location, but can be any object/character) will not list it, even though players can still look
    at it if they realize it exists.
    """
    key = "@hide"
    locks = "cmd:perm(hide) or perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: @hide <objname>")
            return

        caller.execute_cmd("@lock {} = notice:false()".format(self.lhs))


class CmdUnhide(Command):
    """
    Unhides a hidden object to make it noticeable again.

    Usage:
      @unhide <objname>
    Example:
      @unhide rock

    This command is equivalent to "@lock/del <objname>/notice", which means that whatever contains it
    (usually a location, but can be any object/character) will list it again.
    """
    key = "@unhide"
    locks = "cmd:perm(hide) or perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: @unhide <objname>")
            return

        caller.execute_cmd("@lock/del {}/notice".format(self.lhs))
