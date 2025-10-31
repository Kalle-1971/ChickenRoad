import json
import os

class GameSettings:
    """
    Verwaltet die Spieleinstellungen, die aus JSON-Dateien geladen werden.
    """
    
    def __init__(self):
        self.game_settings = None
        self.display_settings = None
        self.car_settings = None
        self.load_all_settings()
    
    def load_all_settings(self):
        """Lädt alle Einstellungen aus den JSON-Dateien."""
        self.load_main_settings()
        self.load_car_settings()
    
    def load_main_settings(self):
        """
        Lädt die Haupteinstellungen aus settings.json.
        Fallback auf Standardwerte, falls Datei nicht existiert.
        """
        try:
            with open('assets/settings.json', 'r') as file:
                settings_data = json.load(file)
                self.game_settings = settings_data["game_settings"]
                self.display_settings = settings_data["display_settings"]
                print("✅ Einstellungen geladen")
        except Exception as e:
            print(f"⚠️ Einstellungen konnten nicht geladen werden: {e}")
            self.set_default_settings()
    
    def load_car_settings(self):
        """Lädt die Auto-Einstellungen aus car_settings.json."""
        try:
            with open('assets/car_settings.json', 'r') as file:
                self.car_settings = json.load(file)
                print("✅ Auto-Einstellungen geladen")
        except Exception as e:
            print(f"⚠️ Auto-Einstellungen konnten nicht geladen werden: {e}")
            self.car_settings = {}
    
    def set_default_settings(self):
        """Setzt Standardwerte für die Einstellungen."""
        print("⚠️ Verwende Standardeinstellungen")
        self.game_settings = {
            "tile_size": 1,
            "level_width": 12,
            "min_car_speed": 2,
            "max_car_speed": 5,
            "car_spawn_chance": 0.18,
            "move_cooldown": 0.1,
            "tree_spawn_chance": 0.7,
            "min_trees_per_lane": 3,
            "max_trees_per_lane": 6,
            "tree_spawn_distance": 2.5,
            "cleanup_distance": 120
        }
        self.display_settings = {
            "window_fullscreen": False,  # Vorerst deaktiviert wegen Fehler
            "window_borderless": False,
            "camera_fov": 80,
            "camera_near": 0.1,
            "camera_far": 100.0
        }