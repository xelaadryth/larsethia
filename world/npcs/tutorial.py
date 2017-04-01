from world.quests.tutorial import INTERNAL_NAME


OPTION_WHERE = {
    "desc": '"Where am I?"',
    "goto": "where"
}
OPTION_WHO = {
    "desc": '"Who are you?"',
    "goto": "who"
}
OPTION_GUIDE = {
    "desc": '"Can you guide me out of here?"',
    "goto": "guide"
}


def start(caller):
    text = '"Welcome to Larsethia!\n\n"It\'s not often I get visitors here. Are you lost?"'

    options = [
        OPTION_WHERE,
        OPTION_WHO,
        OPTION_GUIDE,
        {
            "desc": '"Thanks, but I know my own way around. Goodbye!"',
            "goto": "end"
        }
    ]

    return text, options

def where(caller):
    text = '"You\'re in Larsethia, of course! What a silly question."'

    options = [
        OPTION_WHO,
        {
            "desc": '"That didn\'t help at all...but can you guide me out of here?"',
            "goto": "guide"
        }
    ]

    return text, options

def who(caller):
    text = '"Now it\'s rude to just ask people who they are, {}. I\'m just a crazy old man, don\'t mind me!'.format(
        caller.name
    )

    options = [
        {
            "desc": '"How...how do you know my name?"',
            "goto": "name"
        },
        OPTION_WHERE,
        OPTION_GUIDE
    ]

    return text, options

def name(caller):
    text = '"Well it would be rude to ask of it, would it not? You speak in circles, haha!"'

    options = [
        OPTION_WHERE,
        OPTION_GUIDE
    ]

    return text, options

def guide(caller):
    text = ('"Very well, just follow me!"\n\nThe old man leaves to the east.\n\n'
            'Try typing the name of the exit, "e" or "east", to follow him!')

    # The old man has a view and talk lock on him that only lets you see him if you have not yet
    # made any quest progress
    # Therefore this turns him invisible and untalkable
    caller.quest_advance(INTERNAL_NAME, 1)

    return text, []

def end(caller):
    return '"Pleasant journeys!"', []
