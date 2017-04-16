from typeclasses.characters import Character, SharedCharacter


class NPC(SharedCharacter):
    def get_display_appearance(self, looker):
        desc = self.db.desc
        if self.db.quest and isinstance(looker, Character):
            quest_status = looker.quest_status(self.db.quest)
            if quest_status is not None:
                # If we have quest-state specific description, display it instead
                desc = getattr(self.db, "desc_quest_{}".format(quest_status), None)
        return desc
