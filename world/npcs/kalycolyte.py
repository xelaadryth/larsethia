OPTION_WHERE = {
    "desc": '"Where am I?"',
    "goto": "where"
}
OPTION_WHO = {
    "desc": '"Okay, what is it you do here?"',
    "goto": "who"
}
OPTION_KALL = {
    "desc": '"Who is Kall?"',
    "goto": "kall"
}


def start(caller):
    text = '"Welcome to Kall\'s Sandbox!\n\n"I am Kalycolyte, fanatic of Kall."'

    options = [
        OPTION_WHERE,
        OPTION_WHO,
        OPTION_KALL,
        {
            "desc": '"You are a freak, I\'m getting out of here!!"',
            "goto": "end"
        }
    ]

    return text, options


def where(caller):
    text = '"You\'re playing in an Kall\'s sandbox, of course!."'

    options = [
        OPTION_KALL,
        {
            "desc": '"Okay... sure, and who the hell is that?"',
            "goto": "kall"
        }
    ]

    return text, options


def who(caller):
    text = '"I praise the immortal Kall, who came before us!"'

    options = [
        {
            "desc": '"Again with this Kall guy, can I get some answers?"',
            "goto": "kall"
        },
        OPTION_WHERE
    ]

    return text, options


def kall(caller):
    text = '"KALL! THE IMMORTAL! THE SHAPER OF WORLDS! YOU STAND UPON HIS DOMAIN! YOU ARE HIS SHEEP, HIS SLAVE!"' 

    options = [
        {
            "desc": '"You\'re mad! I think I\'ll leave...?"',
            "goto": "end"
        }
    ]
    
    return text, options


def end(caller):
    return '"LoL, sure cyah nerd!"', []
