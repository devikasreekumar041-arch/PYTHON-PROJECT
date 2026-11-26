"""
LEGENDS OF THE FORGOTTEN REALM
A command-line, turn-based RPG project.
Python 3.9+ | No external packages required

Run: python legends_of_the_forgotten_realm.py
Save file: legends_save.json
"""

import json
import os
import random
import time

SAVE_FILE = "legends_save.json"

CLASSES = {
    "Warrior":  {"hp": 150, "mana": 45, "attack": 18, "defense": 12, "crit": 5},
    "Mage":     {"hp": 100, "mana": 120, "attack": 22, "defense": 5, "crit": 10},
    "Archer":   {"hp": 115, "mana": 75, "attack": 17, "defense": 8, "crit": 18},
    "Assassin": {"hp": 90, "mana": 80, "attack": 25, "defense": 4, "crit": 25},
}

RARITY = {
    "Common": (1.0, 0, 50),
    "Uncommon": (1.1, 2, 100),
    "Rare": (1.3, 5, 250),
    "Super Rare": (1.5, 8, 500),
    "Epic": (1.8, 12, 1000),
    "Mythical": (2.2, 18, 2500),
    "Legendary": (2.8, 25, 6000),
}

WEAPONS = [
    ("Wooden Sword", "Common", 5, 1), ("Rusty Axe", "Common", 6, 1),
    ("Training Bow", "Common", 5, 1), ("Iron Dagger", "Common", 6, 1),
    ("Bronze Staff", "Common", 7, 1), ("Iron Sword", "Uncommon", 10, 5),
    ("Steel Axe", "Uncommon", 12, 5), ("Long Bow", "Uncommon", 11, 5),
    ("Knight Spear", "Rare", 17, 10), ("Frost Wand", "Rare", 18, 10),
    ("Crystal Blade", "Super Rare", 25, 20), ("Shadow Dagger", "Super Rare", 27, 20),
    ("Lightning Bow", "Super Rare", 26, 20), ("Flame Sword", "Epic", 36, 30),
    ("Ice Spear", "Epic", 38, 30), ("Thunder Hammer", "Epic", 40, 30),
    ("Phoenix Blade", "Mythical", 52, 40), ("Demon Slayer", "Mythical", 56, 40),
    ("Celestial Staff", "Mythical", 54, 40),
    ("Dragon King's Sword", "Legendary", 75, 50),
    ("Blade of Eternity", "Legendary", 82, 60),
    ("Bow of the Gods", "Legendary", 78, 60),
]

ARMORS = [
    ("Cloth Outfit", "Common", 2, 10, 0, 0, 1),
    ("Leather Vest", "Common", 4, 15, 0, 1, 1),
    ("Apprentice Robe", "Uncommon", 5, 10, 10, 1, 5),
    ("Chainmail", "Uncommon", 8, 25, 0, 2, 5),
    ("Iron Guard", "Rare", 12, 35, 5, 3, 10),
    ("Ranger Set", "Rare", 10, 25, 10, 5, 10),
    ("Crystal Armor", "Super Rare", 17, 45, 20, 7, 20),
    ("Shadow Suit", "Super Rare", 15, 35, 15, 12, 20),
    ("Flame Plate", "Epic", 23, 65, 15, 10, 30),
    ("Frost Guardian", "Epic", 25, 55, 25, 12, 30),
    ("Phoenix Armor", "Mythical", 32, 90, 35, 18, 40),
    ("Demon King's Guard", "Legendary", 45, 130, 50, 25, 50),
]

