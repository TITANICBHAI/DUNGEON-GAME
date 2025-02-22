from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    current_scene = db.Column(db.String(50), default="entrance")
    inventory_slots = db.Column(db.Integer, default=20)
    current_weapon = db.Column(db.String(50), default="Wood Sword")
    items = db.relationship('PlayerItem', backref='player', lazy=True)
    quick_slots = db.relationship('QuickSlot', backref='player', lazy=True)
    in_combat = db.Column(db.Boolean, default=False)
    carrying_capacity = db.Column(db.Float, default=50.0)
    current_weight = db.Column(db.Float, default=0.0)

    # New character attributes
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    skill_points = db.Column(db.Integer, default=0)

    # Base stats
    strength = db.Column(db.Integer, default=10)
    dexterity = db.Column(db.Integer, default=10)
    intelligence = db.Column(db.Integer, default=10)
    vitality = db.Column(db.Integer, default=10)

    # Combat stats
    max_health = db.Column(db.Integer, default=100)
    current_health = db.Column(db.Integer, default=100)
    max_mana = db.Column(db.Integer, default=50)
    current_mana = db.Column(db.Integer, default=50)

    # Animation state flags
    current_animation = db.Column(db.String(50), default="idle")
    movement_state = db.Column(db.String(50), default="standing")
    
    # 3D Position and Rotation
    position_x = db.Column(db.Float, default=0.0)
    position_y = db.Column(db.Float, default=0.0)
    position_z = db.Column(db.Float, default=0.0)
    rotation_x = db.Column(db.Float, default=0.0)
    rotation_y = db.Column(db.Float, default=0.0)
    rotation_z = db.Column(db.Float, default=0.0)
    current_animation_state = db.Column(db.String(50), default="idle")

    # Relationships
    skills = db.relationship('PlayerSkill', backref='player', lazy=True)

    def gain_experience(self, amount):
        self.experience += amount
        level_up_exp = self.level * 100  # Simple level up formula

        while self.experience >= level_up_exp:
            self.level_up()
            level_up_exp = self.level * 100

    def level_up(self):
        self.level += 1
        self.skill_points += 2
        self.max_health += 10
        self.current_health = self.max_health
        self.max_mana += 5
        self.current_mana = self.max_mana
        
    def calculate_total_capacity(self):
        base_capacity = self.carrying_capacity
        for item in self.items:
            if item.item.type == 'storage' and item.equipped:
                base_capacity += item.item.storage_capacity
        return base_capacity

    def to_dict(self):
        return {
            'points': self.points,
            'current_scene': self.current_scene,
            'position': {
                'x': self.position_x,
                'y': self.position_y,
                'z': self.position_z
            },
            'rotation': {
                'x': self.rotation_x,
                'y': self.rotation_y,
                'z': self.rotation_z
            },
            'animation_state': self.current_animation_state,
            'inventory_slots': self.inventory_slots,
            'current_weapon': self.current_weapon,
            'inventory': [item.to_dict() for item in self.items],
            'quick_slots': [slot.to_dict() for slot in self.quick_slots],
            'in_combat': self.in_combat,
            'carrying_capacity': self.carrying_capacity,
            'current_weight': self.current_weight,
            'level': self.level,
            'experience': self.experience,
            'skill_points': self.skill_points,
            'stats': {
                'strength': self.strength,
                'dexterity': self.dexterity,
                'intelligence': self.intelligence,
                'vitality': self.vitality,
                'health': f"{self.current_health}/{self.max_health}",
                'mana': f"{self.current_mana}/{self.max_mana}"
            },
            'skills': [skill.to_dict() for skill in self.skills]
        }

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    skill_tree = db.Column(db.String(50))  # e.g., "combat", "magic", "crafting"
    required_level = db.Column(db.Integer, default=1)
    mana_cost = db.Column(db.Integer, default=0)
    cooldown = db.Column(db.Float, default=0.0)  # in seconds
    animation_id = db.Column(db.String(100))  # Reference to 3D animation
    icon_url = db.Column(db.String(200))
    prerequisites = db.Column(db.JSON)  # Required skills to learn this one

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'skill_tree': self.skill_tree,
            'required_level': self.required_level,
            'mana_cost': self.mana_cost,
            'cooldown': self.cooldown,
            'animation_id': self.animation_id,
            'icon_url': self.icon_url,
            'prerequisites': self.prerequisites
        }

class PlayerSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)

    skill = db.relationship('Skill')

    def to_dict(self):
        skill_dict = self.skill.to_dict()
        skill_dict.update({
            'level': self.level,
            'is_active': self.is_active,
            'last_used': self.last_used.isoformat() if self.last_used else None
        })
        return skill_dict

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    rarity = db.Column(db.String(20), default='common')
    texture_url = db.Column(db.String(200))  # For 3D model textures
    material_type = db.Column(db.String(50))  # e.g., "metal", "wood", "cloth"
    properties = db.Column(db.JSON)  # Physical properties for 3D rendering

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rarity': self.rarity,
            'texture_url': self.texture_url,
            'material_type': self.material_type,
            'properties': self.properties
        }

class GameProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    scene_id = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    visited_at = db.Column(db.DateTime, server_default=db.func.now())
    player = db.relationship('Player', backref=db.backref('progress', lazy=True))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # weapon, potion, shield, storage etc.
    storage_capacity = db.Column(db.Float, default=0.0)  # Additional carrying capacity for storage items
    image_url = db.Column(db.String(200), nullable=False)
    damage = db.Column(db.Integer, default=0)  # for weapons
    defense = db.Column(db.Integer, default=0)  # for shields
    healing = db.Column(db.Integer, default=0)  # for potions
    description = db.Column(db.Text)
    max_durability = db.Column(db.Integer, default=100)  # Durability for equipment
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    quality = db.Column(db.Integer, default=1)  # 1-100 quality rating
    weight = db.Column(db.Float, default=1.0)  # Weight in inventory
    stackable = db.Column(db.Boolean, default=False)  # Can items stack?
    max_stack = db.Column(db.Integer, default=1)  # Maximum stack size
    guild_price = db.Column(db.Integer, default=100)  # Cost in guild points
    is_quest_item = db.Column(db.Boolean, default=False)  # Quest items can't be sold/dropped
    crafting_difficulty = db.Column(db.Integer, default=1)  # Difficulty to craft (1-10)
    repair_cost = db.Column(db.Integer, default=10)  # Cost to repair in guild points

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'image_url': self.image_url,
            'damage': self.damage,
            'defense': self.defense,
            'healing': self.healing,
            'description': self.description,
            'max_durability': self.max_durability,
            'rarity': self.rarity,
            'quality': self.quality,
            'weight': self.weight,
            'stackable': self.stackable,
            'max_stack': self.max_stack,
            'guild_price': self.guild_price,
            'is_quest_item': self.is_quest_item,
            'crafting_difficulty': self.crafting_difficulty
        }

class PlayerItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    equipped = db.Column(db.Boolean, default=False)
    current_durability = db.Column(db.Integer)
    is_favorite = db.Column(db.Boolean, default=False)  # For marking favorites
    hotkey = db.Column(db.String(10))  # For hotkey assignment

    item = db.relationship('Item')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.item:
            self.current_durability = self.item.max_durability

    def to_dict(self):
        item_dict = self.item.to_dict()
        item_dict.update({
            'quantity': self.quantity,
            'equipped': self.equipped,
            'current_durability': self.current_durability,
            'is_favorite': self.is_favorite,
            'hotkey': self.hotkey
        })
        return item_dict

class QuickSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    slot_number = db.Column(db.Integer, nullable=False)  # 1-5 for quick slots
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)

    item = db.relationship('Item')

    def to_dict(self):
        return {
            'slot_number': self.slot_number,
            'item': self.item.to_dict() if self.item else None
        }

class CraftingRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    required_level = db.Column(db.Integer, default=1)
    points_reward = db.Column(db.Integer, default=10)
    required_skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))  # New: Required crafting skill
    difficulty = db.Column(db.Integer, default=1)  # 1-10 scale
    crafting_time = db.Column(db.Float, default=1.0)  # Time in seconds
    crafting_animation = db.Column(db.String(100))  # Animation to play while crafting

    result_item = db.relationship('Item', foreign_keys=[result_item_id])
    required_skill = db.relationship('Skill', foreign_keys=[required_skill_id])
    ingredients = db.relationship('CraftingIngredient', backref='recipe', lazy=True)
    materials = db.relationship('RecipeMaterial', backref='recipe', lazy=True)

class CraftingIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('crafting_recipe.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    item = db.relationship('Item')

class RecipeMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('crafting_recipe.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    material = db.relationship('Material')


class Guild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location_x = db.Column(db.Float, default=0.0)
    location_y = db.Column(db.Float, default=0.0)
    location_z = db.Column(db.Float, default=0.0)
    npc_name = db.Column(db.String(100))
    available_quests = db.relationship('Quest', backref='guild', lazy=True)
    tradeable_items = db.relationship('Item', secondary='guild_items')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'npc_name': self.npc_name,
            'location': {'x': self.location_x, 'y': self.location_y, 'z': self.location_z},
            'quests': [quest.to_dict() for quest in self.available_quests],
            'items': [item.to_dict() for item in self.tradeable_items]
        }

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    required_level = db.Column(db.Integer, default=1)
    reward_exp = db.Column(db.Integer, default=100)
    reward_gold = db.Column(db.Integer, default=50)
    reward_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    monster_kill_requirement = db.Column(db.JSON)  # {"monster_type": count}
    is_completed = db.Column(db.Boolean, default=False)

    reward_item = db.relationship('Item')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'required_level': self.required_level,
            'rewards': {
                'exp': self.reward_exp,
                'gold': self.reward_gold,
                'item': self.reward_item.to_dict() if self.reward_item else None
            },
            'requirements': self.monster_kill_requirement,
            'is_completed': self.is_completed
        }

