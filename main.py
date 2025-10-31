"""
Korrigierte Hauptdatei - Sicherstellung der korrekten Initialisierungsreihenfolge
"""
import ursina
from ursina import *

# ZUERST Ursina initialisieren, BEVOR irgendwelche Entities erstellt werden
app = Ursina()

# DANACH die Module importieren und Entities erstellen
from modules.game_settings import GameSettings
from modules.highscore_manager import HighscoreManager
from modules.world_generator import WorldGenerator
from modules.car_manager import CarManager
from modules.ui_manager import UIManager
from modules.player import Player

# Initialisiere Manager (keine Entities)
settings_manager = GameSettings()
highscore_manager = HighscoreManager()

# Einstellungen aus JSON
tile_size = settings_manager.game_settings["tile_size"]
level_width = settings_manager.game_settings["level_width"]
max_x_tiles = level_width // 2
start_z = 0
min_car_speed = settings_manager.game_settings["min_car_speed"]
max_car_speed = settings_manager.game_settings["max_car_speed"]
car_spawn_chance = settings_manager.game_settings["car_spawn_chance"]
game_paused = False
is_game_over = False
move_cooldown = settings_manager.game_settings["move_cooldown"]
last_move_time = 0

# Fenster konfigurieren
window.fullscreen = False
window.borderless = settings_manager.display_settings.get("window_borderless", False)
window.title = 'Crossy Road Clone'
window.exit_button.visible = False

# Beleuchtung
DirectionalLight(shadows=False, rotation=(45, -45, 45))
AmbientLight(color=color.rgb(200, 200, 200))

# Kamera
camera.position = (8, 14, -13)
camera.rotation_x = 55
camera.rotation_y = -45
camera.fov = settings_manager.display_settings.get("camera_fov", 80)

mouse.visible = False
mouse.enabled = False

# JETZT erst die Spielkomponenten initialisieren (nach Ursina)
world_generator = WorldGenerator(settings_manager.game_settings)
car_manager = CarManager(settings_manager.game_settings, settings_manager.car_settings)
ui_manager = UIManager(highscore_manager)
player = Player(start_position=(0, 1.0, start_z))

# Highscore-UI Variablen
current_score = 0
highscore = highscore_manager.current_highscore
score_text = None  # Startet als None, wird erst erstellt wenn needed
highscore_text = Text(
    text=f"Highscore: {highscore:.1f} m", 
    position=(-0.85, 0.4), 
    scale=1.2, 
    color=color.azure,
    background=False
)

# Funktion zum Erstellen des Score-Texts
def create_score_text():
    global score_text
    if score_text is None:
        score_text = Text(
            text=f"{current_score:.1f} m", 
            position=(-0.85, 0.45), 
            scale=1.5, 
            color=color.white,
            background=False
        )

# Spielbereich-Grenzen
world_generator.create_play_area_border()

# Pause Menü
pause_overlay = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 80), scale=(1.6, 1.0), z=1, enabled=False)
pause_menu = Entity(parent=camera.ui, enabled=False)

pause_title = Text("GAME OVER", parent=pause_menu, y=0.2, origin=(0, 0), scale=2, color=color.rgb(255, 80, 80))
restart_txt = Text("Restart", parent=pause_menu, y=-0.05, scale=1.4, color=color.white, origin=(0, 0))
quit_txt = Text("Quit", parent=pause_menu, y=-0.25, scale=1.4, color=color.white, origin=(0, 0))

pause_buttons = [restart_txt, quit_txt]
selected_index = 0

def update_button_highlight():
    for i, txt in enumerate(pause_buttons):
        if i == selected_index:
            txt.color = color.rgb(255, 80, 80)
            txt.scale = 2.5
        else:
            txt.color = color.white
            txt.scale = 1.4

def show_pause(game_over=False):
    global game_paused, selected_index, is_game_over
    game_paused = True
    is_game_over = game_over
    
    if game_over:
        pause_title.text = "GAME OVER"
        pause_title.color = color.rgb(255, 80, 80)
    else:
        pause_title.text = "PAUSED"
        pause_title.color = color.rgb(100, 150, 255)
    
    pause_overlay.enabled = True
    pause_menu.enabled = True
    selected_index = 0
    update_button_highlight()

def hide_pause():
    global game_paused, is_game_over
    if is_game_over:
        return
    game_paused = False
    pause_menu.enabled = False
    pause_overlay.enabled = False

