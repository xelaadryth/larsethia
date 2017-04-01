from commands.command import Command
from evennia.utils import logger, mod_import
from utils.constants import QUEST_DIR, QUEST_NAME_CONST, QUEST_DESC_CONST


class CmdQuests(Command):
    """
    List out your uncompleted quests and your current progress.

    Usage:
      quests
    """
    key = "quests"
    aliases = ["quest"]
    locks = "cmd:all()"
    help_category = "General"

    # TODO: Add in a way to list completed quests
    # TODO: Add in listing out specific quest details with "quest <quest name>"
    def func(self):
        """
        Lists out your quests.
        """
        initial_output = "Active Quests\n============="
        output = initial_output
        for quest, quest_status in self.caller.db.quests.items():
            try:
                quest_module = mod_import(QUEST_DIR + quest)
            except Exception as e:
                logger.log_err("Failed to import module {}".format(QUEST_DIR + quest))
                continue

            # Quest already completed
            if not quest_status:
                continue

            # If we're missing the quest name then we skip displaying it
            quest_name = getattr(quest_module, QUEST_NAME_CONST, None)
            if not quest_name:
                continue

            output += "\n" + quest_name

            # Skip the description if it's not present
            quest_descs = getattr(quest_module, QUEST_DESC_CONST, None)
            if not quest_descs or len(quest_descs) < quest_status + 1:
                logger.log_warn("Quest {} missing description for progression {}.".format(quest, quest_status))
                continue

            output += " - " + quest_descs[quest_status]

        if output == initial_output:
            output += "\nNo quests are currently in progress."
        self.caller.msg(output)


class CmdQuestSet(Command):
    """
    Resets a quest you have progress in.

    Usage:
      @questset [<player_name>/]<quest_name> = <quest_status>
    Example:
      @questset tutorial =
      @questset tutorial = 0
      @questset Madler/tutorial = 3

    Setting to 0 marks a quest as completed.
    Setting to positive integers marks it as that progress status.
    Setting to anything else clears all data for that quest.
    Optionally setting a player sets quest progress on another character.
    """
    key = "@questset"
    locks = "cmd:perm(questset) or perm(Builders)"
    help_category = "Building"

    def func(self):
        """
        Lists out your quests.
        """
        if not self.lhs or self.rhs is None:
            self.caller.msg("Usage: @questset <quest_name> = <quest_status>")
            return

        target = self.caller
        quest_name = self.lhs

        split_lhs = self.lhs.split('/')
        if len(split_lhs) > 1:
            target = self.caller.search(split_lhs[0])
            if not target:
                return
            quest_name = split_lhs[1]

        try:
            value = int(self.rhs)
            target.db.quests[quest_name] = value
            target.msg("Set quest status on {} for {} to {}.".format(target.name, quest_name, self.rhs))
            return
        except ValueError:
            if quest_name in target.db.quests:
                del target.db.quests[quest_name]
                self.caller.msg("Deleted quest progress on {} for {}.".format(target.name, quest_name))
            else:
                self.caller.msg("Failed to find quest {} on {}, could not delete progress.".format(
                    quest_name, target.name))
