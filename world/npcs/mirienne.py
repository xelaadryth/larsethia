from world.quests.lost_kitten import INTERNAL_NAME, LostKitten


def start(caller):
    quest_status = caller.quest_status(INTERNAL_NAME)
    if quest_status == 0:
        text = 'Mirienne smiles at you and waves Edna\'s tiny paw at you as you approach.\n\n"How can I help you?"'
        options = [
            {
                "desc": '"Oh no need, I\'ll be on my way."',
                "goto": "end"
            }
        ]
    elif quest_status is None:
        text = ('Mirienne looks up from her searching as you approach her. '
                'She smiles and asks, "Why hello there, how can I help you?')
        options = [
            {
                "desc": '"Actually, I was wondering if I could help YOU. Did you lose something?"',
                "goto": "search"
            },
            {
                "desc": '"Oh no need, I\'ll be on my way."',
                "goto": "end"
            }
        ]
    else:
        # Currently on the quest
        text = 'Mirienne looks up from her searching and smiles hopefully. "Any luck finding the cat?" she inquires.'
        options = [
            {
                "desc": '"Sorry, no luck. I\'ll keep looking."',
                "goto": "end"
            }
        ]
        if quest_status == 2:
            text = ('Mirienne looks up from her searching and smiles hopefully.\n\n'
                    '"Any luck finding the cat?" she inquires.')
            options.insert(0, {
                "desc": "Hand her the kitten.",
                "goto": "kitten"
            })

    return text, options


def search(caller):
    text = ('"Actually, yes! I can\'t seem to find my kitten. I had her with me while I was shopping in the market, '
            'but I put her down for just one second when I reached the square and now I can\'t seem to find her!"\n\n'
            'She seems pretty calm about the whole situation; you figure this probably happens a lot.')
    options = [
        {
            "desc": '"I\'ll keep an eye out for her."',
            "goto": "end"
        }
    ]

    caller.quest_advance(INTERNAL_NAME, 1)

    return text, options


def kitten(caller):
    text = ('"Oh Edna, there you are! Come here!" Mirienne lifts the kitten from your arms and beams at you. '
            'Your face pales. After all, if Mirienne named you something like Edna you\'d probably run '
            'away from her too. The kitten seems happy enough though.\n\n'
            '"Thank you so much for your help. I\'m in your debt!" she says, smiling. She lifts Edna\'s tiny kitten '
            'paw and waves goodbye.\n\n'
            'You feel a little more perceptive.')

    for obj in caller.contents:
        if isinstance(obj, LostKitten):
            obj.delete()

    # TODO: Increase perception skill
    caller.quest_complete(INTERNAL_NAME)

    return text, []


def end(caller):
    quest_status = caller.quest_status(INTERNAL_NAME)
    if quest_status is None:
        text = '"Have a wonderful day!" Mirienne says, and goes back to searching.'
    else:
        text = '"Let me know if you find anything!"'

    return text, []
