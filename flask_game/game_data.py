gameData = {
    "startScene": "entrance",
    "scenes": {
        "entrance": {
            "text": "You stand before an ancient dungeon entrance...",
            "image": "entrance.jpg",
            "model_path": "models/entrance.glb",
            "ambient_light": {"r": 0.5, "g": 0.5, "b": 0.5},
            "spawn_point": {"x": 0, "y": 0, "z": 0},  
            "options": [
                {"text": "Enter", "nextScene": "mainHall", "points": 5},
                {"text": "Inspect", "nextScene": "entranceInspect", "points": 2}
            ]
        },
        "mainHall": {
            "text": "You enter the main hall...",
            "image": "main_hall.jpg",
            "options": [
                {"text": "Go left", "nextScene": "room1"},
                {"text": "Go right", "nextScene": "room2"}
            ]
        },
        "entranceInspect": {
            "text": "You find a rusty sword...",
            "image": "rusty_sword.jpg",
            "options": [
                {"text": "Take sword", "nextScene": "mainHall", "points": 10, "weapon": "Rusty Sword"},
                {"text": "Leave sword", "nextScene": "mainHall", "points": 5}
            ]
        },
        "room1": {
            "text": "You are in room 1...",
            "image": "room1.jpg",
            "options": [
                {"text": "Go back", "nextScene": "mainHall"}
            ]
        },
        "room2": {
            "text": "You are in room 2...",
            "image": "room2.jpg",
            "options": [
                {"text": "Go back", "nextScene": "mainHall"}
            ]
        }
    }
}