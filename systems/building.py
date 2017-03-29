from evennia.commands.default.building import ObjManipCommand
from evennia.utils import create


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


class CmdHide(ObjManipCommand):
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
            string = "@hide <objname>"
            caller.msg(string)
            return

        caller.execute_cmd("@lock {} = notice:false()".format(self.lhs))


class CmdUnhide(ObjManipCommand):
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
            string = "@unhide <objname>"
            caller.msg(string)
            return

        caller.execute_cmd("@lock/del {}/notice".format(self.lhs))
