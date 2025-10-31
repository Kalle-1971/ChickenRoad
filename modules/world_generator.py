from ursina import *
import random
import math

class WorldGenerator:
    """
    Generiert und verwaltet die Spielwelt inklusive Straßen, Gras und Bäumen.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.lanes = []
        self.tiles = []
        self.trees = []
        self.occupied_tile_positions = set()
        
        # Model-Pfade und Skalierungen
        self.road_model_path = 'assets/models/simple_road.glb'
        self.road_model_scale = 0.25
        self.grass_model_path = 'assets/models/grass.glb'
        self.grass_model_scale = 6.0
        
        # Level-Breite aus Settings
        self.level_width = settings["level_width"]
        
        # Tile-Dimensionen (werden später initialisiert)
        self.road_tile_width = None
        self.road_tile_length = None
        self.grass_tile_width = None
        self.grass_tile_length = None
    
    def initialize_model_bounds(self):
        """Initialisiert die Modell-Abmessungen, wenn sie benötigt werden."""
        if self.road_tile_width is not None:
            return  # Bereits initialisiert
            
        print("📐 Initialisiere Modell-Abmessungen...")
        try:
            self.road_tile_width, self.road_tile_length = self.get_model_bounds(
                self.road_model_path, self.road_model_scale
            )
            self.grass_tile_width, self.grass_tile_length = self.get_model_bounds(
                self.grass_model_path, self.grass_model_scale
            )
            print(f"✅ Modell-Abmessungen initialisiert: Road={self.road_tile_length}, Grass={self.grass_tile_length}")
        except Exception as e:
            print(f"⚠️ Fehler beim Initialisieren der Modell-Abmessungen: {e}")
            # Fallback-Werte
            self.road_tile_width, self.road_tile_length = 1.0, 1.0
            self.grass_tile_width, self.grass_tile_length = 1.0, 1.0
    
    def get_model_bounds(self, model_path, scale):
        """
        Ermittelt die Abmessungen eines Modells.
        
        Args:
            model_path (str): Pfad zum Modell
            scale (float): Skalierungsfaktor
            
        Returns:
            tuple: (width, length) des Modells
        """
        try:
            temp_entity = Entity(model=model_path, scale=scale)
            bounds = temp_entity.bounds
            destroy(temp_entity)
            return bounds.size.x, bounds.size.z
        except Exception as e:
            print(f"⚠️ Konnte Modell-Bounds nicht ermitteln: {e}")
            return 1.0, 1.0  # Fallback-Werte
    
    def tile_key(self, x, z, precision=3):
        """
        Erzeugt einen eindeutigen Schlüssel für eine Tile-Position.
        
        Args:
            x (float): X-Koordinate
            z (float): Z-Koordinate
            precision (int): Rundungsgenauigkeit
            
        Returns:
            tuple: Gerundete Koordinaten als Schlüssel
        """
        return (round(x, precision), round(z, precision))
    
    def create_play_area_border(self):
        """
        Erstellt einen dunklen Rand um das Spielfeld.
        
        Returns:
            tuple: (border_entity, play_area_entity)
        """
        border_size = 50
        border = Entity(
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(border_size, border_size),
            position=(0, -0.5, 0),
            rotation=(90, 0, 0),
            eternal=True
        )
        
        play_area = Entity(
            model='quad',
            color=color.rgba(100, 100, 100, 0.3),
            scale=(self.level_width + 2, 100),
            position=(0, -0.4, 50),
            rotation=(90, 0, 0),
            eternal=True
        )
        
        return border, play_area
    
    def create_crossy_tree(self, x, z):
        """
        Erstellt einen Crossy-Road-Style Baum.
        
        Args:
            x (float): X-Position
            z (float): Z-Position
            
        Returns:
            Entity: Der erstellte Baum
        """
        tree = Entity(position=(x, 0, z))
        
        # Stamm
        trunk = Entity(
            model='cube',
            parent=tree,
            color=color.brown,
            scale=(0.3, 1.2, 0.3),
            position=(0, 0.6, 0),
            collider='box',
            texture='white_cube'
        )
        
        # Baumkrone (mehrere Ebenen)
        foliage_bottom = Entity(
            model='cube', 
            parent=tree,
            color=color.green,
            scale=(1.2, 0.8, 1.2),
            position=(0, 1.6, 0),
            texture='white_cube'
        )
        
        foliage_middle = Entity(
            model='cube',
            parent=tree,
            color=color.lime,
            scale=(0.9, 0.7, 0.9),
            position=(0, 2.2, 0),
            texture='white_cube'
        )
        
        foliage_top = Entity(
            model='cube',
            parent=tree,
            color=color.olive,
            scale=(0.6, 0.6, 0.6),
            position=(0, 2.7, 0),
            texture='white_cube'
        )
        
        # Collider für den gesamten Baum
        tree.collider = 'box'
        tree.collider.size = (1.0, 2.8, 1.0)
        
        return tree
    
    def create_lane(self, index):
        """
        Erstellt eine neue Lane (Straße oder Gras) an der gegebenen Position.
        
        Args:
            index (int): Index der Lane
        """
        # Stelle sicher, dass Model-Bounds initialisiert sind
        if self.road_tile_length is None:
            self.initialize_model_bounds()
            
        z_position = index * self.road_tile_length
        if math.isnan(z_position) or math.isinf(z_position):
            print(f"⚠️ Ungültige Z-Position für Lane {index}")
            return
        
        # Bestimme Lane-Typ und Richtung
        lane_type = random.choice(['road', 'grass'])
        direction = random.choice([-1, 1]) if lane_type == 'road' else 0
        
        self.lanes.append({
            'index': index, 
            'z': z_position, 
            'type': lane_type, 
            'direction': direction
        })
        
        # Unsichtbare Lane-Entity für Kollisionserkennung
        collider_type = 'box' if lane_type in ('road', 'grass') else None
        lane_entity = Entity(
            position=(0, 0, z_position),
            model='cube',
            scale=(self.level_width, 1, 1),
            collider=collider_type,
            color=color.clear,
            enabled=True
        )
        
        # Erstelle die sichtbaren Tiles
        self.create_lane_tiles(lane_type, z_position)
        
        # Füge Bäume hinzu, falls es eine Gras-Lane ist
        if lane_type == 'grass':
            self.spawn_trees_in_lane(z_position)
        
        print(f"✅ Lane {index} erstellt ({lane_type}) bei Z={z_position}")
    
    def create_lane_tiles(self, lane_type, z_position):
        """
        Erstellt die sichtbaren Tiles für eine Lane.
        
        Args:
            lane_type (str): Typ der Lane ('road' oder 'grass')
            z_position (float): Z-Position der Lane
        """
        extra_left, extra_right = 10, 8
        epsilon = 0.0005
        
        if lane_type == 'road':
            model_path = self.road_model_path
            model_scale = self.road_model_scale
            tile_width = self.road_tile_width
            y_position = 0.0
        else:  # grass
            model_path = self.grass_model_path
            model_scale = self.grass_model_scale
            tile_width = self.grass_tile_width
            y_position = -0.24
        
        # Korrekte Berechnung der Segment-Anzahl
        num_segments = math.ceil(
            self.level_width / tile_width
        ) + extra_left + extra_right
        total_width = num_segments * tile_width
        offset_start = -total_width / 2 + tile_width / 2
        
        tiles_created = 0
        for segment_index in range(num_segments):
            x_position = offset_start + segment_index * tile_width + segment_index * epsilon
            current_tile_key = self.tile_key(x_position, z_position)
            
            if current_tile_key in self.occupied_tile_positions:
                continue
            
            try:
                tile_entity = Entity(
                    model=model_path,
                    position=(x_position, y_position, z_position),
                    rotation=(0, 90, 0),
                    scale=(model_scale,) * 3,
                    double_sided=True,
                    collider='box'
                )
                
                self.tiles.append(tile_entity)
                self.occupied_tile_positions.add(current_tile_key)
                tiles_created += 1
            except Exception as e:
                print(f"⚠️ Konnte Tile nicht erstellen: {e}")
                # Fallback: Einfache Box
                tile_color = color.gray if lane_type == 'road' else color.green
                tile_entity = Entity(
                    model='cube',
                    position=(x_position, y_position, z_position),
                    scale=(tile_width, 0.1, self.road_tile_length),
                    color=tile_color,
                    collider='box'
                )
                self.tiles.append(tile_entity)
                self.occupied_tile_positions.add(current_tile_key)
                tiles_created += 1
        
        print(f"   {tiles_created} Tiles für {lane_type}-Lane bei Z={z_position} erstellt")
    
    def spawn_trees_in_lane(self, z_position):
        """
        Platziert Bäume in einer Gras-Lane.
        
        Args:
            z_position (float): Z-Position der Lane
        """
        if random.random() < self.settings["tree_spawn_chance"]:
            num_trees = random.randint(
                self.settings["min_trees_per_lane"], 
                self.settings["max_trees_per_lane"]
            )
            
            trees_spawned = 0
            attempts = 0
            max_attempts = 40
            
            spawn_area_width = self.level_width * 2
            min_tree_x = -spawn_area_width / 2
            max_tree_x = spawn_area_width / 2
            
            tree_positions_in_lane = []
            
            while trees_spawned < num_trees and attempts < max_attempts:
                attempts += 1
                tree_x = random.uniform(min_tree_x, max_tree_x)
                
                tree_pos_key = self.tile_key(tree_x, z_position)
                if tree_pos_key in self.occupied_tile_positions:
                    continue
                
                min_distance = self.settings["tree_spawn_distance"]
                too_close = any(
                    abs(existing_x - tree_x) < min_distance 
                    for existing_x in tree_positions_in_lane
                )
                
                if too_close:
                    continue
                
                try:
                    tree = self.create_crossy_tree(tree_x, z_position)
                    self.trees.append(tree)
                    trees_spawned += 1
                    tree_positions_in_lane.append(tree_x)
                    self.occupied_tile_positions.add(tree_pos_key)
                except Exception as e:
                    print(f"⚠️ Konnte Baum nicht erstellen: {e}")
            
            if trees_spawned > 0:
                print(f"   {trees_spawned} Bäume für Gras-Lane bei Z={z_position} erstellt")
    
    def create_backward_lanes(self, count=5):
        """
        Erstellt initiale Lanes hinter dem Startpunkt.
        
        Args:
            count (int): Anzahl der rückwärtigen Lanes
        """
        # Stelle sicher, dass Model-Bounds initialisiert sind
        if self.road_tile_length is None or self.grass_tile_width is None:
            self.initialize_model_bounds()
            
        epsilon = 0.002
        for i in range(1, count + 1):
            z_index = -i
            z_position = z_index * self.road_tile_length
            
            self.lanes.append({
                'index': z_index, 
                'z': z_position, 
                'type': 'grass', 
                'direction': 0
            })
            
            num_segments = math.ceil(
                self.level_width / self.grass_tile_width
            ) + 6
            offset_start = -num_segments * self.grass_tile_width / 2 + self.grass_tile_width / 2
            
            tiles_created = 0
            for segment_index in range(num_segments):
                x_position = offset_start + segment_index * self.grass_tile_width + segment_index * epsilon
                current_tile_key = self.tile_key(x_position, z_position)
                
                if current_tile_key in self.occupied_tile_positions:
                    continue
                
                try:
                    grass_tile = Entity(
                        model=self.grass_model_path,
                        position=(x_position, -0.24, z_position),
                        rotation=(0, 90, 0),
                        scale=(self.grass_model_scale,) * 3,
                        double_sided=True,
                        collider='box'
                    )
                    
                    self.tiles.append(grass_tile)
                    self.occupied_tile_positions.add(current_tile_key)
                    tiles_created += 1
                except Exception as e:
                    print(f"⚠️ Konnte Gras-Tile nicht erstellen: {e}")
                    # Fallback
                    grass_tile = Entity(
                        model='cube',
                        position=(x_position, -0.24, z_position),
                        scale=(self.grass_tile_width, 0.1, self.road_tile_length),
                        color=color.green,
                        collider='box'
                    )
                    self.tiles.append(grass_tile)
                    self.occupied_tile_positions.add(current_tile_key)
                    tiles_created += 1
            
            print(f"✅ Rückwärts-Lane {z_index} erstellt mit {tiles_created} Tiles")
    
    def extend_level(self, count=5):
        """
        Erweitert das Level um weitere Lanes.
        
        Args:
            count (int): Anzahl der neuen Lanes
        """
        if not self.lanes:
            max_index = 0
        else:
            max_index = max([lane['index'] for lane in self.lanes])
        
        print(f"🌍 Erweitere Level von {max_index} bis {max_index + count}")
        
        for i in range(1, count + 1):
            self.create_lane(max_index + i)
    
    def cleanup_old_objects(self, player_z_position):
        """
        Entfernt alte Tiles, Lanes und Bäume, die zu weit hinter dem Spieler sind.
        
        Args:
            player_z_position (float): Aktuelle Z-Position des Spielers
        """
        cleanup_distance = self.settings["cleanup_distance"]
        removed_tiles = 0
        removed_lanes = 0
        removed_trees = 0
        
        # Tiles aufräumen
        for tile in self.tiles[:]:
            if tile.z < player_z_position - cleanup_distance:
                tile_key = self.tile_key(tile.x, tile.z)
                self.occupied_tile_positions.discard(tile_key)
                destroy(tile)
                self.tiles.remove(tile)
                removed_tiles += 1
        
        # Lanes aufräumen
        for lane in self.lanes[:]:
            if lane['z'] < player_z_position - cleanup_distance:
                self.lanes.remove(lane)
                removed_lanes += 1
        
        # Bäume aufräumen
        for tree in self.trees[:]:
            if tree.z < player_z_position - cleanup_distance:
                tree_key = self.tile_key(tree.x, tree.z)
                self.occupied_tile_positions.discard(tree_key)
                destroy(tree)
                self.trees.remove(tree)
                removed_trees += 1
        
        if removed_tiles > 0 or removed_lanes > 0 or removed_trees > 0:
            print(f"🧹 Aufgeräumt: {removed_tiles} Tiles, {removed_lanes} Lanes, {removed_trees} Bäume")