
MATERIALS = {
    'common': [
        {
            'name': 'Iron Ore',
            'type': 'material',
            'image_url': 'items/iron_ore.svg',
            'description': 'Common iron ore for basic crafting',
            'rarity': 'common',
            'guild_price': 10
        },
        {
            'name': 'Wood Log',
            'type': 'material',
            'image_url': 'items/wood_log.svg',
            'description': 'Basic wood for crafting',
            'rarity': 'common',
            'guild_price': 5
        }
    ],
    'rare': [
        {
            'name': 'Gold Ore',
            'type': 'material',
            'image_url': 'items/gold_ore.svg',
            'description': 'Rare gold ore for advanced crafting',
            'rarity': 'rare',
            'guild_price': 50
        }
    ],
    'epic': [
        {
            'name': 'Dragon Scale',
            'type': 'material',
            'image_url': 'items/dragon_scale.svg',
            'description': 'Epic crafting material from dragons',
            'rarity': 'epic',
            'guild_price': 200
        }
    ]
}

CRAFTING_RECIPES = [
    {
        'name': 'Iron Sword',
        'materials': [
            {'item': 'Iron Ore', 'quantity': 3},
            {'item': 'Wood Log', 'quantity': 1}
        ],
        'result': {
            'name': 'Iron Sword',
            'type': 'weapon',
            'damage': 15,
            'rarity': 'rare'
        },
        'points_reward': 50
    }
]