POTIONS = {
    "Small Health Potion": ("health", 50, 30),
    "Medium Health Potion": ("health", 100, 60),
    "Large Health Potion": ("health", 250, 120),
    "Giant Health Potion": ("health", 500, 250),
    "Ultimate Health Potion": ("health", -1, 500),
    "Small Mana Potion": ("mana", 30, 30),
    "Medium Mana Potion": ("mana", 75, 60),
    "Large Mana Potion": ("mana", 150, 120),
    "Giant Mana Potion": ("mana", 300, 250),
    "Ultimate Mana Potion": ("mana", -1, 500),
    "Healing Elixir": ("mixed", (100, 30), 150),
    "Mystic Elixir": ("mixed", (50, 100), 180),
    "Grand Elixir": ("mixed", (200, 150), 350),
    "Attack Tonic": ("buff_attack", 10, 120),
    "Defense Tonic": ("buff_defense", 10, 120),
    "Critical Tonic": ("buff_crit", 15, 150),
}

ENEMY_NAMES = [
    "Goblin", "Wolf", "Slime", "Zombie", "Skeleton",
    "Orc", "Bandit", "Troll", "Dark Archer", "Giant Spider",
    "Vampire", "Werewolf", "Necromancer", "Ice Golem", "Fire Demon",
    "Sand Raider", "Desert Scorpion", "Mummy", "Stone Guardian", "Lost Knight",
    "Castle Wraith", "Dark Paladin", "Lava Beast", "Ash Dragon", "Frost Wolf",
    "Ice Witch", "Sky Harpy", "Storm Elemental", "Demon Hound", "Void Reaper",
]

BOSSES = {
    10: "Goblin King", 20: "Forest Guardian", 30: "Ancient Golem",
    40: "Vampire Lord", 50: "Dragon Rider", 60: "Demon General",
    70: "Ice Titan", 80: "Shadow Emperor", 90: "Celestial Dragon",
    100: "Ancient Demon King",
}

REGIONS = [
    "Village", "Forest", "Cave", "Desert", "Ruins",
    "Castle", "Volcano", "Frozen Mountain", "Sky Temple", "Demon Realm",
]


def ask_int(prompt, low, high):
    while True:
        try:
            value = int(input(prompt))
            if low <= value <= high:
                return value
            print(f"Enter a number from {low} to {high}.")
        except ValueError:
            print("Please enter a valid number.")


def new_player():
    name = input("Enter player name: ").strip() or "Hero"
    print("\nChoose your class:")
    for i, class_name in enumerate(CLASSES, 1):
        print(f"{i}. {class_name}")
    choice = ask_int("Class: ", 1, len(CLASSES))
    class_name = list(CLASSES)[choice - 1]
    base = CLASSES[class_name]
    player = {
        "name": name, "class": class_name, "level": 1, "exp": 0,
        "hp": base["hp"], "max_hp": base["hp"],
        "mana": base["mana"], "max_mana": base["mana"],
        "attack": base["attack"], "defense": base["defense"],
        "crit": base["crit"], "gold": 100, "weapon": None, "armor": None,
        "potions": {"Small Health Potion": 3, "Small Mana Potion": 2},
        "inventory": [], "bosses_defeated": [], "enemies_defeated": 0,
        "started": time.time(), "buffs": {},
    }
    print(f"\nWelcome, {name} the {class_name}! Your journey begins in Eldoria.")
    return player


def weapon_record(item):
    name, rank, damage, required = item
    multiplier, crit_bonus, price = RARITY[rank]
    return {"name": name, "rank": rank, "damage": damage,
            "crit_bonus": crit_bonus, "price": price, "required": required}


def armor_record(item):
    name, rank, defense, hp, mana, crit_resist, required = item
    return {"name": name, "rank": rank, "defense": defense, "hp": hp,
            "mana": mana, "crit_resist": crit_resist,
            "price": RARITY[rank][2], "required": required}


def gear_stats(player):
    weapon = player.get("weapon")
    armor = player.get("armor")
    weapon_damage = weapon["damage"] if weapon else 0
    armor_defense = armor["defense"] if armor else 0
    return weapon_damage, armor_defense


