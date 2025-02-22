import os
from flask import Flask, render_template, request, session, jsonify
from game_data import gameData
from models import db, Player, GameProgress, Item, PlayerItem, QuickSlot, CraftingRecipe, Dungeon, Monster, Guild, Quest # Added imports for Dungeon and Monster
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)
migrate = Migrate(app, db)

# Initialize database tables
with app.app_context():
    db.create_all()

# Initial game items with durability
INITIAL_ITEMS = [
    {
        'name': 'Small Bag',
        'type': 'storage',
        'image_url': 'items/small_bag.svg',
        'description': 'A small bag that increases carrying capacity',
        'max_durability': 100,
        'rarity': 'common',
        'quality': 1,
        'weight': 1,
        'max_stack': 1,
        'guild_price': 30,
        'storage_capacity': 20.0
    },
    {
        'name': 'Large Chest',
        'type': 'storage',
        'image_url': 'items/large_chest.svg',
        'description': 'A large chest that significantly increases carrying capacity',
        'max_durability': 200,
        'rarity': 'rare',
        'quality': 2,
        'weight': 5,
        'max_stack': 1,
        'guild_price': 100,
        'storage_capacity': 50.0
    },
    {
        'name': 'Wooden Sword',
        'type': 'weapon',
        'image_url': 'items/wooden_sword.svg',
        'damage': 5,
        'description': 'A basic wooden sword',
        'max_durability': 50,
        'rarity': 'common',
        'quality': 1,
        'weight': 2,
        'max_stack': 1,
        'guild_price': 0
    },
    {
        'name': 'Iron Sword',
        'type': 'weapon',
        'image_url': 'items/iron_sword.svg',
        'damage': 10,
        'description': 'A sturdy iron sword',
        'max_durability': 100,
        'rarity': 'rare',
        'quality': 2,
        'weight': 3,
        'max_stack': 1,
        'guild_price': 50
    },
    {
        'name': 'Health Potion',
        'type': 'potion',
        'image_url': 'items/health_potion.svg',
        'healing': 20,
        'description': 'Restores 20 HP',
        'max_durability': 1,  # Potions are single-use
        'rarity': 'common',
        'quality': 1,
        'weight': 1,
        'max_stack': 10,
        'guild_price': 20
    },
    {
        'name': 'Wooden Shield',
        'type': 'shield',
        'image_url': 'items/wooden_shield.svg',
        'defense': 5,
        'description': 'A basic wooden shield',
        'max_durability': 75,
        'rarity': 'common',
        'quality': 1,
        'weight': 4,
        'max_stack': 1,
        'guild_price': 0
    },
    {
        'name': 'Teleporter',
        'type': 'consumable',
        'image_url': 'items/teleporter.svg',
        'description': 'Teleports you back to the guild',
        'max_durability': 5,
        'rarity': 'rare',
        'quality': 2,
        'weight': 1,
        'max_stack': 1,
        'guild_price': 5
    }
]

def initialize_guild():
    with app.app_context():
        try:
            if Guild.query.count() == 0:
                guild = Guild(
                    name="Adventurer's Guild",
                    description="A place for adventurers to gather, trade and take on quests",
                    npc_name="Guild Master",
                    location_x=10.0,
                    location_y=0.0,
                    location_z=10.0
                )
                db.session.add(guild)

                # Add some initial quests
                quest1 = Quest(
                    guild_id=1,
                    title="Goblin Slayer",
                    description="Defeat 5 goblins in the dungeon",
                    required_level=1,
                    reward_exp=100,
                    reward_gold=50,
                    monster_kill_requirement={"goblin": 5}
                )
                db.session.add(quest1)

                quest2 = Quest(
                    guild_id=1,
                    title="Orc Hunter",
                    description="Defeat 3 orcs in the dungeon",
                    required_level=5,
                    reward_exp=300,
                    reward_gold=150,
                    monster_kill_requirement={"orc": 3}
                )
                db.session.add(quest2)
                db.session.commit()

        except Exception as e:
            app.logger.error(f"Error initializing guild: {str(e)}")
            db.session.rollback()

def initialize_items():
    with app.app_context():
        try:
            if Item.query.count() == 0:
                for item_data in INITIAL_ITEMS:
                    item = Item(**item_data)
                    db.session.add(item)
                db.session.commit()
        except Exception as e:
            app.logger.error(f"Error initializing items: {str(e)}")
            db.session.rollback()

