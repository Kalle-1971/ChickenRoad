from ursina import *

class UIManager:
    """
    Verwaltet die Benutzeroberfläche inklusive Pause-Menü und Score-Anzeige.
    """
    
    def __init__(self, highscore_manager):
        self.highscore_manager = highscore_manager
        self.current_score = 0
        self.game_paused = False
        self.is_game_over = False
        self.selected_pause_index = 0
        
        self.setup_ui_elements()
        self.setup_pause_menu()
    
    def setup_ui_elements(self):
        """Initialisiert die UI-Elemente für Score und Highscore."""
        self.score_text = None
        
        self.highscore_text = None
    
    def setup_pause_menu(self):
        """Initialisiert das Pause-Menü."""
        self.pause_overlay = Entity(
            parent=camera.ui, 
            model='quad', 
            color=color.rgba(0, 0, 0, 80), 
            scale=(1.6, 1.0), 
            z=1, 
            enabled=False
        )
        
        self.pause_menu = Entity(parent=camera.ui, enabled=False)
        
        self.pause_title = Text(
            "GAME OVER", 
            parent=self.pause_menu, 
            y=0.2, 
            origin=(0, 0), 
            scale=2, 
            color=color.rgb(255, 80, 80)
        )
        
        self.restart_text = Text(
            "Restart", 
            parent=self.pause_menu, 
            y=-0.05, 
            scale=1.4, 
            color=color.white, 
            origin=(0, 0)
        )
        
        self.quit_text = Text(
            "Quit", 
            parent=self.pause_menu, 
            y=-0.25, 
            scale=1.4, 
            color=color.white, 
            origin=(0, 0)
        )
        
        self.pause_buttons = [self.restart_text, self.quit_text]
        self.update_button_highlight()
    
    def update_button_highlight(self):
        """Aktualisiert die Hervorhebung der Pause-Menü-Buttons."""
        for index, text_element in enumerate(self.pause_buttons):
            if index == self.selected_pause_index:
                text_element.color = color.rgb(255, 80, 80)
                text_element.scale = 2.5
            else:
                text_element.color = color.white
                text_element.scale = 1.4
    
    def show_pause_menu(self, game_over=False):
        """
        Zeigt das Pause-Menü an.
        
        Args:
            game_over (bool): True falls Game Over, sonst Pause
        """
        self.game_paused = True
        self.is_game_over = game_over
        
        if game_over:
            self.pause_title.text = "GAME OVER"
            self.pause_title.color = color.rgb(255, 80, 80)
        else:
            self.pause_title.text = "PAUSED"
            self.pause_title.color = color.rgb(100, 150, 255)
        
        self.pause_overlay.enabled = True
        self.pause_menu.enabled = True
        self.selected_pause_index = 0
        self.update_button_highlight()
    
    def hide_pause_menu(self):
        """Versteckt das Pause-Menü."""
        if self.is_game_over:
            return
        self.game_paused = False
        self.pause_menu.enabled = False
        self.pause_overlay.enabled = False
    
    def handle_pause_input(self, key):
        """
        Verarbeitet Eingaben im Pause-Menü.
        
        Args:
            key (str): Die gedrückte Taste
            
        Returns:
            tuple: (should_restart, should_quit)
        """
        if key == 'up arrow':
            self.selected_pause_index = (self.selected_pause_index - 1) % len(self.pause_buttons)
            self.update_button_highlight()
        elif key == 'down arrow':
            self.selected_pause_index = (self.selected_pause_index + 1) % len(self.pause_buttons)
            self.update_button_highlight()
        elif key in ('enter', 'return'):
            if self.selected_pause_index == 0:
                return True, False  # Restart
            elif self.selected_pause_index == 1:
                return False, True  # Quit
        elif key == 'escape' and not self.is_game_over:
            self.hide_pause_menu()
        
        return False, False
    
    def update_score(self, player_z, start_z):
        """
        Aktualisiert die Score-Anzeige.
        
        Args:
            player_z (float): Aktuelle Z-Position des Spielers
            start_z (float): Start-Z-Position
            
        Returns:
            bool: True falls Highscore gebrochen wurde
        """
        distance_traveled = player_z - start_z
        if distance_traveled > self.current_score:
            self.current_score = distance_traveled
            self.score_text.text = f"{self.current_score:.1f} m"
            
            highscore_updated = self.highscore_manager.update_highscore(self.current_score)
            if highscore_updated:
                self.highscore_text.text = f"Highscore: {self.highscore_manager.current_highscore:.1f} m"
                return True
        
        return False
    
    def reset_score(self):
        """Setzt den aktuellen Score zurück."""
        self.current_score = 0
        self.score_text.text = f"{self.current_score:.1f} m"
        # Highscore-Text aktualisieren
        self.highscore_text.text = f"Highscore: {self.highscore_manager.current_highscore:.1f} m"