# Association table for guild tradeable items
guild_items = db.Table('guild_items',
    db.Column('guild_id', db.Integer, db.ForeignKey('guild.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
)

class Monster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # goblin, orc, dragon
    level = db.Column(db.Integer, default=1)
    max_health = db.Column(db.Integer, nullable=False)
    current_health = db.Column(db.Integer)
    damage = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, default=0)
    experience_reward = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)  # 1: easy, 2: medium, 3: hard
    is_aggressive = db.Column(db.Boolean, default=True)
    attack_range = db.Column(db.Float, default=1.0)  # For ranged attacks
    attack_width = db.Column(db.Float, default=1.0)  # For wide attacks
    current_target_id = db.Column(db.Integer)  # ID of current target (player or monster)
    target_type = db.Column(db.String(20))  # 'player' or 'monster'
    position_x = db.Column(db.Float, default=0.0)
    position_y = db.Column(db.Float, default=0.0)
    position_z = db.Column(db.Float, default=0.0)
    dungeon_id = db.Column(db.Integer, db.ForeignKey('dungeon.id'))
    animation_state = db.Column(db.String(50), default='idle')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_health = self.max_health

    def take_damage(self, damage, attacker_id, attacker_type):
        self.current_health -= max(0, damage - self.defense)
        if self.current_health <= 0:
            self.current_health = 0
            return True  # Monster died

        # If attacked by another monster, become aggressive towards them
        if attacker_type == 'monster' and attacker_id != self.id:
            self.current_target_id = attacker_id
            self.target_type = 'monster'
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'level': self.level,
            'health': f"{self.current_health}/{self.max_health}",
            'damage': self.damage,
            'defense': self.defense,
            'difficulty': self.difficulty,
            'position': {
                'x': self.position_x,
                'y': self.position_y,
                'z': self.position_z
            },
            'animation_state': self.animation_state
        }

class Dungeon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    return_points = db.Column(db.JSON, default=lambda: {'points': []})  # List of x,y,z coordinates
    level_requirement = db.Column(db.Integer, default=1)
    difficulty = db.Column(db.Integer, default=1)
    dungeon_level = db.Column(db.Integer, default=1)  # Current level of dungeon
    is_boss_level = db.Column(db.Boolean, default=False)
    previous_level_id = db.Column(db.Integer, db.ForeignKey('dungeon.id'))
    next_level_id = db.Column(db.Integer, db.ForeignKey('dungeon.id'))
    is_cleared = db.Column(db.Boolean, default=False)
    max_monsters = db.Column(db.Integer, default=10)
    current_monsters = db.Column(db.Integer, default=0)
    size_x = db.Column(db.Float, default=100.0)  # Dungeon dimensions
    size_y = db.Column(db.Float, default=100.0)
    size_z = db.Column(db.Float, default=20.0)

    monsters = db.relationship('Monster', backref='dungeon', lazy=True)
    active_players = db.relationship('Player', secondary='dungeon_players')

    def spawn_monster(self, monster_type):
        if self.current_monsters >= self.max_monsters:
            return None

        monster_data = MONSTER_TYPES.get(monster_type)
        if not monster_data:
            return None

        # Random position within dungeon bounds
        import random
        x = random.uniform(0, self.size_x)
        y = random.uniform(0, self.size_y)
        z = 0  # Ground level

        monster = Monster(
            name=f"{monster_type.capitalize()} {self.current_monsters + 1}",
            type=monster_type,
            max_health=monster_data['health'],
            damage=monster_data['damage'],
            defense=monster_data['defense'],
            difficulty=monster_data['difficulty'],
            experience_reward=monster_data['exp_reward'],
            position_x=x,
            position_y=y,
            position_z=z,
            dungeon_id=self.id
        )
        db.session.add(monster)
        self.current_monsters += 1
        db.session.commit()
        return monster

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level_requirement': self.level_requirement,
            'difficulty': self.difficulty,
            'monsters': [monster.to_dict() for monster in self.monsters],
            'monster_count': f"{self.current_monsters}/{self.max_monsters}"
        }

# Association table for players in dungeons
dungeon_players = db.Table('dungeon_players',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key=True),
    db.Column('dungeon_id', db.Integer, db.ForeignKey('dungeon.id'), primary_key=True)
)

# Monster type definitions
MONSTER_TYPES = {
    'goblin': {
        'health': 50,
        'damage': 5,
        'defense': 2,
        'difficulty': 1,
        'exp_reward': 20,
        'attack_range': 1.0,
        'attack_width': 1.0
    },
    'orc': {
        'health': 100,
        'damage': 15,
        'defense': 5,
        'difficulty': 2,
        'exp_reward': 50,
        'attack_range': 2.0,
        'attack_width': 2.0
    },
    'dragon': {
        'health': 500,
        'damage': 50,
        'defense': 20,
        'difficulty': 3,
        'exp_reward': 200,
        'attack_range': 5.0,
        'attack_width': 3.0
    }
}