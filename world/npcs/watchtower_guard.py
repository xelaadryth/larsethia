def start(caller):
    text = "Aye! Who goes there!"

    options = [
        {
            "dsec": '"A Traveler"',
            "goto": "traveler"
        },
        {
            "dsec": '"A Man of Faith"',
            "goto": "faith"
        },
        {
            "desc": '"A Warrior'",
            "goto": "warrior"
        }
    ]
    return text, options

def traveler(caller):
    text = "Ah, a nomad. There is food and lodging inside the temple, if you have the coin."
    options = [
        {
            "desc": '"Very well..."',
            "goto": "end"
        }
    ]
    return text, options
    
def faith(caller):
    text = "Another pilgrim who wishes to be graced by Meruvia. Enter, child"
    options = [
        {
            "desc": '"My thanks"',
            "goto": "end"
        }
    ]
    return text, options
    
def warrior(caller):
    return '"Aye, we will see about that, Meruvia will bless those who battle the darkness. Go forth, and may Meruvia\'s light bless you."', []
    
def end(caller):
    return '"Go forth, and may Meruvia\'s light bless you."', []
