# By default, all conversations begin at "start"
def start(caller):
    text = "You begin a conversation."

    options = [{"desc": "Where am I?",
                "goto": "info1"},
               {"desc": "Who are you?",
                "goto": "info2"},
               {"desc": "Goodbye.",
                "goto": "end"}]

    return text, options


def info1(caller):
    text = "'Briskell.'"

    options = [{"desc": "Goodbye.",
                "goto": "end"}]

    return text, options

def info2(caller):
    text = "'None of your business.'"

    options = [{"desc": "Goodbye.",
                "goto": "end"}]

    return text, options


def end(caller):
    # When a node returns an empty "options" second argument, the conversation ends
    # Note that every conversation needs at least one option, or EvMenu will glitch a little temporarily
    return "'Goodbye.'", []
