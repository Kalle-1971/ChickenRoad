from ursina import *
import time

class Player(Entity):
    """
    Repräsentiert den Spieler-Charakter mit Bewegungslogik und Animationen.
    """
    
    def __init__(self, start_position=(0, 1.0, 0)):
        # Verwende einen einfachen Würfel als Fallback, falls das Modell nicht geladen werden kann
        try:
            super().__init__(
                model='assets/models/crossy_road_style_yellow_chicken.glb',
                position=start_position,
                rotation=(0, 180, 0),
                collider='box'
            )
        except Exception as e:
            print(f"⚠️ Spieler-Modell konnte nicht geladen werden: {e}")
            super().__init__(
                model='cube',
                position=start_position,
                rotation=(0, 180, 0),
                color=color.yellow,
                collider='box'
            )
            
        self.base_scale = 1
        self.base_y_position = 1
        self.last_move_time = 0
        self.move_cooldown = 0.1
        
        # Größe anpassen
        self.fit_player_to_height(1.6)
        self.last_position = self.position
    
    def fit_player_to_height(self, target_height=1.6):
        """
        Passt die Spielergröße an die gewünschte Höhe an.
        """
        try:
            bounds = self.bounds
            model_height = bounds.size.y
            if model_height <= 0:
                print("⚠️ Warnung: Player-Modell hat ungültige Höhe!")
                return
            
            scale_factor = target_height / model_height
            self.scale = scale_factor
            self.base_scale = scale_factor
            self.y = target_height / 2.0
        except Exception as e:
            print(f"⚠️ Spieler-Höhe konnte nicht angepasst werden: {e}")
            # Fallback
            self.scale = 0.5
            self.base_scale = 0.5
    
    def face_direction(self, target_angle):
        """Lässt den Spieler in eine Richtung schauen."""
        self.animate_rotation_y(target_angle, duration=0.15, curve=curve.linear)
    
    def hop(self):
        """Lässt den Spieler einen kleinen Hopser machen."""
        try:
            self.animate_y(
                self.base_y_position + 0.3,
                duration=0.12,
                curve=curve.out_quad
            )
            invoke(
                self.animate_y,
                self.base_y_position,
                duration=0.12,
                delay=0.12,
                curve=curve.in_quad
            )
        except Exception as e:
            print(f"⚠️ Hop-Animation fehlgeschlagen: {e}")
    
    def can_move(self):
        """Prüft, ob der Spieler sich bewegen darf (Cooldown)."""
        return time.time() - self.last_move_time >= self.move_cooldown
    
    def update_move_time(self):
        """Aktualisiert den Zeitpunkt der letzten Bewegung."""
        self.last_move_time = time.time()