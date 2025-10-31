from ursina import *
import random
import time

class CarManager:
    """
    Verwaltet das Spawnen, Bewegen und Entfernen von Autos.
    """
    
    def __init__(self, settings, car_settings):
        self.settings = settings
        self.car_settings = car_settings
        self.cars = []
        self.lane_last_spawn = {}
        self.car_lane_speed = {}
        
        self.car_models_small = [
            'assets/models/car.glb',
            'assets/models/car2.glb',
            'assets/models/car3.glb'
        ]
        
        self.min_spawn_distance = 4
        self.level_width = settings["level_width"]
    
    def spawn_car(self, lane_index, lanes):
        """
        Spawnt ein Auto in der angegebenen Lane, falls Bedingungen erfüllt sind.
        
        Args:
            lane_index (int): Index der Lane
            lanes (list): Liste aller Lanes
        """
        lane = next(
            (lane for lane in lanes 
             if lane['index'] == lane_index and lane['type'] == 'road'), 
            None
        )
        if not lane:
            return
        
        current_time = time.time()
        last_spawn = self.lane_last_spawn.get(('car', lane_index), 0)
        default_lane_speed = 3.0
        lane_speed = self.car_lane_speed.get(lane_index, default_lane_speed)
        
        if current_time - last_spawn < (self.min_spawn_distance / lane_speed):
            return
        
        lane_z_position = lane['z']
        direction = lane['direction']
        
        if lane_index not in self.car_lane_speed:
            self.car_lane_speed[lane_index] = random.uniform(
                self.settings["min_car_speed"], 
                self.settings["max_car_speed"]
            )
        lane_speed = self.car_lane_speed[lane_index]
        
        spawn_offset = self.level_width * 1.5
        start_x = -spawn_offset if direction == 1 else spawn_offset
        
        min_car_distance = lane_speed * 2.5
        
        # Prüfe Abstand zu anderen Autos in derselben Lane
        for other_car in self.cars:
            if abs(other_car.z - lane_z_position) < 0.2:
                if abs(other_car.x - start_x) < min_car_distance:
                    return
        
        # Wähle zufälliges Auto-Modell
        model_path = random.choice(self.car_models_small)
        model_name = model_path.split('/')[-1]
        car_config = self.car_settings.get(
            model_name, 
            {"scale": [1.5, 1.5, 1.5], "collider_scale": [1, 1, 1]}
        )
        
        car = Entity(
            model=model_path,
            position=(start_x, 0.9, lane_z_position),
            scale=tuple(car_config["scale"]),
            rotation=(0, -90, 0) if direction == 1 else (0, 90, 0),
            collider='box'
        )
        
        car.y -= car.scale_y * 0.25
        car.direction = direction
        car.speed = lane_speed
        self.cars.append(car)
        self.lane_last_spawn[('car', lane_index)] = current_time
    
    def update_cars(self):
        """Bewegt alle Autos und entfernt solche, die außerhalb des Bereichs sind."""
        for car in self.cars[:]:
            car.x += car.direction * car.speed * time.dt
            if abs(car.x) > self.level_width * 3:
                destroy(car)
                self.cars.remove(car)
    
    def check_collision_with_player(self, player):
        """
        Prüft Kollisionen zwischen Autos und dem Spieler.
        
        Args:
            player (Entity): Der Spieler
            
        Returns:
            bool: True bei Kollision, sonst False
        """
        for car in self.cars:
            if player.intersects(car).hit:
                return True
        return False
    
    def cleanup(self):
        """Entfernt alle Autos."""
        for car in self.cars:
            destroy(car)
        self.cars.clear()
        self.lane_last_spawn.clear()
        self.car_lane_speed.clear()