def initialize_quick_slots(player):
    try:
        if len(player.quick_slots) == 0:
            for i in range(5):
                quick_slot = QuickSlot(player_id=player.id, slot_number=i+1)
                db.session.add(quick_slot)
            db.session.commit()
    except Exception as e:
        app.logger.error(f"Error initializing quick slots: {str(e)}")
        db.session.rollback()

def get_or_create_player():
    try:
        if 'player_id' in session:
            player = Player.query.get(session['player_id'])
            if player:
                return player

        # Create new player if not found
        player = Player()
        db.session.add(player)
        db.session.commit()
        session['player_id'] = player.id

        # Give new player initial items
        wooden_sword = Item.query.filter_by(name='Wooden Sword').first()
        if not wooden_sword:
            # Create wooden sword item if it doesn't exist
            wooden_sword = Item(
                name='Wooden Sword',
                type='weapon',
                image_url='items/wooden_sword.svg',
                damage=5,
                description='A basic wooden sword',
                max_durability=50,
                rarity='common',
                quality=1,
                weight=2,
                max_stack=1,
                guild_price=0
            )
            db.session.add(wooden_sword)
            db.session.commit()

        # Add wooden sword to player's inventory
        initial_item = PlayerItem(
            player_id=player.id,
            item_id=wooden_sword.id,
            equipped=True,
            current_durability=wooden_sword.max_durability
        )
        db.session.add(initial_item)
        db.session.commit()

        initialize_quick_slots(player)
        return player

    except Exception as e:
        app.logger.error(f"Error in get_or_create_player: {str(e)}")
        db.session.rollback()
        # Create a new session and try again
        db.session.remove()
        player = Player()
        db.session.add(player)
        db.session.commit()
        session['player_id'] = player.id
        return player

from game_materials import MATERIALS, CRAFTING_RECIPES

def initialize_materials():
    with app.app_context():
        try:
            for rarity, items in MATERIALS.items():
                for item_data in items:
                    if Item.query.filter_by(name=item_data['name']).first() is None:
                        item = Item(**item_data)
                        db.session.add(item)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error initializing materials: {str(e)}")
            db.session.rollback()

def initialize_recipes():
    with app.app_context():
        try:
            for recipe_data in CRAFTING_RECIPES:
                if CraftingRecipe.query.filter_by(name=recipe_data['name']).first() is None:
                    result_item = Item.query.filter_by(name=recipe_data['result']['name']).first()
                    if result_item:
                        recipe = CraftingRecipe(
                            name=recipe_data['name'],
                            result_item_id=result_item.id,
                            points_reward=recipe_data['points_reward']
                        )
                        db.session.add(recipe)
                        for material in recipe_data['materials']:
                            mat_item = Item.query.filter_by(name=material['item']).first()
                            if mat_item:
                                ingredient = CraftingIngredient(
                                    recipe=recipe,
                                    item_id=mat_item.id,
                                    quantity=material['quantity']
                                )
                                db.session.add(ingredient)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error initializing recipes: {str(e)}")
            db.session.rollback()

# Initialize database with items, materials and recipes
initialize_items()
initialize_materials()
initialize_recipes()
initialize_guild()

@app.route('/')
def index():
    try:
        player = get_or_create_player()
        if not player:
            app.logger.error("Failed to get or create player")
            return "Error loading game", 500

        player_data = player.to_dict()
        current_scene = player.current_scene
        return render_template('game.html', 
                             scene=gameData["scenes"][current_scene],
                             player=player_data)
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return "Error loading game", 500

@app.route('/scene', methods=['POST'])
def scene():
    player = get_or_create_player()
    currentScene = request.form['scene']
    selectedOption = request.form['option']

    nextScene = None
    for option in gameData["scenes"][currentScene]["options"]:
        if option["text"] == selectedOption:
            nextScene = option["nextScene"]

            if "points" in option:
                player.points += option["points"]

            if "weapon" in option:
                weapon_item = Item.query.filter_by(name=option["weapon"]).first()
                if weapon_item:
                    player_item = PlayerItem(player_id=player.id, item_id=weapon_item.id, current_durability=weapon_item.max_durability)
                    db.session.add(player_item)

            progress = GameProgress(player_id=player.id, scene_id=nextScene)
            db.session.add(progress)
            player.current_scene = nextScene
            db.session.commit()
            break

    return render_template('game.html', 
                         scene=gameData["scenes"][nextScene],
                         player=player.to_dict())

