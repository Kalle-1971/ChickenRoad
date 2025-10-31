<div align="center">
  <h1>🐔 ChickenRoad - Crossy Road Clone</h1>
  
  <p>Ein unterhaltsames 3D-Spiel inspiriert von Crossy Road, entwickelt mit Python und Ursina Engine</p>

  <img alt="Github top language" src="https://img.shields.io/github/languages/top/Kalle-1971/chickenroad?color=56BEB8">
  <img alt="Github language count" src="https://img.shields.io/github/languages/count/Kalle-1971/chickenroad?color=56BEB8">
  <img alt="Repository size" src="https://img.shields.io/github/repo-size/Kalle-1971/chickenroad?color=56BEB8">
  <img alt="License" src="https://img.shields.io/github/license/Kalle-1971/chickenroad?color=56BEB8">
  <img alt="Python Version" src="https://img.shields.io/badge/python-3.13.0-blue">
  <img alt="Ursina Version" src="https://img.shields.io/badge/ursina-8.1.1-orange">
</div>

<br>

## 🎮 Über das Spiel

ChickenRoad ist ein unterhaltsames 3D-Spiel, bei dem du ein Huhn durch eine gefährliche Welt voller Autos und Hindernisse steuerst. Das Spiel ist inspiriert vom beliebten Mobile Game "Crossy Road" und bietet eine moderne, objektorientierte Implementierung mit Python.

**Ziel des Spiels**: Überquere so viele Straßen wie möglich, ohne von Autos erwischt zu werden, und sammle dabei Punkte!

## ✨ Features

### 🎯 Spielmechaniken
- **Bewegung**: Steuere dein Huhn mit W, A, S, D durch die Welt
- **Springmechanik**: Realistisches Hüpfen bei jeder Bewegung
- **Kollisionserkennung**: Kollisionen mit Autos und Bäumen
- **Dynamische Kamera**: Kamera folgt dem Spieler automatisch

### 🌍 Spielwelt
- **Prozedurale Generierung**: Unendlich generierte Levels
- **Verschiedene Lane-Typen**: Straßen mit Autos und Grasflächen mit Bäumen
- **Realistische Assets**: 3D-Modelle für Straßen, Gras, Autos und Bäume
- **Optimierte Performance**: Automatisches Cleanup von nicht sichtbaren Objekten

### 🚗 Fahrzeuge & Hindernisse
- **Verschiedene Auto-Modelle**: Mehrere Auto-Typen mit individuellen Einstellungen
- **Intelligentes Spawning**: Autos spawnen mit angemessenen Abständen
- **Baum-Hindernisse**: Bäume blockieren den Weg auf Grasflächen
- **Geschwindigkeitsvariation**: Autos haben unterschiedliche Geschwindigkeiten

### ⚙️ System & Einstellungen
- **Konfigurierbare Einstellungen**: Alle Spielparameter in JSON-Dateien
- **Highscore-System**: Persistenter Local Highscore
- **Pause-Menü**: Voll funktionsfähiges Pause- und Game-Over-Menü
- **Responsive UI**: Dynamische Score-Anzeige und Highscore-Tracking

### 🎨 Technische Features
- **Modulare Architektur**: Sauber strukturierter, objektorientierter Code
- **Erweiterbares System**: Einfache Erweiterung um neue Features
- **Fehlerbehandlung**: Robuste Fehlerbehandlung für verschiedene Szenarien
- **Detaillierte Logs**: Umfangreiche Debug-Ausgaben zur Fehlersuche

## 🛠️ Technologien

Das Spiel wurde mit folgenden Technologien entwickelt:

- **Python 3.13.0** - Programmiersprache
- **Ursina Engine 8.1.1** - 3D-Spiel-Engine
- **JSON** - Konfigurationsdateien
- **Panda3D** - Unterliegende Game Engine (von Ursina verwendet)

## 📋 Voraussetzungen

Bevor du beginnst, stelle sicher, dass du folgendes installiert hast:

- **Python 3.13.0** oder höher
- **pip** (Python Package Manager)

### Unterstützte Betriebssysteme
- ✅ Windows 10/11
- ✅ macOS (getestet mit neueren Versionen)
- ✅ Linux (Ubuntu, Fedora, etc.)

## 🚀 Installation & Start

### 1. Projekt klonen
```bash
# Klone das Repository
git clone https://github.com/Kalle-1971/chickenroad.git

# Wechsle in das Projektverzeichnis
cd chickenroad

# Checke deine Python Version (mind 3.13)
python --version

# installiere Ursina
python pip install ursina==8.1.1

# Spiel Starten
python main.py
