# By default, all conversations begin at the function "start"
def start(caller):
    # This is a variable that stores text (otherwise known as a "string" of characters)
    text = "You begin a conversation."

    # This is a variable that holds an array (everything within the "[]" symbols)
    # The array here contains dictionaries (everything within the "{}" symbols)
    # A dictionary's format is {key: value, key: value}
    # In this file, all keys and values must either be strings, or variables that contain strings
    options = [
        {
            "desc": '"Where am I?"',
            "goto": "info1"
        },
        {
            "desc": '"Who are you?"',
            "goto": "info2"
        }
    ]

    # An example of how we can do more complicated logic. "caller.db.[variable_name]" gets thevalue of
    # the calling player's persistent attributes from the db
    if not caller.db.is_kind:
        # Arrays have an "append" function that adds another thing to the end of it, in this case another option
        options.append(
            {
                "desc": 'Leave',
                "goto": "end"
            }
        )

    # This returns the string variable and array variables we defined above.
    # We could also have defined them in-line; it makes no difference.
    return text, options


def info1(caller):
    # Note that it doesn't matter if you use single or double quotes on the outside when defining text (strings)
    # What's important to note is that if you use the SAME symbol within the quote marks,
    # you need to "escape" the symbol with a "\"
    text = "\"Briskell.\""

    options = [
        {
            "desc": '"Goodbye."',
            "goto": "end"
        }
    ]

    return text, options


def info2(caller):
    # Usually we use double quotation marks on the outside to mark text (strings), but since dialogue gets obnoxious
    # to deal with if you have escaped \" everywhere, for speech it's easier to use single quotes on the outside
    # Note however that now we need to escape any apostrophes \' that appear in the text instead.
    # There's just no winning
    text = '"None of your business. I don\'t care for all of your questions."'

    options = [
        {
            "desc": '"Goodbye."',
            "goto": "end"
        }
    ]

    return text, options


def end(caller):
    # When a node returns an empty "options" second argument, the conversation ends
    # Note that every conversation needs at least one option, or EvMenu will glitch a little temporarily
    # Here's an example of in-lining the text and options from before.
    # A variable's name is purely for readability and there is no intrinsic dependency on the variable's name
    return '"I hope we don\'t meet again."', []
