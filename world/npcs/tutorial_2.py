from world.quests.tutorial import INTERNAL_NAME


def start(caller):
    text = ('"Are you getting more comfortable moving around? '
            'Movement feels a little strange in Larsethia, after all."\n\n'
            'The old man looks at the glowing portal in the center of the dark chamber, '
            'and then smiles at you warmly.\n\n'
            '"When you\'re ready to proceed, just go through the portal, and it will bring you home."')

    options = [
        {
            "desc": '"How do I go through the portal?"',
            "goto": "portal"
        }
    ]

    return text, options


def portal(caller):
    text = ('You turn to point at the portal, but then realize the old man has disappeared.\n\n'
            'As you try to think about where he may have gone, you realize with horror that there is no old man '
            'in your memories at all, and that you were just speaking into empty space this whole time.\n\n'
            'However, you somehow know that you should type the name of an exit in order to travel there, '
            'so you prepare to type "portal".')

    # Complete the quest
    caller.quest_complete(INTERNAL_NAME)

    return text, []