def restart_game():
    global is_game_over, game_paused, current_score, highscore
    
    pause_overlay.enabled = False
    pause_menu.enabled = False
    is_game_over = False
    game_paused = False

    # Score reset
    current_score = 0
    highscore = highscore_manager.current_highscore
    
    # Score-Text entfernen und auf None setzen
    if score_text is not None:
        destroy(score_text)
        score_text = None
    
    # Highscore-Text aktualisieren
    highscore_text.text = f"Highscore: {highscore:.1f} m"

    # Player reset
    player.position = (0, 0.5, start_z)
    player.rotation_y = 180
    player.scale = player.base_scale
    player.color = color.white

    # Aufräumen
    car_manager.cleanup()
    
    # Welt zurücksetzen
    for tile in world_generator.tiles:
        destroy(tile)
    world_generator.tiles.clear()
    
    for tree in world_generator.trees:
        destroy(tree)
    world_generator.trees.clear()
    
    world_generator.lanes.clear()
    world_generator.occupied_tile_positions.clear()

    # Neue Welt erstellen
    world_generator.create_backward_lanes(5)
    for i in range(15):
        world_generator.create_lane(start_z + i)
    world_generator.extend_level(5)

# Input-Funktion
def input(key):
    global selected_index, last_move_time

    if game_paused:
        if key == 'up arrow':
            selected_index = (selected_index - 1) % len(pause_buttons)
            update_button_highlight()
        elif key == 'down arrow':
            selected_index = (selected_index + 1) % len(pause_buttons)
            update_button_highlight()
        elif key in ('enter', 'return'):
            if selected_index == 0:
                restart_game()
            elif selected_index == 1:
                application.quit()
        elif key == 'escape':
            hide_pause()
        return

    if game_paused or is_game_over:
        return

    if time.time() - last_move_time < move_cooldown:
        return

    if key == 'escape':
        show_pause()
        return

    moved = False
    old_position = player.position
    
    if key == 'w':
        player.z += tile_size
        player.face_direction(0)
        player.hop()
        world_generator.extend_level(1)
        moved = True
    elif key == 's' and player.z - tile_size >= start_z:
        player.z -= tile_size
        player.face_direction(180)
        player.hop()
        moved = True
    elif key == 'a' and player.x - tile_size >= -max_x_tiles:
        player.x -= tile_size
        player.face_direction(-90)
        player.hop()
        moved = True
    elif key == 'd' and player.x + tile_size <= max_x_tiles:
        player.x += tile_size
        player.face_direction(90)
        player.hop()
        moved = True

    if moved:
        # Kollisionsprüfung mit Bäumen
        collision_occurred = False
        for tree in world_generator.trees:
            if abs(tree.x) <= max_x_tiles + 0.5:
                if distance(player.position, tree.position) < 1.5:
                    if player.intersects(tree).hit:
                        collision_occurred = True
                        break
        
        if collision_occurred:
            player.position = old_position
            player.color = color.red
            invoke(setattr, player, 'color', color.white, delay=0.2)
        else:
            last_move_time = time.time()

# Update-Funktion
def update():
    global current_score, highscore

    world_generator.cleanup_old_objects(player.z)

    if not game_paused:
        safe_x = max(-max_x_tiles, min(max_x_tiles, player.x + 8))
        camera.position = lerp(camera.position, (safe_x, 15, player.z - 8), 4 * time.dt)
        camera.rotation_x = 60
        camera.rotation_y = -45

    # Score-Logik
    distance_traveled = player.z - start_z
    
    # Erstelle Score-Text erst wenn der Spieler sich bewegt hat (Score > 0)
    if distance_traveled > 0:
        current_score = distance_traveled
        
        # Text erstellen falls noch nicht existiert
        if score_text is None:
            create_score_text()
        else:
            # Text aktualisieren falls bereits existiert
            score_text.text = f"{current_score:.1f} m"
        
        # Highscore prüfen und aktualisieren
        if current_score > highscore:
            highscore = current_score
            highscore_text.text = f"Highscore: {highscore:.1f} m"
            highscore_manager.save_highscore(highscore)

    # Autos bewegen
    car_manager.update_cars()

    # Auto-Spawning
    if random.random() < car_spawn_chance:
        road_lane_indices = [l['index'] for l in world_generator.lanes if l['type'] == 'road']
        if road_lane_indices:
            car_manager.spawn_car(random.choice(road_lane_indices), world_generator.lanes)

    # Auto-Kollision
    if car_manager.check_collision_with_player(player):
        player.color = color.black
        show_pause(game_over=True)
        
# Start - WICHTIG: Model-Bounds initialisieren BEVOR create_backward_lanes aufgerufen wird
world_generator.initialize_model_bounds()
world_generator.create_backward_lanes(5)
for i in range(15):
    world_generator.create_lane(start_z + i)
world_generator.extend_level(5)

print("✅ Spiel gestartet - Bewegung mit W,A,S,D möglich")

app.run()