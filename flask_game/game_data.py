gameData = {
    "startScene": "entrance",
    "scenes": {
        "entrance": {
            "text": "You stand before an ancient dungeon entrance...",
            "image": "entrance.jpg",
            "model_path": "models/entrance.glb",
            "ambient_light": {"r": 0.5, "g": 0.5, "b": 0.5},
            "spawn_point": {"x": 0, "y": 0, "z": 0},  
            "animation_path": "animations/entrance_animation.glb",
            "options": [
                {"text": "Enter", "nextScene": "mainHall", "points": 5},
                {"text": "Inspect", "nextScene": "entranceInspect", "points": 2}
            ]
        },
        "mainHall": {
            "text": "You enter the main hall...",
            "image": "main_hall.jpg",
            "model_path": "models/main_hall.glb",
            "animation_path": "animations/main_hall_animation.glb",
            "options": [
                {"text": "Go left", "nextScene": "room1"},
                {"text": "Go right", "nextScene": "room2"}
            ]
        },
        "entranceInspect": {
            "text": "You find a rusty sword...",
            "image": "rusty_sword.jpg",
            "model_path": "models/rusty_sword.glb",
            "animation_path": "animations/rusty_sword_animation.glb",
            "options": [
                {"text": "Take sword", "nextScene": "mainHall", "points": 10, "weapon": "Rusty Sword"},
                {"text": "Leave sword", "nextScene": "mainHall", "points": 5}
            ]
        },
        "room1": {
            "text": "You are in room 1...",
            "image": "room1.jpg",
            "model_path": "models/room1.glb",
            "animation_path": "animations/room1_animation.glb",
            "options": [
                {"text": "Go back", "nextScene": "mainHall"}
            ]
        },
        "room2": {
            "text": "You are in room 2...",
            "image": "room2.jpg",
            "model_path": "models/room2.glb",
            "animation_path": "animations/room2_animation.glb",
            "options": [
                {"text": "Go back", "nextScene": "mainHall"}
            ]
        }
    }
}