@app.route('/toggle_combat', methods=['POST'])
def toggle_combat():
    player = get_or_create_player()
    player.in_combat = not player.in_combat
    db.session.commit()
    return jsonify({'in_combat': player.in_combat})

@app.route('/set_quick_slot/<int:item_id>/<int:slot_number>')
def set_quick_slot(item_id, slot_number):
    if not 1 <= slot_number <= 5:
        return jsonify({'success': False, 'error': 'Invalid slot number'}), 400

    player = get_or_create_player()
    quick_slot = QuickSlot.query.filter_by(player_id=player.id, slot_number=slot_number).first()

    if quick_slot:
        quick_slot.item_id = item_id
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Quick slot not found'}), 404

@app.route('/use_item/<int:item_id>')
def use_item(item_id):
    player = get_or_create_player()
    player_item = PlayerItem.query.filter_by(player_id=player.id, item_id=item_id).first()

    if not player_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    if player_item.item.type == 'potion':
        # Potions are consumed on use
        if player_item.quantity > 1:
            player_item.quantity -= 1
        else:
            db.session.delete(player_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Potion used'})
    elif player_item.item.type in ['weapon', 'shield']:
        # Reduce durability on use
        if player_item.current_durability > 0:
            player_item.current_durability -= 1
            if player_item.current_durability <= 0:
                db.session.delete(player_item)
            db.session.commit()
            return jsonify({'success': True, 'durability': player_item.current_durability})
        else:
            return jsonify({'success': False, 'error': 'Item broken'}), 400

    return jsonify({'success': False, 'error': 'Invalid item type'}), 400

@app.route('/equip_item/<int:item_id>')
def equip_item(item_id):
    player = get_or_create_player()
    player_item = PlayerItem.query.filter_by(player_id=player.id, item_id=item_id).first()

    if not player_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    if player_item.current_durability <= 0:
        return jsonify({'success': False, 'error': 'Item is broken'}), 400

    item_type = player_item.item.type

    # For storage items, check if equipping would exceed weight limit
    if item_type == 'storage' and not player_item.equipped:
        if player.current_weight > player.calculate_total_capacity() + player_item.item.storage_capacity:
            return jsonify({'success': False, 'error': 'Current inventory too heavy for new capacity'}), 400

    # Unequip all other items of the same type (except storage)
    if item_type != 'storage':
        PlayerItem.query.filter_by(
            player_id=player.id, 
            equipped=True
        ).filter(
            PlayerItem.item.has(type=item_type)
        ).update({"equipped": False})

    # Toggle equipped state for storage items, equip for others
    if item_type == 'storage':
        player_item.equipped = not player_item.equipped
    else:
        player_item.equipped = True
        if item_type == 'weapon':
            player.current_weapon = player_item.item.name

    db.session.commit()
    return jsonify({'success': True, 'current_capacity': player.calculate_total_capacity()})


@app.route('/inventory/sort/<sort_by>')
def sort_inventory(sort_by):
    player = get_or_create_player()

    if sort_by == 'name':
        sorted_items = sorted(player.items, key=lambda x: x.item.name)
    elif sort_by == 'rarity':
        rarity_order = {'common': 0, 'rare': 1, 'epic': 2, 'legendary': 3}
        sorted_items = sorted(player.items, key=lambda x: rarity_order.get(x.item.rarity, 0)) # Handle missing rarity
    elif sort_by == 'type':
        sorted_items = sorted(player.items, key=lambda x: x.item.type)
    elif sort_by == 'quality':
        sorted_items = sorted(player.items, key=lambda x: x.item.quality, reverse=True)
    else:
        sorted_items = player.items

    return jsonify({
        'success': True,
        'inventory': [item.to_dict() for item in sorted_items]
    })

@app.route('/inventory/filter/<item_type>')
def filter_inventory(item_type):
    player = get_or_create_player()

    if item_type == 'all':
        filtered_items = player.items
    else:
        filtered_items = [item for item in player.items if item.item.type == item_type]

    return jsonify({
        'success': True,
        'inventory': [item.to_dict() for item in filtered_items]
    })

@app.route('/guild/shop')
def guild_shop():
    all_items = Item.query.filter(Item.guild_price > 0).all()
    return jsonify({
        'success': True,
        'items': [item.to_dict() for item in all_items]
    })

@app.route('/guild/purchase/<int:item_id>')
def purchase_from_guild(item_id):
    player = get_or_create_player()
    item = Item.query.get(item_id)

    if not item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    if player.points < item.guild_price:
        return jsonify({'success': False, 'error': 'Not enough points'}), 400

    # Check weight capacity
    if player.current_weight + item.weight > player.carrying_capacity:
        return jsonify({'success': False, 'error': 'Inventory too heavy'}), 400

    # Check if item is stackable and player already has it
    existing_item = PlayerItem.query.filter_by(
        player_id=player.id,
        item_id=item.id,
        equipped=False
    ).first()

    if existing_item and item.max_stack and existing_item.quantity < item.max_stack: # Corrected condition
        existing_item.quantity += 1
    else:
        # Create new inventory entry
        player_item = PlayerItem(
            player_id=player.id,
            item_id=item.id,
            current_durability=item.max_durability,
            quantity=1 # Added quantity
        )
        db.session.add(player_item)

    player.points -= item.guild_price
    player.current_weight += item.weight
    db.session.commit()

    return jsonify({'success': True, 'points_remaining': player.points})

@app.route('/crafting/recipes')
def get_crafting_recipes():
    recipes = CraftingRecipe.query.all()
    return jsonify({
        'success': True,
        'recipes': [{
            'id': recipe.id,
            'result': recipe.result_item.to_dict(),
            'ingredients': [{
                'item': ingredient.item.to_dict(),
                'quantity': ingredient.quantity
            } for ingredient in recipe.ingredients],
            'required_level': recipe.required_level,
            'points_reward': recipe.points_reward
        } for recipe in recipes]
    })

@app.route('/crafting/craft/<int:recipe_id>')
def craft_item(recipe_id):
    player = get_or_create_player()
    recipe = CraftingRecipe.query.get(recipe_id)

    if not recipe:
        return jsonify({'success': False, 'error': 'Recipe not found'}), 404

    # Check if player has all ingredients
    for ingredient in recipe.ingredients:
        player_item = PlayerItem.query.filter_by(
            player_id=player.id,
            item_id=ingredient.item_id
        ).first()

        if not player_item or player_item.quantity < ingredient.quantity:
            return jsonify({
                'success': False,
                'error': f'Missing ingredient: {ingredient.item.name}'
            }), 400

    # Remove ingredients
    for ingredient in recipe.ingredients:
        player_item = PlayerItem.query.filter_by(
            player_id=player.id,
            item_id=ingredient.item_id
        ).first()
        player_item.quantity -= ingredient.quantity
        if player_item.quantity <= 0:
            db.session.delete(player_item)

    # Add crafted item to inventory
    new_item = PlayerItem(
        player_id=player.id,
        item_id=recipe.result_item_id,
        current_durability=recipe.result_item.max_durability,
        quantity=1 # Added quantity
    )
    db.session.add(new_item)

    # Award crafting points
    player.points += recipe.points_reward

    db.session.commit()
    return jsonify({'success': True, 'points_earned': recipe.points_reward})

@app.route('/inventory/toggle_favorite/<int:item_id>')
def toggle_favorite(item_id):
    player = get_or_create_player()
    player_item = PlayerItem.query.filter_by(
        player_id=player.id,
        item_id=item_id
    ).first()

    if not player_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    player_item.is_favorite = not player_item.is_favorite
    db.session.commit()

    return jsonify({'success': True, 'is_favorite': player_item.is_favorite})

@app.route('/inventory/set_hotkey/<int:item_id>/<hotkey>')
def set_hotkey(item_id, hotkey):
    player = get_or_create_player()
    player_item = PlayerItem.query.filter_by(
        player_id=player.id,
        item_id=item_id
    ).first()

    if not player_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    # Clear this hotkey from other items
    PlayerItem.query.filter_by(
        player_id=player.id,
        hotkey=hotkey
    ).update({"hotkey": None})

    player_item.hotkey = hotkey
    db.session.commit()

    return jsonify({'success': True, 'hotkey': hotkey})

@app.route('/repair/cost/<int:item_id>')
def get_repair_cost(item_id):
    player = get_or_create_player()
    player_item = PlayerItem.query.filter_by(
        player_id=player.id,
        item_id=item_id
    ).first()

    if not player_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    missing_durability = player_item.item.max_durability - player_item.current_durability
    repair_cost = missing_durability * player_item.item.repair_cost

    return jsonify({
        'success': True,
        'repair_cost': repair_cost,
        'current_durability': player_item.current_durability,
        'max_durability': player_item.item.max_durability
    })

@app.route('/repair/item/<int:item_id>')
def repair_item(item_id):
    player = get_or_create_player()
    player_item = PlayerItem.query.filter_by(
        player_id=player.id,
        item_id=item_id
    ).first()

    if not player_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    missing_durability = player_item.item.max_durability - player_item.current_durability
    repair_cost = missing_durability * player_item.item.repair_cost

    if player.points < repair_cost:
        return jsonify({'success': False, 'error': 'Not enough points'}), 400

    player.points -= repair_cost
    player_item.current_durability = player_item.item.max_durability
    db.session.commit()

    return jsonify({
        'success': True,
        'points_remaining': player.points,
        'current_durability': player_item.current_durability
    })

# Add these new routes after the existing ones
@app.route('/dungeon/enter/<int:dungeon_id>')
def enter_dungeon(dungeon_id):
    player = get_or_create_player()
    dungeon = Dungeon.query.get(dungeon_id)

    if not dungeon:
        return jsonify({'success': False, 'error': 'Dungeon not found'}), 404

    if player.level < dungeon.level_requirement:
        return jsonify({
            'success': False, 
            'error': f'Level {dungeon.level_requirement} required'
        }), 400

    # Add player to dungeon
    if player not in dungeon.active_players:
        dungeon.active_players.append(player)
        db.session.commit()

    # Spawn initial monsters if dungeon is empty
    if dungeon.current_monsters == 0:
        if dungeon.difficulty == 1:
            for _ in range(3):
                dungeon.spawn_monster('goblin')
        elif dungeon.difficulty == 2:
            for _ in range(2):
                dungeon.spawn_monster('orc')
        else:
            dungeon.spawn_monster('dragon')

    return jsonify({
        'success': True,
        'dungeon': dungeon.to_dict()
    })

@app.route('/dungeon/leave/<int:dungeon_id>')
def leave_dungeon(dungeon_id):
    player = get_or_create_player()
    dungeon = Dungeon.query.get(dungeon_id)

    if not dungeon:
        return jsonify({'success': False, 'error': 'Dungeon not found'}), 404

    if player in dungeon.active_players:
        dungeon.active_players.remove(player)
        db.session.commit()

    return jsonify({'success': True})

@app.route('/dungeon/attack', methods=['POST'])
def attack():
    data = request.get_json()
    player = get_or_create_player()
    target_id = data.get('target_id')
    target_type = data.get('target_type')

    if not target_id or not target_type:
        return jsonify({'success': False, 'error': 'Invalid target'}), 400

    # Calculate damage based on player stats and equipment
    base_damage = 10 + (player.strength // 2)
    weapon_item = next((item for item in player.items if item.equipped and item.item.type == 'weapon'), None)
    if weapon_item:
        base_damage += weapon_item.item.damage

    if target_type == 'monster':
        monster = Monster.query.get(target_id)
        if not monster:
            return jsonify({'success': False, 'error': 'Monster not found'}), 404

        # Check if monster is in range
        distance = ((monster.position_x - data.get('player_x', 0))**2 + 
                   (monster.position_y - data.get('player_y', 0))**2)**0.5

        if distance > 5.0:  # Maximum attack range
            return jsonify({'success': False, 'error': 'Target out of range'}), 400

        # Apply damage to monster
        monster_died = monster.take_damage(base_damage, player.id, 'player')

        if monster_died:
            player.gain_experience(monster.experience_reward)
            dungeon = monster.dungeon
            dungeon.current_monsters -= 1
            db.session.delete(monster)

        db.session.commit()

        return jsonify({
            'success': True,
            'damage_dealt': base_damage,
            'monster_died': monster_died,
            'experience_gained': monster.experience_reward if monster_died else 0
        })

    return jsonify({'success': False, 'error': 'Invalid target type'}), 400

@app.route('/guild/<int:guild_id>')
def get_guild(guild_id):
    guild = Guild.query.get(guild_id)
    if not guild:
        return jsonify({'success': False, 'error': 'Guild not found'}), 404
    return jsonify({'success': True, 'guild': guild.to_dict()})

@app.route('/guild/<int:guild_id>/trade', methods=['POST'])
def trade_with_guild(guild_id):
    data = request.get_json()
    player = get_or_create_player()
    guild = Guild.query.get(guild_id)

    if not guild:
        return jsonify({'success': False, 'error': 'Guild not found'}), 404

    item_to_buy = Item.query.get(data.get('item_id'))
    if not item_to_buy or item_to_buy not in guild.tradeable_items:
        return jsonify({'success': False, 'error': 'Item not available'}), 400

    if player.points < item_to_buy.guild_price:
        return jsonify({'success': False, 'error': 'Not enough points'}), 400

    player_item = PlayerItem(
        player_id=player.id,
        item_id=item_to_buy.id,
        current_durability=item_to_buy.max_durability
    )
    player.points -= item_to_buy.guild_price
    db.session.add(player_item)
    db.session.commit()

    return jsonify({'success': True, 'points_remaining': player.points})

@app.route('/guild/<int:guild_id>/quests')
def get_guild_quests(guild_id):
    guild = Guild.query.get(guild_id)
    if not guild:
        return jsonify({'success': False, 'error': 'Guild not found'}), 404
    return jsonify({
        'success': True, 
        'quests': [quest.to_dict() for quest in guild.available_quests]
    })

@app.route('/dungeon/all')
def get_all_dungeons():
    player = get_or_create_player()
    dungeons = Dungeon.query.all()
    return jsonify({
        'success': True,
        'dungeons': [dungeon.to_dict() for dungeon in dungeons if dungeon.is_cleared or 
                    (not dungeon.previous_level_id or 
                     Dungeon.query.get(dungeon.previous_level_id).is_cleared)]
    })

@app.route('/dungeon/status/<int:dungeon_id>')
def dungeon_status(dungeon_id):
    dungeon = Dungeon.query.get(dungeon_id)
    if not dungeon:
        return jsonify({'success': False, 'error': 'Dungeon not found'}), 404

@app.route('/dungeon/complete/<int:dungeon_id>', methods=['POST'])
def complete_dungeon(dungeon_id):
    player = get_or_create_player()
    dungeon = Dungeon.query.get(dungeon_id)

    if not dungeon:
        return jsonify({'success': False, 'error': 'Dungeon not found'}), 404

    if dungeon.current_monsters > 0:
        return jsonify({'success': False, 'error': 'Defeat all monsters first'}), 400

    dungeon.is_cleared = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'Dungeon cleared!'})

