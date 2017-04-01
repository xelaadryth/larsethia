"""

Lockfuncs

Lock functions are functions available when defining lock strings,
which in turn limits access to various game systems.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See the
Evennia documentation for more info on locks.

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled with *args, **kwargs. The lock function
should handle all eventual tracebacks by logging the error and
returning False.

Lock functions in this module extend (and will overload same-named)
lock functions from evennia.locks.lockfuncs.

"""
from evennia.locks.lockfuncs import CF_MAPPING
from evennia.utils import logger


def quest(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Checks to see if we have encountered a quest, or matches the exact stage of a quest.
    """
    # Invalid lock
    if len(args) == 0:
        logger.log_warn("Invalid quest lock on {} accessed by {}.".format(accessed_obj, accessing_obj))
        return False

    # Just check if we have seen the quest before
    quest_name = args[0]
    if len(args) == 1:
        return accessing_obj.quest_status(quest_name) is not None

    compare = 'eq'
    if kwargs:
        compare = kwargs.get('compare', 'eq')

    # Note that QUEST_COMPLETE is 0, so to check for completed quests lock at 0
    required_quest_status = args[1]
    quest_status = accessing_obj.quest_status(quest_name)

    # Convert to a float-able value for comparisons
    if quest_status is None:
        quest_status = -1

    return CF_MAPPING.get(compare, CF_MAPPING['default'])(quest_status, required_quest_status)
