import json
import os

class HighscoreManager:
    """
    Verwaltet das Laden und Speichern des Highscores.
    """
    
    def __init__(self, filename="assets/highscore.json"):
        self.highscore_file = filename
        self.current_highscore = self.load_highscore()
    
    def load_highscore(self):
        """
        Lädt den Highscore aus der JSON-Datei.
        
        Returns:
            float: Der aktuelle Highscore, 0 falls nicht vorhanden
        """
        if os.path.exists(self.highscore_file):
            try:
                with open(self.highscore_file, "r") as file:
                    data = json.load(file)
                    return data.get("highscore", 0)
            except Exception:
                return 0
        return 0
    
    def save_highscore(self, value):
        """
        Speichert einen neuen Highscore.
        
        Args:
            value (float): Der neue Highscore-Wert
        """
        with open(self.highscore_file, "w") as file:
            json.dump({"highscore": value}, file)
    
    def update_highscore(self, new_score):
        """
        Aktualisiert den Highscore, falls der neue Score höher ist.
        
        Args:
            new_score (float): Der neue Score
            
        Returns:
            bool: True falls Highscore aktualisiert wurde, sonst False
        """
        if new_score > self.current_highscore:
            self.current_highscore = new_score
            self.save_highscore(new_score)
            return True
        return False