@app.route('/player/update_position', methods=['POST'])
def update_player_position():
    player = get_or_create_player()
    data = request.get_json()

    player.position_x = data.get('x', player.position_x)
    player.position_y = data.get('y', player.position_y)
    player.position_z = data.get('z', player.position_z)
    player.rotation_x = data.get('rotX', player.rotation_x)
    player.rotation_y = data.get('rotY', player.rotation_y)
    player.rotation_z = data.get('rotZ', player.rotation_z)
    player.current_animation_state = data.get('animation', player.current_animation_state)

    db.session.commit()
    return jsonify({'success': True})

    return jsonify({
        'success': True,
        'dungeon': dungeon.to_dict()
    })

@app.route('/teleport', methods=['POST'])
def teleport():
    player = get_or_create_player()
    data = request.get_json()

    # Check if player has teleporter equipped
    teleporter = next((item for item in player.items 
                      if item.equipped and item.item.name == 'Teleporter'), None)

    if not teleporter:
        return jsonify({'success': False, 'error': 'No teleporter equipped'}), 400

    if teleporter.current_durability <= 0:
        return jsonify({'success': False, 'error': 'Teleporter is broken'}), 400

    # Get guild location
    guild = Guild.query.first()
    if not guild:
        return jsonify({'success': False, 'error': 'Guild not found'}), 404

    # Teleport player to guild
    player.position_x = guild.location_x
    player.position_y = guild.location_y
    player.position_z = guild.location_z
    player.current_scene = 'guild'

    # Use durability
    teleporter.current_durability -= 1
    if teleporter.current_durability <= 0:
        db.session.delete(teleporter)

    db.session.commit()
    return jsonify({'success': True, 'new_position': {
        'x': player.position_x,
        'y': player.position_y,
        'z': player.position_z
    }})