def show_stats(p):
    wd, ad = gear_stats(p)
    print("\n" + "=" * 42)
    print(f"{p['name']} the {p['class']} | Level {p['level']}")
    print(f"HP: {p['hp']}/{p['max_hp']}   Mana: {p['mana']}/{p['max_mana']}")
    print(f"Attack: {p['attack']} (+{wd} weapon)   Defense: {p['defense']} (+{ad} armor)")
    print(f"Critical chance: {p['crit']}%   Gold: {p['gold']}   EXP: {p['exp']}")
    print(f"Weapon: {p['weapon']['name'] if p['weapon'] else 'None'}")
    print(f"Armor: {p['armor']['name'] if p['armor'] else 'None'}")
    print(f"Bosses defeated: {len(p['bosses_defeated'])}/10")
    print("=" * 42)


def save_game(p):
    data = dict(p)
    data.pop("started", None)
    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print("Game saved successfully.")


def load_game():
    if not os.path.exists(SAVE_FILE):
        print("No save file found.")
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            p = json.load(file)
        p["started"] = time.time()
        p.setdefault("buffs", {})
        print(f"Welcome back, {p['name']}!")
        return p
    except (OSError, json.JSONDecodeError, KeyError) as error:
        print("Could not load save:", error)
        return None


def level_up(p):
    while p["level"] < 100 and p["exp"] >= p["level"] * 100:
        p["exp"] -= p["level"] * 100
        p["level"] += 1
        p["max_hp"] += 18
        p["max_mana"] += 10
        p["attack"] += 3
        p["defense"] += 2
        p["hp"] = p["max_hp"]
        p["mana"] = p["max_mana"]
        print(f"\nLEVEL UP! You are now level {p['level']}!")
        if p["level"] % 5 == 0:
            p["crit"] += 2
            print("Milestone bonus: critical chance increased by 2%!")


def reward_enemy(p, boss=False):
    p["enemies_defeated"] += 1
    gained = random.randint(35, 65) if boss else random.randint(15, 35)
    p["gold"] += gained
    exp = random.randint(100, 160) if boss else random.randint(35, 65)
    p["exp"] += exp
    print(f"You earned {gained} gold and {exp} EXP.")
    if boss:
        return
    roll = random.random()
    if roll < 0.50:
        potion = random.choice(list(POTIONS))
        p["potions"][potion] = p["potions"].get(potion, 0) + 1
        print(f"Loot drop: {potion}!")
    elif roll < 0.70:
        item = random.choice(WEAPONS[:12])
        p["inventory"].append({"type": "weapon", "item": weapon_record(item)})
        print(f"Loot drop: {item[0]}!")
    elif roll < 0.82:
        item = random.choice(ARMORS[:8])
        p["inventory"].append({"type": "armor", "item": armor_record(item)})
        print(f"Loot drop: {item[0]}!")
    else:
        print("No item drop this time.")
    level_up(p)


def use_potion(p):
    available = [(name, count) for name, count in p["potions"].items() if count > 0]
    if not available:
        print("You have no potions.")
        return
    print("\nPotions:")
    for i, (name, count) in enumerate(available, 1):
        print(f"{i}. {name} x{count}")
    choice = ask_int("Choose potion (0 to cancel): ", 0, len(available))
    if choice == 0:
        return
    name = available[choice - 1][0]
    kind, amount, _ = POTIONS[name]
    p["potions"][name] -= 1
    if kind == "health":
        restored = p["max_hp"] - p["hp"] if amount == -1 else amount
        p["hp"] = min(p["max_hp"], p["hp"] + restored)
        print(f"Restored {restored} HP.")
    elif kind == "mana":
        restored = p["max_mana"] - p["mana"] if amount == -1 else amount
        p["mana"] = min(p["max_mana"], p["mana"] + restored)
        print(f"Restored {restored} mana.")
    elif kind == "mixed":
        h, m = amount
        p["hp"] = min(p["max_hp"], p["hp"] + h)
        p["mana"] = min(p["max_mana"], p["mana"] + m)
        print(f"Restored {h} HP and {m} mana.")
    else:
        key = kind.replace("buff_", "")
        p["buffs"][key] = (amount, 3)
        print(f"{key.title()} increased for 3 turns.")


