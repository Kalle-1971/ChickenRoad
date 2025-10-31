from ursina import *
from modules.game_settings import GameSettings
from modules.highscore_manager import HighscoreManager
from modules.player import Player
from modules.world_generator import WorldGenerator
from modules.car_manager import CarManager
from modules.ui_manager import UIManager

class GameController:
    """
    Hauptcontroller, der alle Spielkomponenten koordiniert.
    """
    
    def __init__(self):
        # ZUERST Ursina initialisieren
        self.app = Ursina()
        
        # DANACH die anderen Komponenten initialisieren
        self.settings_manager = GameSettings()
        self.highscore_manager = HighscoreManager()
        
        # Spielzustand
        self.game_paused = False
        self.is_game_over = False
        self.start_z_position = 0
        self.tile_size = self.settings_manager.game_settings["tile_size"]
        self.level_width = self.settings_manager.game_settings["level_width"]
        self.max_x_tiles = self.level_width // 2
        self.min_car_speed = self.settings_manager.game_settings["min_car_speed"]
        self.max_car_speed = self.settings_manager.game_settings["max_car_speed"]
        self.car_spawn_chance = self.settings_manager.game_settings["car_spawn_chance"]
        self.move_cooldown = self.settings_manager.game_settings["move_cooldown"]
        self.last_move_time = 0
        
        # Fenster und Kamera setup
        self.setup_window()
        self.setup_lighting()
        self.setup_camera()
        
        # JETZT erst die Spielkomponenten initialisieren (nach Ursina)
        self.world_generator = WorldGenerator(self.settings_manager.game_settings)
        self.car_manager = CarManager(
            self.settings_manager.game_settings, 
            self.settings_manager.car_settings
        )
        self.ui_manager = UIManager(self.highscore_manager)
        self.player = Player(start_position=(0, 1.0, 0))
        
        self.create_initial_world()
        
        # WICHTIG: Ursina Input-Handler direkt überschreiben
        self.setup_ursina_handlers()
        
        print("✅ Spiel erfolgreich initialisiert")
    
    def setup_ursina_handlers(self):
        """Setzt die Input- und Update-Handler für Ursina direkt."""
        # Überschreibe die globalen Ursina-Funktionen
        def handle_input(key):
            self.handle_player_input(key)
        
        def handle_update():
            self.game_update()
        
        # Weise die Funktionen direkt zu
        self.app.input = handle_input
        self.app.update = handle_update
    
    def setup_window(self):
        """Konfiguriert das Fenster und die Anzeigeeinstellungen."""
        display_settings = self.settings_manager.display_settings
        
        window.fullscreen = False
        window.borderless = display_settings.get("window_borderless", False)
        window.title = 'Crossy Road Clone'
        window.exit_button.visible = False
        
        mouse.visible = False
        mouse.enabled = False
    
    def setup_lighting(self):
        """Richtet die Beleuchtung der Szene ein."""
        DirectionalLight(shadows=False, rotation=(45, -45, 45))
        AmbientLight(color=color.rgb(200, 200, 200))
    
    def setup_camera(self):
        """Positioniert und konfiguriert die Kamera."""
        display_settings = self.settings_manager.display_settings
        
        camera.position = (8, 14, -13)
        camera.rotation_x = 55
        camera.rotation_y = -45
        camera.fov = display_settings.get("camera_fov", 80)
    
    def create_initial_world(self):
        """Erstellt die initiale Spielwelt."""
        print("🌍 Erstelle Spielwelt...")
        self.world_generator.create_play_area_border()
        self.world_generator.create_backward_lanes(5)
        
        for i in range(15):
            self.world_generator.create_lane(self.start_z_position + i)
        
        self.world_generator.extend_level(5)
        print(f"✅ Spielwelt erstellt: {len(self.world_generator.tiles)} Tiles, {len(self.world_generator.trees)} Bäume, {len(self.world_generator.lanes)} Lanes")
    
    def handle_player_input(self, key):
        """
        Verarbeitet Spielereingaben.
        
        Args:
            key (str): Die gedrückte Taste
        """
        # Debug-Ausgabe um zu sehen, ob Tasten erkannt werden
        if key in ['w', 'a', 's', 'd', 'escape']:
            print(f"🎮 Tastendruck erkannt: {key}")
        
        # Pause-Menü Eingaben
        if self.ui_manager.game_paused:
            should_restart, should_quit = self.ui_manager.handle_pause_input(key)
            if should_restart:
                self.restart_game()
            elif should_quit:
                application.quit()
            return
        
        # Normale Spiel-Eingaben
        if self.ui_manager.game_paused or self.ui_manager.is_game_over:
            return
        
        # Cooldown prüfen
        if time.time() - self.last_move_time < self.move_cooldown:
            return
        
        if key == 'escape':
            self.ui_manager.show_pause_menu()
            return
        
        old_position = self.player.position
        moved = False
        
        if key == 'w':
            self.move_player_forward()
            moved = True
        elif key == 's' and self.player.z - self.tile_size >= self.start_z_position:
            self.move_player_backward()
            moved = True
        elif key == 'a' and self.player.x - self.tile_size >= -self.max_x_tiles:
            self.move_player_left()
            moved = True
        elif key == 'd' and self.player.x + self.tile_size <= self.max_x_tiles:
            self.move_player_right()
            moved = True
        
        if moved:
            self.handle_player_movement(old_position)
    
    def move_player_forward(self):
        """Bewegt den Spieler vorwärts."""
        self.player.z += self.tile_size
        self.player.face_direction(0)
        self.player.hop()
        self.world_generator.extend_level(1)
        print(f"🎯 Spieler bewegt nach vorne: Z={self.player.z}")
    
    def move_player_backward(self):
        """Bewegt den Spieler rückwärts."""
        self.player.z -= self.tile_size
        self.player.face_direction(180)
        self.player.hop()
        print(f"🎯 Spieler bewegt nach hinten: Z={self.player.z}")
    
    def move_player_left(self):
        """Bewegt den Spieler nach links."""
        self.player.x -= self.tile_size
        self.player.face_direction(-90)
        self.player.hop()
        print(f"🎯 Spieler bewegt nach links: X={self.player.x}")
    
    def move_player_right(self):
        """Bewegt den Spieler nach rechts."""
        self.player.x += self.tile_size
        self.player.face_direction(90)
        self.player.hop()
        print(f"🎯 Spieler bewegt nach rechts: X={self.player.x}")
    
    def handle_player_movement(self, old_position):
        """
        Verarbeitet die Spielerbewegung und Kollisionserkennung.
        
        Args:
            old_position (Vec3): Die Position vor der Bewegung
        """
        collision_occurred = self.check_tree_collision()
        
        if collision_occurred:
            # Bewegung rückgängig machen
            self.player.position = old_position
            # Visuelles Feedback
            self.player.color = color.red
            invoke(setattr, self.player, 'color', color.white, delay=0.2)
            print("🚫 Bewegung blockiert: Kollision mit Baum")
        else:
            self.player.update_move_time()
            self.last_move_time = time.time()
    
    def check_tree_collision(self):
        """
        Prüft Kollisionen mit Bäumen.
        
        Returns:
            bool: True bei Kollision, sonst False
        """
        for tree in self.world_generator.trees:
            if abs(tree.x) <= self.max_x_tiles + 0.5:
                if distance(self.player.position, tree.position) < 1.5:
                    if self.player.intersects(tree).hit:
                        return True
        return False
    
    def game_update(self):
        """Wird jeden Frame aufgerufen, um die Spielogik zu aktualisieren."""
        if not self.ui_manager.game_paused:
            self.update_camera()
        
        # Aufräumen
        self.world_generator.cleanup_old_objects(self.player.z)
        
        # Score aktualisieren
        self.ui_manager.update_score(self.player.z, self.start_z_position)
        
        # Autos aktualisieren
        self.car_manager.update_cars()
        
        # Auto-Spawning
        if random.random() < self.car_spawn_chance:
            road_lane_indices = [
                lane['index'] for lane in self.world_generator.lanes 
                if lane['type'] == 'road'
            ]
            if road_lane_indices:
                self.car_manager.spawn_car(
                    random.choice(road_lane_indices), 
                    self.world_generator.lanes
                )
        
        # Kollisionsprüfung mit Autos
        if self.car_manager.check_collision_with_player(self.player):
            self.player.color = color.black
            self.ui_manager.show_pause_menu(game_over=True)
            print("💥 Kollision mit Auto!")
    
    def update_camera(self):
        """Aktualisiert die Kameraposition, um dem Spieler zu folgen."""
        safe_x = max(-self.max_x_tiles, min(self.max_x_tiles, self.player.x + 8))
        camera.position = lerp(
            camera.position, 
            (safe_x, 15, self.player.z - 8), 
            4 * time.dt
        )
        camera.rotation_x = 60
        camera.rotation_y = -45
    
    def restart_game(self):
        """Setzt das Spiel zurück und startet neu."""
        print("🔄 Starte Spiel neu...")
        self.ui_manager.hide_pause_menu()
        self.ui_manager.is_game_over = False
        self.ui_manager.game_paused = False
        self.ui_manager.reset_score()
        
        # Spieler zurücksetzen
        self.player.position = (0, 0.5, self.start_z_position)
        self.player.rotation_y = 180
        self.player.scale = self.player.base_scale
        self.player.color = color.white
        
        # Welt zurücksetzen
        self.car_manager.cleanup()
        
        for tile in self.world_generator.tiles:
            destroy(tile)
        self.world_generator.tiles.clear()
        
        for tree in self.world_generator.trees:
            destroy(tree)
        self.world_generator.trees.clear()
        
        self.world_generator.lanes.clear()
        self.world_generator.occupied_tile_positions.clear()
        
        # Cooldown zurücksetzen
        self.last_move_time = 0
        
        # Neue Welt erstellen
        self.create_initial_world()
    
    def run(self):
        """Startet die Hauptspielschleife."""
        self.app.run()