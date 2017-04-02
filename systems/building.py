from commands.command import Command
from evennia.commands.default.building import ObjManipCommand
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import create, search


class CmdCreate(ObjManipCommand):
    """
    create new objects

    Usage:
      @create objname[;alias;alias...][:typeclass], objname...

    Creates one or more new objects. If typeclass is given, the object
    is created as a child of this typeclass. The typeclass script is
    assumed to be located under types/ and any further
    directory structure is given in Python notation. So if you have a
    correct typeclass 'RedButton' defined in
    types/examples/red_button.py, you could create a new
    object of this type like this:

       @create/drop button;red : examples.red_button.RedButton

    """

    key = "@create"
    locks = "cmd:perm(create) or perm(Builders)"
    help_category = "Building"

    # lockstring of newly created objects, for easy overloading.
    # Will be formatted with the {id} of the creating object.
    new_obj_lockstring = "control:id({id}) or perm(Wizards);delete:id({id}) or perm(Wizards);get:false()"

    def func(self):
        """
        Creates the object.
        """

        caller = self.caller
        location = caller
        if caller.location:
            location = caller.location
        string = ""

        if not self.args:
            string = "Usage: @create <objname>[;alias;alias...] [:typeclass_path]"
            caller.msg(string)
            return

        # create the objects
        for objdef in self.lhs_objs:
            string = ""
            name = objdef['name']
            aliases = objdef['aliases']
            typeclass = objdef['option']

            # create object (if not a valid typeclass, the default
            # object typeclass will automatically be used)
            lockstring = self.new_obj_lockstring.format(id=caller.id)
            obj = create.create_object(typeclass, name, location,
                                       home=location, aliases=aliases,
                                       locks=lockstring, report_to=caller)
            if not obj:
                continue
            if aliases:
                string = "You create a new %s: %s (aliases: %s)."
                string = string % (obj.typename, obj.name, ", ".join(aliases))
            else:
                string = "You create a new %s: %s."
                string = string % (obj.typename, obj.name)
            # set a default desc
            if not obj.db.desc:
                obj.db.desc = "You see nothing special."
        if string:
            caller.msg(string)


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

class CmdBoot(Command):
    """
    kick a player from the server. If there is a character without an associated player in the room, boots that instead.

    Usage
      @boot[/switches] <player obj> [: reason]

    Switches:
      quiet - Silently boot without informing player
      sid - boot by session id instead of name or dbref

    Boot a player object from the server. If a reason is
    supplied it will be echoed to the user unless /quiet is set.
    """

    key = "@boot"
    aliases = ["@kick"]
    locks = "cmd:perm(boot) or perm(Wizards)"
    help_category = "Admin"

    def func(self):
        """Implementing the function"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("Usage: @boot[/switches] <player> [:reason]")
            return

        if ':' in args:
            args, reason = [a.strip() for a in args.split(':', 1)]
        else:
            args, reason = args, ""

        boot_list = []

        if 'sid' in self.switches:
            # Boot a particular session id.
            sessions = SESSIONS.get_sessions(True)
            for sess in sessions:
                # Find the session with the matching session id.
                if sess.sessid == int(args):
                    boot_list.append(sess)
                    break
        else:
            # Boot by player object
            pobj = search.player_search(args)
            if not pobj:
                caller.msg("Player %s was not found." % args)
                return
            pobj = pobj[0]
            if not pobj.access(caller, 'boot'):
                string = "You don't have the permission to boot %s." % (pobj.key, )
                caller.msg(string)
                return
            # we have a bootable object with a connected user
            matches = SESSIONS.sessions_from_player(pobj)
            for match in matches:
                boot_list.append(match)

        if not boot_list:
            character = caller.search(args)
            if character:
                # This character has no currently attached player, but we still need to boot it
                character.at_post_unpuppet(None)
                caller.msg("Booting disconnected player character {}.".format(character.name))
            else:
                caller.msg("No matching sessions found. The Player does not seem to be online.")
            return

        # Carry out the booting of the sessions in the boot list.

        feedback = None
        if 'quiet' not in self.switches:
            feedback = "You have been disconnected by %s.\n" % caller.name
            if reason:
                feedback += "\nReason given: %s" % reason

        for session in boot_list:
            session.msg(feedback)
            session.player.disconnect_session_from_player(session)
