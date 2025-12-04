# Wilderness Survival System (WSS)

### CS3560 – Object-Oriented Design and Programming Project  

**Team 9:**  
Sarah Huynh, Joseline Ly, Sam Klapper, Carlos Vargas, Danny Caceres, Cheyenne Chavis  

---

## 📖 Overview
**Wilderness Survival System (WSS)** is a turn-based survival game built with **Python Arcade**.  
The player must cross a randomly generated wilderness map — moving from west to east — while managing **food, water, strength, and gold**.  
Along the way, they’ll encounter different terrains, collect items, and trade with unpredictable traders.

---

## 🤸‍♀️ Running The Game
First install python arcade using `pip install arcade`.
Then just run `python game.py`.
*Mac users will have to allow their IDE to access their keystrokes.*

---

## 🧱 Project Structure
```
WSS/
├── game.py    #Main Arcade view and game loop  
├── ai/        #Vision and Brain logic for player decision-making  
├── actors/    #Player and Trader classes  
├── world/     #Map, Terrain, and generation logic  
├── items/     #Item and bonus definitions  
├── systems/   #Turn, trading, and gameplay systems  
├── assets/    #Sprites, textures, and sounds
```