def inventory_menu(p):
    while True:
        print("\nINVENTORY")
        print("1. View items  2. Equip item  3. Sell item  4. Drop item  0. Back")
        choice = ask_int("Choice: ", 0, 4)
        if choice == 0:
            return
        if choice == 1:
            if not p["inventory"]:
                print("Your inventory is empty.")
            for i, entry in enumerate(p["inventory"], 1):
                print(f"{i}. {entry['item']['name']} ({entry['type']})")
        elif choice in (2, 3, 4):
            if not p["inventory"]:
                print("Your inventory is empty.")
                continue
            for i, entry in enumerate(p["inventory"], 1):
                print(f"{i}. {entry['item']['name']} ({entry['type']})")
            index = ask_int("Item number: ", 1, len(p["inventory"])) - 1
            entry = p["inventory"][index]
            item = entry["item"]
            if choice == 2:
                if item["required"] > p["level"]:
                    print(f"You need level {item['required']} to equip this.")
                    continue
                if entry["type"] == "weapon":
                    p["weapon"] = item
                else:
                    p["armor"] = item
                    p["max_hp"] += item["hp"]
                    p["max_mana"] += item["mana"]
                    p["hp"] = min(p["hp"] + item["hp"], p["max_hp"])
                    p["mana"] = min(p["mana"] + item["mana"], p["max_mana"])
                p["inventory"].pop(index)
                print(f"Equipped {item['name']}.")
            elif choice == 3:
                value = max(1, item["price"] // 2)
                p["gold"] += value
                p["inventory"].pop(index)
                print(f"Sold for {value} gold.")
            else:
                p["inventory"].pop(index)
                print(f"Dropped {item['name']}.")


def shop(p):
    while True:
        print(f"\nVILLAGE SHOP | Gold: {p['gold']}")
        print("1. Weapons  2. Armor  3. Potions  4. Sell inventory  0. Exit")
        choice = ask_int("Choice: ", 0, 4)
        if choice == 0:
            return
        stock = []
        if choice == 1:
            stock = [("weapon", weapon_record(x)) for x in WEAPONS]
        elif choice == 2:
            stock = [("armor", armor_record(x)) for x in ARMORS]
        elif choice == 3:
            stock = [("potion", {"name": n, "price": v[2]}) for n, v in POTIONS.items()]
        elif choice == 4:
            inventory_menu(p)
            continue
        for i, (kind, item) in enumerate(stock, 1):
            print(f"{i}. {item['name']} - {item['price']} gold")
        print("0. Back")
        selected = ask_int("Buy item: ", 0, len(stock))
        if selected == 0:
            continue
        kind, item = stock[selected - 1]
        if kind in ("weapon", "armor") and item["required"] > p["level"]:
            print(f"Required level: {item['required']}")
            continue
        if p["gold"] < item["price"]:
            print("Not enough gold.")
            continue
        p["gold"] -= item["price"]
        if kind == "potion":
            p["potions"][item["name"]] = p["potions"].get(item["name"], 0) + 1
        else:
            p["inventory"].append({"type": kind, "item": item})
        print(f"Purchased {item['name']}.")


def make_enemy(p, boss=False):
    if boss:
        name = BOSSES.get(p["level"], "Ancient Demon King")
        hp = 180 + p["level"] * 24
        attack = 12 + p["level"] * 2
        defense = 5 + p["level"]
    else:
        name = random.choice(ENEMY_NAMES)
        hp = 35 + p["level"] * 12
        attack = 5 + p["level"] * 2
        defense = 1 + p["level"] // 3
    return {"name": name, "hp": hp, "max_hp": hp, "attack": attack,
            "defense": defense, "boss": boss, "turn": 0}


def class_skill(p):
    skills = {
        "Warrior": [("Slash", 8, 1.5), ("Shield Bash", 12, 1.7),
                    ("Rage", 18, 2.2), ("Earthquake", 30, 3.0)],
        "Mage": [("Fireball", 10, 1.6), ("Ice Blast", 15, 2.0),
                 ("Thunder Strike", 22, 2.6), ("Meteor", 35, 3.5)],
        "Archer": [("Multi Shot", 8, 1.5), ("Poison Arrow", 13, 1.9),
                   ("Explosive Arrow", 22, 2.5), ("Sniper Shot", 32, 3.2)],
        "Assassin": [("Backstab", 8, 1.8), ("Smoke Strike", 13, 2.0),
                     ("Shadow Strike", 22, 2.8), ("Deadly Strike", 32, 3.4)],
    }
    print("\nSkills:")
    for i, (name, cost, mult) in enumerate(skills[p["class"]], 1):
        print(f"{i}. {name} - {cost} mana")
    choice = ask_int("Choose skill (0 to cancel): ", 0, 4)
    if choice == 0:
        return None
    return skills[p["class"]][choice - 1]


def battle(p, enemy):
    print(f"\nA {'BOSS' if enemy['boss'] else 'wild'} {enemy['name']} appears!")
    defending = False
    while p["hp"] > 0 and enemy["hp"] > 0:
        print(f"\n{p['name']}: {p['hp']}/{p['max_hp']} HP | "
              f"{p['mana']}/{p['max_mana']} MP")
        print(f"{enemy['name']}: {enemy['hp']}/{enemy['max_hp']} HP")
        print("1 Attack  2 Skills  3 Heal  4 Use Potion")
        print("5 Defend  6 Inventory  7 Stats  8 Run")
        action = ask_int("Your action: ", 1, 8)
        if action == 1:
            damage = max(1, p["attack"] + gear_stats(p)[0] - enemy["defense"])
            crit_chance = p["crit"] + (p["weapon"]["crit_bonus"] if p["weapon"] else 0)
            if random.randint(1, 100) <= min(75, crit_chance):
                damage = int(damage * 2)
                print("CRITICAL HIT!")
            enemy["hp"] -= damage
            print(f"You dealt {damage} damage.")
        elif action == 2:
            skill = class_skill(p)
            if skill is None:
                continue
            name, cost, multiplier = skill
            if p["mana"] < cost:
                print("Not enough mana.")
                continue
            p["mana"] -= cost
            damage = max(1, int((p["attack"] + gear_stats(p)[0]) * multiplier)
                         - enemy["defense"])
            enemy["hp"] -= damage
            print(f"{name}! You dealt {damage} damage.")
        elif action == 3:
            amount = min(60, p["max_hp"] - p["hp"])
            p["hp"] += amount
            print(f"You recovered {amount} HP.")
        elif action == 4:
            use_potion(p)
        elif action == 5:
            defending = True
            print("You brace yourself. Next incoming damage is reduced by 50%.")
        elif action == 6:
            inventory_menu(p)
        elif action == 7:
            show_stats(p)
        elif action == 8 and not enemy["boss"]:
            if random.random() < 0.5:
                print("You escaped.")
                return False
            print("Escape failed!")
        elif action == 8:
            print("You cannot run from a boss!")
            continue

        if enemy["hp"] <= 0:
            break
        enemy["turn"] += 1
        incoming = max(1, enemy["attack"] - p["defense"] - gear_stats(p)[1])
        if enemy["boss"] and enemy["turn"] % 3 == 0:
            incoming = int(incoming * 1.8)
            print(f"{enemy['name']} uses a powerful special attack!")
        if defending:
            incoming = max(1, incoming // 2)
            defending = False
        p["hp"] -= incoming
        print(f"{enemy['name']} dealt {incoming} damage.")
        if enemy["boss"] and enemy["hp"] < enemy["max_hp"] // 3 and random.random() < 0.25:
            heal = int(enemy["max_hp"] * 0.08)
            enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + heal)
            print(f"{enemy['name']} recovers {heal} HP!")
        for key in list(p["buffs"]):
            amount, turns = p["buffs"][key]
            turns -= 1
            if turns <= 0:
                del p["buffs"][key]
            else:
                p["buffs"][key] = (amount, turns)

    if p["hp"] <= 0:
        print("\nGAME OVER. Your hero has fallen.")
        return False
    print(f"\nYou defeated {enemy['name']}!")
    reward_enemy(p, enemy["boss"])
    if enemy["boss"]:
        p["bosses_defeated"].append(enemy["name"])
        p["hp"] = min(p["max_hp"], p["hp"] + 40)
        p["mana"] = min(p["max_mana"], p["mana"] + 30)
        print("Boss reward: bonus recovery and progression unlocked!")
    return True


def instructions():
    print("""
LEGENDS OF THE FORGOTTEN REALM
Defeat enemies to earn EXP and gold. Level up to become stronger.
Every 10 levels, defeat the region boss to unlock the next region.
Use the village shop to buy equipment and potions.
Equip gear from Inventory. Save regularly from the main game menu.
Reach level 100 and defeat the Ancient Demon King to win.
""")


def victory(p):
    elapsed = int(time.time() - p.get("started", time.time()))
    print("\n" + "*" * 48)
    print("       YOU SAVED THE FORGOTTEN REALM!")
    print("*" * 48)
    print(f"Hero: {p['name']} | Class: {p['class']}")
    print(f"Final level: {p['level']} | Gold: {p['gold']}")
    print(f"Bosses defeated: {len(p['bosses_defeated'])}")
    print(f"Enemies defeated: {p['enemies_defeated']}")
    print(f"Play time: {elapsed // 60} minutes {elapsed % 60} seconds")
    print(f"Items collected: {len(p['inventory'])}")
    print("Final score:", p["level"] * 100 + p["gold"] + p["enemies_defeated"] * 10)
    print("*" * 48)


def play(p):
    while True:
        if p["level"] >= 100 and "Ancient Demon King" in p["bosses_defeated"]:
            victory(p)
            return
        region_index = min((p["level"] - 1) // 10, 9)
        print(f"\n--- {REGIONS[region_index]} | Level {p['level']} ---")
        print("1. Explore and fight  2. Village shop  3. Inventory")
        print("4. View stats  5. Save game  6. Main menu")
        choice = ask_int("Choose: ", 1, 6)
        if choice == 1:
            next_boss_level = ((p["level"] // 10) + 1) * 10
            if p["level"] in BOSSES and p["level"] not in [int(x) for x in []]:
                boss_name = BOSSES[p["level"]]
                if boss_name not in p["bosses_defeated"]:
                    won = battle(p, make_enemy(p, True))
                    if not won and p["hp"] <= 0:
                        return
                    continue
            if p["level"] >= 100:
                print("Defeat the final boss to finish the game.")
                continue
            if p["level"] >= next_boss_level:
                print("Defeat the boss to unlock the next region.")
                continue
            won = battle(p, make_enemy(p))
            if not won and p["hp"] <= 0:
                return
        elif choice == 2:
            shop(p)
        elif choice == 3:
            inventory_menu(p)
        elif choice == 4:
            show_stats(p)
        elif choice == 5:
            save_game(p)
        elif choice == 6:
            return


def main():
    while True:
        print("\n" + "=" * 44)
        print(" LEGENDS OF THE FORGOTTEN REALM")
        print("=" * 44)
        print("1. New Game\n2. Continue\n3. Instructions\n4. Exit")
        choice = ask_int("Select: ", 1, 4)
        if choice == 1:
            player = new_player()
            play(player)
        elif choice == 2:
            player = load_game()
            if player:
                play(player)
        elif choice == 3:
            instructions()
        else:
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