@app.route('/check_return_point', methods=['POST'])
def check_return_point():
    player = get_or_create_player()
    data = request.get_json()
    dungeon = Dungeon.query.get(data.get('dungeon_id'))

    if not dungeon:
        return jsonify({'success': False, 'error': 'Dungeon not found'}), 404

    # Check if player is standing on return point
    player_pos = (player.position_x, player.position_y, player.position_z)
    for point in dungeon.return_points.get('points', []):
        distance = ((player_pos[0] - point['x'])**2 + 
                   (player_pos[1] - point['y'])**2 + 
                   (player_pos[2] - point['z'])**2)**0.5
        if distance < 2.0:  # Within 2 units of return point
            # Teleport to guild
            guild = Guild.query.first()
            if guild:
                player.position_x = guild.location_x
                player.position_y = guild.location_y
                player.position_z = guild.location_z
                player.current_scene = 'guild'
                db.session.commit()
                return jsonify({'success': True, 'teleported': True})

    return jsonify({'success': True, 'teleported': False})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
@app.route('/download')
def download_project():
    import os
    import zipfile
    from io import BytesIO
    from flask import send_file

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Walk through the flask_game directory
        for root, dirs, files in os.walk('flask_game'):
            for file in files:
                if '__pycache__' not in root and not file.endswith('.pyc'):
                    file_path = os.path.join(root, file)
                    zf.write(file_path)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='flask_game.zip'
    )

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

