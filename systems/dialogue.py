from commands.command import Command
from evennia.utils.evmenu import EvMenu


def talk(player, target):
    """
    Given legal targets for talking, have them talk. Usually called from the Talk command, but can also
    be called programmatically.
    """
    # Now that we have a legal target, try to talk
    try:
        player.db.talk_target = target
        # Don't automatically look on exit
        EvMenu(player, target.db.talk_file, cmd_on_exit=None)
        player.location.msg_contents("{} talks to {}.".format(player.name, target.name), exclude=player)
    except ImportError:
        player.msg("Dialogue is broken, please contact the builders.")


class CmdTalk(Command):
    """
    Attempts to talk to an NPC.

    Usage:
     talk
     talk <target>

    This command is only available if a talkative non-player-character
    (NPC) is actually present. It will strike up a conversation with
    that NPC and give you options on what to talk about.
    """
    key = "talk"
    locks = "cmd:all()"
    help_category = "General"

    def can_talk(self, target):
        return target and (target != self.caller) and (target.access(self.caller, "view")) and\
            (target.access(self.caller, "talk", default=True)) and target.db.talk_file

    def func(self):
        # Acquire target
        if not self.args:
            legal = []
            for obj in self.caller.location.contents:
                if self.can_talk(obj):
                    legal.append(obj)

            if len(legal) == 0:
                self.caller.msg("There's no one talkative here.")
                return
            elif len(legal) == 1:
                target = legal[0]
            else:
                response = "Who do you want to talk to?"
                for target in legal:
                    response += "\ntalk {}".format(target.key)
                self.caller.msg(response)
                return
        else:
            target = self.caller.search(self.args)
            if not target:
                self.caller.msg("You couldn't find {}.".format(self.args))
                return
            elif target == self.caller:
                self.caller.msg("You talk to yourself.")
                self.caller.location.msg_contents("{} talks to no one in particular.".format(self.caller.name),
                                                  exclude=self.caller)
                return
            elif not self.can_talk(target):
                self.caller.msg("{} isn't talkative.".format(target))
                return

        talk(self.caller, target)


class CmdAddTalk(Command):
    """
    Adds dialogue to an NPC.

    Usage:
     @addtalk <npc> = <menu file location>
    Example:
     @addtalk Merchant = world.npcs.briskell_merchant
    """
    key = "@addtalk"
    locks = "cmd:perm(addtalk) or perm(Builders)"
    help_category = "Building"

    def func(self):
        # Make sure we're syntactically valid
        if not self.lhs and self.rhs:
            self.caller.msg("Usage: @addtalk <npc> = <menu file location>")
            return

        # Gives the caller a failure message if we can't find it
        target = self.caller.search(self.lhs)

        # Try to talk
        if target:
            target.db.talk_file = self.rhs
            self.caller.msg("{}'s talk file set to: {}".format(target.key, self.rhs))


class CmdDelTalk(Command):
    """
    Deletes dialogue from an NPC.

    Usage:
     @deltalk <npc>
    Example:
     @deltalk Merchant
    """
    key = "@deltalk"
    locks = "cmd:perm(deltalk) or perm(Builders)"
    help_category = "Building"

    def func(self):
        # Make sure we're syntactically valid
        if not self.lhs:
            self.caller.msg("Usage: @deltalk <npc>")
            return

        # Gives the caller a failure message if we can't find it
        target = self.caller.search(self.lhs)

        # Try to talk
        if target:
            del target.db.talk_file
            self.caller.msg("{}'s talk file removed.".format(target.key))
        else:
            # We shouldn't really hit this code path
            self.caller.msg("Usage: @deltalk <npc>")
            return
