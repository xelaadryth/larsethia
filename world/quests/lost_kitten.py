from typeclasses.characters import Character
from typeclasses.objects import Object


# This name MUST match the filename
INTERNAL_NAME = "lost_kitten"
# This is the text displayed to the player; if it's missing it won't appear in the player's quest log
QUEST_NAME = "A Lost Kitten"

# The first entry is a description of the entire quest (shown after completion). The other ones describe
# what actions to take to proceed
QUEST_DESC = [
    "Mirienne can't find her cat.",
    "Try to find Mirienne's kitten somewhere in Briskell and bring it back to her.",
    "Bring the kitten back to Mirienne in Briskell Square."
]


class LostKitten(Object):
    def at_get(self, getter):
        if isinstance(getter, Character):
            self.locks.add("view:all()")
            self.db.desc = "Mirienne's cute kitten looks up at you trustingly and mewls softly."
            getter.quest_advance(INTERNAL_NAME, 2)