from models import PlayerItem, CraftingRecipe, CraftingIngredient, RecipeMaterial, Guild, Quest

def get_or_create_player():
    try:
        player = Player.query.filter_by(id=session.get('player_id')).first()
        if not player:
            player = Player()
            db.session.add(player)
            db.session.commit()
            session['player_id'] = player.id

        # Initialize player with some items
        wooden_sword = Item.query.filter_by(name="Wooden Sword").first()
        if wooden_sword:
            initial_item = PlayerItem(
                player_id=player.id,
                item_id=wooden_sword.id,
                equipped=True,
                current_durability=wooden_sword.max_durability
            )
            db.session.add(initial_item)
            db.session.commit()

        initialize_quick_slots(player)
        return player

    except Exception as e:
        app.logger.error(f"Error in get_or_create_player: {str(e)}")
        db.session.rollback()
        # Create a new session and try again
        db.session.remove()
        player = Player()
        db.session.add(player)
        db.session.commit()
        session['player_id'] = player.id
        return player

from game_materials import MATERIALS, CRAFTING_RECIPES

def initialize_materials():
    with app.app_context():
        try:
            for rarity, items in MATERIALS.items():
                for item_data in items:
                    if Item.query.filter_by(name=item_data['name']).first() is None:
                        item = Item(**item_data)
                        db.session.add(item)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error initializing materials: {str(e)}")
            db.session.rollback()

def initialize_recipes():
    with app.app_context():
        try:
            for recipe_data in CRAFTING_RECIPES:
                if CraftingRecipe.query.filter_by(name=recipe_data['name']).first() is None:
                    result_item = Item.query.filter_by(name=recipe_data['result']['name']).first()
                    if result_item:
                        recipe = CraftingRecipe(
                            name=recipe_data['name'],
                            result_item_id=result_item.id,
                            points_reward=recipe_data['points_reward']
                        )
                        db.session.add(recipe)
                        for material in recipe_data['materials']:
                            mat_item = Item.query.filter_by(name=material['item']).first()
                            if mat_item:
                                ingredient = CraftingIngredient(
                                    recipe=recipe,
                                    item_id=mat_item.id,
                                    quantity=material['quantity']
                                )
                                db.session.add(ingredient)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error initializing recipes: {str(e)}")
            db.session.rollback()

# Initialize database with items, materials and recipes
initialize_items()
initialize_materials()
initialize_recipes()
initialize_guild()

@app.route('/')
def index():
    try:
        player = get_or_create_player()
        if not player:
            app.logger.error("Failed to get or create player")
            return "Error loading game", 500

        player_data = player.to_dict()
        current_scene = player.current_scene
        return render_template('game.html', 
                             scene=gameData["scenes"][current_scene],
                             player=player_data)
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return "Error loading game", 500

@app.route('/scene', methods=['POST'])
def scene():
    player = get_or_create_player()
    currentScene = request.form['scene']
    selectedOption = request.form['option']

    nextScene = None
    for option in gameData["scenes"][currentScene]["options"]:
        if option["text"] == selectedOption:
            nextScene = option["nextScene"]

            if "points" in option:
                player.points += option["points"]

            if "weapon" in option:
                weapon_item = Item.query.filter_by(name=option["weapon"]).first()
                if weapon_item:
                    player_item = PlayerItem(player_id=player.id, item_id=weapon_item.id, current_durability=weapon_item.max_durability)
                    db.session.add(player_item)
