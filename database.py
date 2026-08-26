"""
Database persistence and game engine calculations using SQLite.
"""

import sqlite3
import json
import time
import os
import random
import threading
from collections import defaultdict
from functools import wraps
from typing import Dict, Any, Tuple, List, Optional
import config
from config import (
    UPGRADES, get_upgrade_cost, MAX_OFFLINE_SECONDS, TOTAL_HUMAN_SOULS,
    ENCOUNTERS, MYTHIC_ARTIFACTS, VOYAGES, FATE_CARDS, BOUNTY_TEMPLATES,
    SURGE_CHARGE_PER_ROW, SURGE_THRESHOLD, SURGE_DURATION_SECONDS, SURGE_MULTIPLIER
)

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "charon.db")
_PLAYER_MUTATION_LOCKS = defaultdict(threading.RLock)


def serialized_player_mutation(func):
    """Prevent concurrent interactions from overwriting one player's state."""
    @wraps(func)
    def wrapper(user_id: int, *args, **kwargs):
        with _PLAYER_MUTATION_LOCKS[user_id]:
            return func(user_id, *args, **kwargs)
    return wrapper


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema and performs auto-migrations."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                obols REAL DEFAULT 0,
                total_souls REAL DEFAULT 0,
                upgrades TEXT DEFAULT '{}',
                prestige INTEGER DEFAULT 0,
                last_update REAL DEFAULT 0,
                last_daily REAL DEFAULT 0,
                encounters_completed INTEGER DEFAULT 0,
                artifacts TEXT DEFAULT '{}',
                ashen_embers INTEGER DEFAULT 0,
                active_bounties TEXT DEFAULT '[]',
                surge_meter REAL DEFAULT 0.0,
                surge_expires REAL DEFAULT 0.0,
                last_gamble REAL DEFAULT 0.0,
                last_fate_card REAL DEFAULT 0.0,
                active_voyage TEXT DEFAULT '{}',
                pending_encounter TEXT DEFAULT '',
                stats TEXT DEFAULT '{}',
                equipment TEXT DEFAULT '{}',
                owned_gear TEXT DEFAULT '[]'
            )
        """)

        # Check existing columns for backwards compatibility
        cursor.execute("PRAGMA table_info(players)")
        columns = [row["name"] for row in cursor.fetchall()]

        new_column_statements = {
            "encounters_completed": "ALTER TABLE players ADD COLUMN encounters_completed INTEGER DEFAULT 0",
            "artifacts": "ALTER TABLE players ADD COLUMN artifacts TEXT DEFAULT '{}'",
            "ashen_embers": "ALTER TABLE players ADD COLUMN ashen_embers INTEGER DEFAULT 0",
            "active_bounties": "ALTER TABLE players ADD COLUMN active_bounties TEXT DEFAULT '[]'",
            "surge_meter": "ALTER TABLE players ADD COLUMN surge_meter REAL DEFAULT 0.0",
            "surge_expires": "ALTER TABLE players ADD COLUMN surge_expires REAL DEFAULT 0.0",
            "last_gamble": "ALTER TABLE players ADD COLUMN last_gamble REAL DEFAULT 0.0",
            "last_fate_card": "ALTER TABLE players ADD COLUMN last_fate_card REAL DEFAULT 0.0",
            "active_voyage": "ALTER TABLE players ADD COLUMN active_voyage TEXT DEFAULT '{}'",
            "pending_encounter": "ALTER TABLE players ADD COLUMN pending_encounter TEXT DEFAULT ''",
            "stats": "ALTER TABLE players ADD COLUMN stats TEXT DEFAULT '{}'"
            ,"equipment": "ALTER TABLE players ADD COLUMN equipment TEXT DEFAULT '{}'"
            ,"owned_gear": "ALTER TABLE players ADD COLUMN owned_gear TEXT DEFAULT '[]'"
        }

        for col, stmt in new_column_statements.items():
            if col not in columns:
                cursor.execute(stmt)

        conn.commit()


def calculate_rates(upgrades_dict: Dict[str, int], prestige: int = 0, artifacts_dict: Dict[str, bool] = None, is_surge: bool = False) -> Tuple[float, float]:
    """Calculates current Obols Per Click (OPC) and Obols Per Second (OPS)."""
    if artifacts_dict is None:
        artifacts_dict = {}

    base_opc = 1.0
    base_ops = 0.0

    for item_id, count in upgrades_dict.items():
        if item_id in UPGRADES and count > 0:
            item = UPGRADES[item_id]
            if item["type"] == "opc":
                base_opc += item["power"] * count
            elif item["type"] == "ops":
                base_ops += item["power"] * count

    # Apply Artifact percentage bonuses
    art_opc_bonus = 0.0
    art_ops_bonus = 0.0
    for art_id, unlocked in artifacts_dict.items():
        if unlocked and art_id in MYTHIC_ARTIFACTS:
            art = MYTHIC_ARTIFACTS[art_id]
            art_opc_bonus += art.get("opc_bonus", 0.0)
            art_ops_bonus += art.get("ops_bonus", 0.0)

    base_opc *= (1.0 + art_opc_bonus)
    base_ops *= (1.0 + art_ops_bonus)

    # Prestige multiplier (each prestige adds +100% boost)
    multiplier = 1.0 + (prestige * 1.0)
    opc = base_opc * multiplier
    ops = base_ops * multiplier

    # Styx Surge multiplier (15x frenzy boost)
    if is_surge:
        opc *= SURGE_MULTIPLIER
        ops *= SURGE_MULTIPLIER

    return opc, ops


def is_surge_active(player: dict) -> bool:
    """Checks if Styx Surge frenzy is currently active."""
    return time.time() < player.get("surge_expires", 0.0)


def current_river() -> dict:
    """Returns a globally rotating river condition (one condition every 3 minutes)."""
    return config.RIVER_CURRENTS[int(time.time() // 180) % len(config.RIVER_CURRENTS)]


def equipped(player: dict, gear_id: str) -> bool:
    return gear_id in player.get("equipment", {}).values()


def gear_effect_multiplier(player: dict, archetype: str) -> float:
    current = current_river()
    if archetype == current["favored"]:
        return 1.25
    if archetype == current["penalty"]:
        return 0.75
    return 1.0


def get_active_pacts(player: dict) -> list[str]:
    equipment = player.get("equipment", {})
    pacts = []
    if equipment.get("hull") == "king_hull" and equipment.get("figurehead") == "king_figurehead":
        pacts.append("Pact of the Underworld King")
    return pacts


def vessel_level(player: dict) -> int:
    return max(1, min(10, int(player.get("stats", {}).get("vessel_level", 1))))


def tempered_stroke_bonus(player: dict) -> float:
    """Total randomized Soulfire bonuses on presently equipped components."""
    mods = player.get("stats", {}).get("gear_mods", {})
    levels = player.get("stats", {}).get("gear_levels", {})
    return sum(float(mods.get(gear_id, 0.0)) + (0.10 * int(levels.get(gear_id, 0))) for gear_id in player.get("equipment", {}).values())


def process_offline_earnings(player: dict) -> Tuple[dict, float]:
    """Applies passive OPS income based on elapsed time."""
    now = time.time()
    last_update = player.get("last_update", 0)
    
    if last_update <= 0:
        player["last_update"] = now
        return player, 0.0

    elapsed = now - last_update
    if elapsed <= 0:
        return player, 0.0

    # Cap offline gains
    capped_elapsed = min(elapsed, MAX_OFFLINE_SECONDS)
    
    upgrades = player["upgrades"]
    prestige = player.get("prestige", 0)
    artifacts = player.get("artifacts", {})
    surge = is_surge_active(player)
    
    _, ops = calculate_rates(upgrades, prestige, artifacts, surge)
    if time.time() < player.get("stats", {}).get("overseer_expires", 0.0):
        ops *= 6.0

    earned = ops * capped_elapsed
    player["obols"] += earned
    if equipped(player, "soul_siphon_hull"):
        player["obols"] += earned * 0.15 * gear_effect_multiplier(player, "necromancer")
    remaining_souls = max(0.0, TOTAL_HUMAN_SOULS - player["total_souls"])
    actual_souls_earned = min(earned, remaining_souls)
    player["total_souls"] += actual_souls_earned
    player["last_update"] = now

    return player, earned


def generate_initial_bounties() -> List[dict]:
    """Creates a fresh set of 3 random active bounties."""
    sample_templates = random.sample(BOUNTY_TEMPLATES, min(3, len(BOUNTY_TEMPLATES)))
    bounties = []
    for t in sample_templates:
        bounties.append({
            "id": f"{t['id']}_{int(time.time())}_{random.randint(100, 999)}",
            "template_id": t["id"],
            "title": t["title"],
            "desc": t["desc"].format(target=t["target"]),
            "target": t["target"],
            "current": 0,
            "reward_embers": t["reward_embers"],
            "type": t["type"],
            "claimed": False
        })
    return bounties


def get_player(user_id: int, username: str = "Ferryman") -> dict:
    """Retrieves or creates a player, processing offline earnings."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        now = time.time()

        if row is None:
            default_upgrades = json.dumps({})
            default_artifacts = json.dumps({})
            default_bounties = json.dumps(generate_initial_bounties())
            default_voyage = json.dumps({})
            default_stats = json.dumps({})

            cursor.execute("""
                INSERT INTO players (
                    user_id, username, obols, total_souls, upgrades, prestige,
                    last_update, last_daily, encounters_completed, artifacts,
                    ashen_embers, active_bounties, surge_meter, surge_expires,
                    last_gamble, last_fate_card, active_voyage, pending_encounter, stats
                )
                VALUES (?, ?, 0, 0, ?, 0, ?, 0, 0, ?, 0, ?, 0.0, 0.0, 0.0, 0.0, ?, '', ?)
            """, (user_id, username, default_upgrades, now, default_artifacts, default_bounties, default_voyage, default_stats))
            conn.commit()

            return {
                "user_id": user_id,
                "username": username,
                "obols": 0.0,
                "total_souls": 0.0,
                "upgrades": {},
                "prestige": 0,
                "last_update": now,
                "last_daily": 0.0,
                "offline_earned": 0.0,
                "encounters_completed": 0,
                "artifacts": {},
                "ashen_embers": 0,
                "active_bounties": json.loads(default_bounties),
                "surge_meter": 0.0,
                "surge_expires": 0.0,
                "last_gamble": 0.0,
                "last_fate_card": 0.0,
                "active_voyage": {},
                "pending_encounter": "",
                "stats": {}
                ,"equipment": {}
                ,"owned_gear": []
            }

        # Convert row to dict
        bounties = json.loads(row["active_bounties"]) if row["active_bounties"] else []
        if not bounties:
            bounties = generate_initial_bounties()

        player = {
            "user_id": row["user_id"],
            "username": username if username != "Ferryman" else row["username"],
            "obols": float(row["obols"]),
            "total_souls": float(row["total_souls"]),
            "upgrades": json.loads(row["upgrades"]) if row["upgrades"] else {},
            "prestige": int(row["prestige"]),
            "last_update": float(row["last_update"]),
            "last_daily": float(row["last_daily"]),
            "encounters_completed": int(row["encounters_completed"] or 0),
            "artifacts": json.loads(row["artifacts"]) if row["artifacts"] else {},
            "ashen_embers": int(row["ashen_embers"] or 0),
            "active_bounties": bounties,
            "surge_meter": float(row["surge_meter"] or 0.0),
            "surge_expires": float(row["surge_expires"] or 0.0),
            "last_gamble": float(row["last_gamble"] or 0.0),
            "last_fate_card": float(row["last_fate_card"] or 0.0),
            "active_voyage": json.loads(row["active_voyage"]) if row["active_voyage"] else {},
            "pending_encounter": str(row["pending_encounter"] or ""),
            "stats": json.loads(row["stats"]) if row["stats"] else {}
            ,"equipment": json.loads(row["equipment"]) if row["equipment"] else {}
            ,"owned_gear": json.loads(row["owned_gear"]) if row["owned_gear"] else []
        }

        # Update username if changed
        if username != "Ferryman" and username != row["username"]:
            cursor.execute("UPDATE players SET username = ? WHERE user_id = ?", (username, user_id))

        player, offline_earned = process_offline_earnings(player)
        player["offline_earned"] = offline_earned

        # Save processed earnings
        cursor.execute("""
            UPDATE players 
            SET obols = ?, total_souls = ?, last_update = ?
            WHERE user_id = ?
        """, (player["obols"], player["total_souls"], player["last_update"], user_id))
        conn.commit()

        return player


def save_player(player: dict):
    """Saves player state back to database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE players
            SET username = ?, obols = ?, total_souls = ?, upgrades = ?, prestige = ?,
                last_update = ?, last_daily = ?, encounters_completed = ?,
                artifacts = ?, ashen_embers = ?, active_bounties = ?,
                surge_meter = ?, surge_expires = ?, last_gamble = ?,
                last_fate_card = ?, active_voyage = ?, pending_encounter = ?, stats = ?, equipment = ?, owned_gear = ?
            WHERE user_id = ?
        """, (
            player["username"],
            player["obols"],
            player["total_souls"],
            json.dumps(player["upgrades"]),
            player["prestige"],
            player["last_update"],
            player["last_daily"],
            player.get("encounters_completed", 0),
            json.dumps(player.get("artifacts", {})),
            player.get("ashen_embers", 0),
            json.dumps(player.get("active_bounties", [])),
            player.get("surge_meter", 0.0),
            player.get("surge_expires", 0.0),
            player.get("last_gamble", 0.0),
            player.get("last_fate_card", 0.0),
            json.dumps(player.get("active_voyage", {})),
            player.get("pending_encounter", ""),
            json.dumps(player.get("stats", {})),
            json.dumps(player.get("equipment", {})),
            json.dumps(player.get("owned_gear", [])),
            player["user_id"]
        ))
        conn.commit()


def progress_bounty(player: dict, bounty_type: str, amount: int = 1) -> bool:
    """Updates progress on matching active bounties."""
    updated = False
    for b in player.get("active_bounties", []):
        if b["type"] == bounty_type and not b.get("claimed", False):
            b["current"] = min(b["target"], b.get("current", 0) + amount)
            updated = True
    return updated


def add_surge_energy(player: dict, amount: float = SURGE_CHARGE_PER_ROW) -> Tuple[bool, bool]:
    """
    Increases the Styx Surge meter.
    Returns (surge_just_triggered, is_currently_active).
    """
    now = time.time()
    if now < player.get("surge_expires", 0.0):
        return False, True

    # Artifact bonus: Stygian Iron Oarlock doubles charge rate
    if player.get("artifacts", {}).get("iron_oarlock"):
        amount *= 2.0

    current = player.get("surge_meter", 0.0) + amount
    if current >= SURGE_THRESHOLD:
        duration = SURGE_DURATION_SECONDS
        if "Pact of the Underworld King" in get_active_pacts(player):
            duration *= 5
        if player.get("artifacts", {}).get("helm_shadows"):
            duration += 15.0  # Helm of Shadow bonus
        player["surge_meter"] = 0.0
        player["surge_expires"] = now + duration
        progress_bounty(player, "surges_triggered", 1)
        return True, True
    else:
        player["surge_meter"] = current
        return False, False


def ferry_souls(user_id: int, username: str = "Ferryman") -> Tuple[dict, float, float, bool, Optional[str]]:
    """
    Ferries souls (click action).
    Returns (player, click_earned, offline_earned, surge_triggered, new_encounter_id).
    """
    player = get_player(user_id, username)
    offline_earned = player.pop("offline_earned", 0.0)

    # If the player has already ferried all human souls, no more souls remain to be ferried
    if player["total_souls"] >= TOTAL_HUMAN_SOULS:
        player["total_souls"] = float(TOTAL_HUMAN_SOULS)
        save_player(player)
        return player, 0.0, offline_earned, False, None

    surge_triggered, surge_active = add_surge_energy(player)

    opc, _ = calculate_rates(player["upgrades"], player["prestige"], player.get("artifacts", {}), surge_active)
    opc *= 1.0 + tempered_stroke_bonus(player)
    now = time.time()
    # The Speed-Rower turns cadence into a short-lived, skill-driven multiplier.
    if equipped(player, "fury_oarlock"):
        stats = player.setdefault("stats", {})
        last = stats.get("last_row_at", 0.0)
        combo = min(10, stats.get("rhythm_combo", 0) + 1) if now - last <= 2 else 1
        stats["rhythm_combo"] = combo
        stats["last_row_at"] = now
        opc *= combo * gear_effect_multiplier(player, "speed")
    else:
        player.setdefault("stats", {})["rhythm_combo"] = 0
    if equipped(player, "bone_diviner_oar") and random.random() < .12:
        opc *= 3 * gear_effect_multiplier(player, "fate")
        player.setdefault("stats", {})["last_gear_proc"] = "Critical Dice Roll! 3x soul burst."
    if surge_active and equipped(player, "bellowing_drums"):
        player["surge_expires"] += 1
    if equipped(player, "chthonic_overseer"):
        player.setdefault("stats", {})["overseer_expires"] = now + 10
    
    # Coin of the Damned gives double obols
    obol_gain = opc * (2.0 if player.get("artifacts", {}).get("coin_damned") else 1.0)
    
    player["obols"] += obol_gain
    
    remaining_souls = max(0.0, TOTAL_HUMAN_SOULS - player["total_souls"])
    actual_souls_added = min(opc, remaining_souls)
    player["total_souls"] += actual_souls_added

    # Progress stats and bounties
    stats = player.get("stats", {})
    stats["total_rows"] = stats.get("total_rows", 0) + 1
    player["stats"] = stats
    progress_bounty(player, "manual_rows", 1)

    # Roll for River Encounter (~18% chance, boosted by Golden Bough)
    new_encounter_id = None
    if not player.get("pending_encounter"):
        # Anomalies are rare events, not a five-stroke interruption.
        chance = 0.03
        if player.get("artifacts", {}).get("golden_bough"):
            chance += 0.10
        if equipped(player, "siren_bait_net"):
            # Net builds target a maximum 12% encounter rate. Cap after all
            # modifiers so Golden Bough cannot turn it into a 52% interruption.
            chance = min(chance * 4 * gear_effect_multiplier(player, "marauder"), 0.12)
        if random.random() < chance:
            anomaly_levels = {"gilded_king": 1, "wandering_shades": 2, "siren_cocytus": 3, "thanatos_envoy": 4, "charybdis_vortex": 6}
            eligible = [enc_id for enc_id in ENCOUNTERS if vessel_level(player) >= anomaly_levels.get(enc_id, 1)]
            encounter_id = random.choice(eligible)
            player["pending_encounter"] = encounter_id
            new_encounter_id = encounter_id

    save_player(player)
    return player, opc, offline_earned, surge_triggered, new_encounter_id


@serialized_player_mutation
def buy_gear(user_id: int, gear_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Binds a unique gear piece and equips it in its dedicated vessel slot."""
    if gear_id not in config.GEAR:
        return False, "Unknown vessel component.", {}
    player = get_player(user_id, username)
    if gear_id in player.get("owned_gear", []):
        return False, "That component is already bound. Equip it from the forge list.", player
    gear = config.GEAR[gear_id]
    if vessel_level(player) < gear["vessel_req"]:
        return False, f"Requires Vessel Rank {gear['vessel_req']} (your vessel is Rank {vessel_level(player)}).", player
    if player["obols"] < gear["cost"]:
        return False, f"Requires {gear['cost']:,} Obols.", player
    player["obols"] -= gear["cost"]
    player.setdefault("owned_gear", []).append(gear_id)
    player.setdefault("equipment", {})[gear["slot"]] = gear_id
    save_player(player)
    return True, f"Bound and equipped {gear['name']} in the {gear['slot']} slot.", player


@serialized_player_mutation
def equip_gear(user_id: int, gear_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    player = get_player(user_id, username)
    if gear_id not in player.get("owned_gear", []) or gear_id not in config.GEAR:
        return False, "That component has not been forged.", player
    gear = config.GEAR[gear_id]
    player.setdefault("equipment", {})[gear["slot"]] = gear_id
    save_player(player)
    return True, f"Equipped {gear['name']}.", player


@serialized_player_mutation
def transmute_gear(user_id: int, gear_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Spend Embers to reroll a Soulfire stroke modifier on a bound component."""
    player = get_player(user_id, username)
    if gear_id not in player.get("owned_gear", []) or gear_id not in config.GEAR:
        return False, "Only a bound vessel component can be transmuted.", player
    cost = 25
    if player.get("ashen_embers", 0) < cost:
        return False, f"Transmutation requires {cost} Ashen Embers.", player
    bonus = random.randint(10, 30) / 100
    player["ashen_embers"] -= cost
    player.setdefault("stats", {}).setdefault("gear_mods", {})[gear_id] = bonus
    save_player(player)
    return True, f"Soulfire reshaped {config.GEAR[gear_id]['name']}: **+{bonus:.0%} stroke yield** while equipped.", player


@serialized_player_mutation
def upgrade_gear(user_id: int, gear_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Level a bound component to a maximum of 10; Ember costs rise quadratically."""
    player = get_player(user_id, username)
    if gear_id not in player.get("owned_gear", []) or gear_id not in config.GEAR:
        return False, "Only a bound vessel component can be upgraded.", player
    levels = player.setdefault("stats", {}).setdefault("gear_levels", {})
    level = int(levels.get(gear_id, 0))
    if level >= 10:
        return False, f"{config.GEAR[gear_id]['name']} is already at the maximum level (10).", player
    cost = 10 * (level + 1) ** 2
    if player.get("ashen_embers", 0) < cost:
        return False, f"Level {level + 1} requires {cost} Ashen Embers.", player
    player["ashen_embers"] -= cost
    levels[gear_id] = level + 1
    save_player(player)
    return True, f"Upgraded {config.GEAR[gear_id]['name']} to **Level {level + 1}/10** (+10% stroke yield while equipped).", player


@serialized_player_mutation
def upgrade_vessel(user_id: int, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Refit the whole vessel, unlocking higher-rank gear and river content."""
    player = get_player(user_id, username)
    level = vessel_level(player)
    if level >= 10:
        return False, "The Elysian Cruise Ship is already the final vessel rank.", player
    obol_cost, ember_cost = config.vessel_upgrade_cost(level)
    if player["obols"] < obol_cost or player.get("ashen_embers", 0) < ember_cost:
        return False, f"Rank {level + 1} needs {obol_cost:,.0f} Obols and {ember_cost} Ashen Embers.", player
    player["obols"] -= obol_cost
    player["ashen_embers"] -= ember_cost
    player.setdefault("stats", {})["vessel_level"] = level + 1
    save_player(player)
    return True, f"Refit complete: **Rank {level + 1} — {config.VESSEL_LEVELS[level + 1]}**. New gear and river threats answer your wake.", player


def resolve_encounter(user_id: int, encounter_id: str, choice_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Resolves a player's decision for a random River Encounter."""
    player = get_player(user_id, username)
    if player.get("pending_encounter") != encounter_id and encounter_id not in ENCOUNTERS:
        return False, "This encounter has dissolved into the river mist.", player

    opc, ops = calculate_rates(player["upgrades"], player["prestige"], player.get("artifacts", {}))
    msg = ""

    if encounter_id == "gilded_king":
        if choice_id == "bribe":
            gold = max(500.0, ops * 1200.0)
            player["obols"] += gold
            loss = player["total_souls"] * 0.05
            player["total_souls"] = max(0.0, player["total_souls"] - loss)
            msg = f"👑 You took the King's bribe! Received **+{gold:,.0f} Obols**, but lost {loss:,.0f} souls to cosmic shame."
        elif choice_id == "ferry":
            souls_reward = max(100.0, opc * 50.0)
            remaining_souls = max(0.0, TOTAL_HUMAN_SOULS - player["total_souls"])
            actual_souls = min(souls_reward, remaining_souls)
            player["total_souls"] += actual_souls
            player["ashen_embers"] = player.get("ashen_embers", 0) + 10
            msg = f"👑 You refused corruption! Delivered **+{actual_souls:,.0f} souls** and earned **+10 Ashen Embers** from Hades."
        elif choice_id == "extort":
            if random.random() < 0.5:
                gold = max(1000.0, ops * 2500.0)
                player["obols"] += gold
                msg = f"👑 **EXTORTION SUCCESS!** You shook down the King for **+{gold:,.0f} Obols**!"
            else:
                msg = "👑 The King cursed your oars in fury! No gold gained."

    elif encounter_id == "siren_cocytus":
        if choice_id == "listen":
            if random.random() < 0.5:
                player["surge_expires"] = time.time() + 60.0
                msg = "🌊 **ECSTATIC FRENZY!** The Siren's song ignited a 60-second **Acheron's Wake (15x Multiplier)**!"
            else:
                loss = player["obols"] * 0.15
                player["obols"] = max(0.0, player["obols"] - loss)
                msg = f"🌊 The Siren's sorrow overwhelmed you. Lost {loss:,.0f} Obols into the icy waters."
        elif choice_id == "plug_ears":
            safe_obols = max(200.0, opc * 30.0)
            player["obols"] += safe_obols
            msg = f"🌊 You plugged your ears with wax and rowed steadily forward. Gained **+{safe_obols:,.0f} Obols**."
        elif choice_id == "cast_net":
            embers = random.randint(15, 30)
            player["ashen_embers"] = player.get("ashen_embers", 0) + embers
            msg = f"🌊 You dredged the frozen riverbed and hauled up **+{embers} Ashen Embers**!"

    elif encounter_id == "charybdis_vortex":
        if choice_id == "power_through":
            if opc >= 5.0 or random.random() < 0.6:
                souls_won = max(500.0, opc * 150.0)
                remaining_souls = max(0.0, TOTAL_HUMAN_SOULS - player["total_souls"])
                actual_souls = min(souls_won, remaining_souls)
                player["total_souls"] += actual_souls
                msg = f"🌪️ **TRIUMPH!** You cleaved through the maelstrom with Titan fury, ferrying **+{actual_souls:,.0f} souls**!"
            else:
                loss = min(player["obols"], 1000.0)
                player["obols"] -= loss
                msg = f"🌪️ The vortex battered your vessel. Lost {loss:,.0f} Obols in structural damage."
        elif choice_id == "sacrifice_cargo":
            player["ashen_embers"] = player.get("ashen_embers", 0) + 25
            msg = "🌪️ You cast out shrouds and drifted smoothly around the vortex, claiming a **Stygian Shard (+25 Ashen Embers)**!"

    elif encounter_id == "wandering_shades":
        if choice_id == "bless":
            souls_won = max(1000.0, (opc + ops) * 100.0)
            remaining_souls = max(0.0, TOTAL_HUMAN_SOULS - player["total_souls"])
            actual_souls = min(souls_won, remaining_souls)
            player["total_souls"] += actual_souls
            msg = f"⚔️ The Spartan Phalanx salutes as they pass into Elysium. Delivered **+{actual_souls:,.0f} souls**!"
        elif choice_id == "conscript":
            upgrades = player["upgrades"]
            upgrades["skeleton"] = upgrades.get("skeleton", 0) + 5
            player["upgrades"] = upgrades
            msg = "⚔️ **MARSHAL FORCE!** Bound 5 Spartan shades directly as **+5 Bound Shade Rowers**!"

    elif encounter_id == "thanatos_envoy":
        if choice_id == "gamble":
            roll = random.randint(1, 6)
            if roll >= 4:
                reward = max(1500.0, ops * 300.0)
                player["obols"] += reward
                msg = f"⚖️ You rolled a **{roll}**! Thanatos smiles and bestows **+{reward:,.0f} Obols**."
            else:
                msg = f"⚖️ You rolled a **{roll}**. Thanatos takes flight into the void."
        elif choice_id == "tribute":
            cost = 1000.0
            if player["obols"] >= cost:
                player["obols"] -= cost
                player["surge_meter"] = min(SURGE_THRESHOLD, player.get("surge_meter", 0.0) + 50.0)
                msg = "⚖️ Surrendered 1,000 Obols. Gained **+50% Acheron's Wake Charge**!"
            else:
                msg = "⚖️ You lack the 1,000 Obols for tribute."

    # Clear pending encounter & increment stats
    player["pending_encounter"] = ""
    player["encounters_completed"] = player.get("encounters_completed", 0) + 1
    progress_bounty(player, "encounters_resolved", 1)
    save_player(player)

    return True, msg, player


def start_voyage(user_id: int, voyage_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Begins an Underworld River Voyage."""
    if voyage_id not in VOYAGES:
        return False, "Unknown voyage destination.", {}

    player = get_player(user_id, username)
    voyage_data = VOYAGES[voyage_id]
    required_rank = config.VOYAGE_VESSEL_REQUIREMENTS.get(voyage_id, 1)
    if vessel_level(player) < required_rank:
        return False, f"{voyage_data['name']} requires Vessel Rank {required_rank}.", player

    if player["total_souls"] < voyage_data["min_souls"]:
        return False, f"Requires at least **{voyage_data['min_souls']:,}** souls delivered to enter {voyage_data['name']}.", player

    player["active_voyage"] = {
        "voyage_id": voyage_id,
        "stage": 0,
        "history": []
    }
    save_player(player)
    return True, f"Embarked on voyage: **{voyage_data['name']}**!", player


def choose_voyage_action(user_id: int, choice_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict, bool]:
    """
    Advances active voyage stage.
    Returns (success, message, player, voyage_completed).
    """
    player = get_player(user_id, username)
    active_voyage = player.get("active_voyage", {})
    if not active_voyage or "voyage_id" not in active_voyage:
        return False, "No active voyage. Use `/voyage` to embark.", player, False

    voyage_id = active_voyage["voyage_id"]
    voyage_cfg = VOYAGES[voyage_id]
    current_stage = active_voyage["stage"]

    stage_info = voyage_cfg["stages"][current_stage]
    current_stage += 1
    active_voyage["stage"] = current_stage

    if current_stage >= len(voyage_cfg["stages"]):
        # Voyage completed!
        embers = voyage_cfg["reward_embers"]
        _, ops = calculate_rates(player["upgrades"], player["prestige"], player.get("artifacts", {}))
        gold = max(1000.0, ops * voyage_cfg["reward_obols_mult"])

        player["ashen_embers"] = player.get("ashen_embers", 0) + embers
        player["obols"] += gold
        player["active_voyage"] = {}

        progress_bounty(player, "voyages_completed", 1)
        save_player(player)
        
        msg = f"🏆 **VOYAGE TRIUMPH!** You mastered **{voyage_cfg['name']}**!\n" \
              f"Rewards: **+{embers} Ashen Embers** and **+{gold:,.0f} Obols**."
        return True, msg, player, True
    else:
        active_voyage["history"].append(choice_id)
        player["active_voyage"] = active_voyage
        save_player(player)
        return True, f"Passed {stage_info['title']}. Moving to Stage {current_stage + 1}...", player, False


def roll_knucklebones(user_id: int, wager: int, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Wagers Obols in a 2d6 dice game against Thanatos."""
    if wager < 10:
        return False, "Minimum wager is 10 Obols.", {}

    player = get_player(user_id, username)
    if player["obols"] < wager:
        return False, f"Not enough Obols! Vaulted: **{player['obols']:,.0f}**", player

    now = time.time()
    if now - player.get("last_gamble", 0.0) < 5.0:
        return False, "Thanatos gathers the knuckle-bones. Please wait a few seconds before rolling again.", player

    p_d1, p_d2 = random.randint(1, 6), random.randint(1, 6)
    t_d1, t_d2 = random.randint(1, 6), random.randint(1, 6)
    p_total = p_d1 + p_d2
    t_total = t_d1 + t_d2

    player["last_gamble"] = now
    progress_bounty(player, "gambles_played", 1)

    fate_weaver = equipped(player, "moirai_spindle")
    if p_total > t_total:
        multiplier = 3.0 if p_d1 == p_d2 else 2.0
        if fate_weaver:
            multiplier *= 4.0 * gear_effect_multiplier(player, "fate")
        winnings = wager * multiplier
        player["obols"] += (winnings - wager)
        save_player(player)
        crit_msg = " ⚡ **DOUBLE CRIT!**" if p_d1 == p_d2 else ""
        return True, f"🎲 You rolled **[{p_d1}, {p_d2}] = {p_total}** vs Thanatos' **[{t_d1}, {t_d2}] = {t_total}**.\n" \
                     f"**VICTORY!**{crit_msg} You won **+{winnings:,.0f} Obols** (x{multiplier:.0f})!", player
    elif p_total == t_total:
        save_player(player)
        return True, f"🎲 Both rolled **{p_total}**. Push! Wager of {wager:,.0f} Obols returned.", player
    else:
        player["obols"] -= wager
        save_player(player)
        return True, f"🎲 You rolled **[{p_d1}, {p_d2}] = {p_total}** vs Thanatos' **[{t_d1}, {t_d2}] = {t_total}**.\n" \
                     f"**DEFEAT.** Lost {wager:,.0f} Obols to the void.", player


def draw_fate_card(user_id: int, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Draws a card from the Moirai (Fate Deck) once every 30 minutes."""
    player = get_player(user_id, username)
    now = time.time()
    cooldown = 900 if equipped(player, "moirai_spindle") else 1800

    last_card = player.get("last_fate_card", 0.0)
    if now - last_card < cooldown:
        rem_min = int((cooldown - (now - last_card)) // 60)
        return False, f"The Moirai are spinning your thread. Next Fate Draw ready in **{rem_min} minutes**.", player

    card = random.choice(FATE_CARDS)
    player["last_fate_card"] = now

    opc, ops = calculate_rates(player["upgrades"], player["prestige"], player.get("artifacts", {}))
    msg = f"🎴 **You drew: {card['name']}**\n_{card['description']}_\n\n"

    if card["type"] == "instant_obols":
        gain = max(500.0, ops * card["value"])
        player["obols"] += gain
        msg += f"Effect: Vaulted **+{gain:,.0f} Obols**!"
    elif card["type"] == "instant_surge":
        player["surge_expires"] = time.time() + SURGE_DURATION_SECONDS
        msg += "Effect: Ignited an instant **Acheron's Wake (15x Multiplier)**!"
    elif card["type"] == "embers_gamble":
        embers = card["value"]
        player["ashen_embers"] = player.get("ashen_embers", 0) + embers
        msg += f"Effect: Received **+{embers} Ashen Embers**!"
    elif card["type"] == "massive_souls":
        gain = max(200.0, opc * card["value"])
        remaining_souls = max(0.0, TOTAL_HUMAN_SOULS - player["total_souls"])
        actual_gain = min(gain, remaining_souls)
        player["total_souls"] += actual_gain
        msg += f"Effect: Delivered **+{actual_gain:,.0f} Human Souls** across the threshold!"

    save_player(player)
    return True, msg, player


def claim_bounty(user_id: int, bounty_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Claims reward for a completed bounty and rolls a new one."""
    player = get_player(user_id, username)
    bounties = player.get("active_bounties", [])

    found_idx = None
    for idx, b in enumerate(bounties):
        if b["id"] == bounty_id:
            found_idx = idx
            break

    if found_idx is None:
        return False, "Decree not found.", player

    target_bounty = bounties[found_idx]
    if target_bounty.get("current", 0) < target_bounty["target"]:
        return False, f"Decree incomplete ({target_bounty.get('current', 0)}/{target_bounty['target']}).", player

    embers = target_bounty["reward_embers"]
    player["ashen_embers"] = player.get("ashen_embers", 0) + embers

    # Replace with a fresh new random bounty template
    unused = [t for t in BOUNTY_TEMPLATES if t["id"] != target_bounty["template_id"]]
    new_t = random.choice(unused if unused else BOUNTY_TEMPLATES)
    bounties[found_idx] = {
        "id": f"{new_t['id']}_{int(time.time())}_{random.randint(100, 999)}",
        "template_id": new_t["id"],
        "title": new_t["title"],
        "desc": new_t["desc"].format(target=new_t["target"]),
        "target": new_t["target"],
        "current": 0,
        "reward_embers": new_t["reward_embers"],
        "type": new_t["type"],
        "claimed": False
    }

    player["active_bounties"] = bounties
    save_player(player)

    return True, f"📜 Claimed +{embers} Ashen Embers for completing {target_bounty['title']}!", player


def buy_artifact(user_id: int, artifact_id: str, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Unlocks a mythic permanent artifact with Ashen Embers."""
    if artifact_id not in MYTHIC_ARTIFACTS:
        return False, "Unknown mythic artifact.", {}

    player = get_player(user_id, username)
    artifacts = player.get("artifacts", {})

    if artifacts.get(artifact_id):
        return False, "You already possess this mythic artifact.", player

    art_info = MYTHIC_ARTIFACTS[artifact_id]
    cost = art_info["cost_embers"]

    if player.get("ashen_embers", 0) < cost:
        return False, f"Requires {cost} Ashen Embers. (You have: {player.get('ashen_embers', 0)})", player

    player["ashen_embers"] -= cost
    artifacts[artifact_id] = True
    player["artifacts"] = artifacts
    save_player(player)

    return True, f"🏆 Bound mythic relic {art_info['name']}! {art_info['description']}", player


def buy_upgrade(user_id: int, upgrade_id: str, username: str = "Ferryman", quantity: int = 1) -> Tuple[bool, str, dict]:
    """Buys specified quantity of upgrade for player."""
    if upgrade_id not in UPGRADES:
        return False, "Invalid upgrade item.", {}

    player = get_player(user_id, username)

    current_qty = player["upgrades"].get(upgrade_id, 0)
    total_cost = 0
    for i in range(quantity):
        total_cost += get_upgrade_cost(upgrade_id, current_qty + i)

    if player["obols"] < total_cost:
        return False, f"Not enough obols! Requires {total_cost:,.0f} Obols.", player

    player["obols"] -= total_cost
    player["upgrades"][upgrade_id] = current_qty + quantity
    save_player(player)

    item_name = UPGRADES[upgrade_id]["name"]
    return True, f"Purchased x{quantity} {item_name} for {total_cost:,.0f} Obols.", player


def claim_daily(user_id: int, username: str = "Ferryman") -> Tuple[bool, str, float, dict]:
    """Claims daily Hades Tribute. 24h cooldown."""
    player = get_player(user_id, username)
    now = time.time()
    last_daily = player.get("last_daily", 0)

    cooldown = 86400  # 24 hours
    if now - last_daily < cooldown:
        remaining = cooldown - (now - last_daily)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return False, f"Daily tribute available in {hours}h {minutes}m.", 0.0, player

    opc, ops = calculate_rates(player["upgrades"], player["prestige"], player.get("artifacts", {}))
    bonus = max(100.0, (opc * 100.0) + (ops * 300.0))

    player["obols"] += bonus
    player["total_souls"] += bonus
    player["last_daily"] = now
    save_player(player)

    return True, f"Claimed the Daily Hades Tribute of {bonus:,.0f} Obols!", bonus, player


def ascend(user_id: int, username: str = "Ferryman") -> Tuple[bool, str, dict]:
    """Prestige once all human souls reached."""
    player = get_player(user_id, username)

    if player["total_souls"] < TOTAL_HUMAN_SOULS:
        return False, f"You must ferry all {config.format_exact(TOTAL_HUMAN_SOULS)} human souls before ascending! (Current: {config.format_exact(player['total_souls'])})", player

    player["prestige"] += 1
    player["total_souls"] = 0.0
    player["obols"] = 0.0
    player["upgrades"] = {}
    player["surge_meter"] = 0.0
    player["surge_expires"] = 0.0
    player["pending_encounter"] = ""
    player["last_update"] = time.time()
    save_player(player)

    return True, f"🏆 CONGRATULATIONS! You have ferried all human souls and ascended to Prestige Level {player['prestige']} (+{(player['prestige']) * 100}% permanent boost)!\nThe shoreline of Acheron replenishes with shades awaiting passage in the new cycle.", player


def reset_player_data(user_id: int, username: str = "Ferryman") -> dict:
    """Completely wipes and resets all player progress (Obols, Souls, Prestige, Embers, Relics, Stats)."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
        conn.commit()
    return get_player(user_id, username)


def get_leaderboard(limit: int = 10) -> List[dict]:
    """Fetches top players by total souls ferried."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, total_souls, obols, prestige, ashen_embers, encounters_completed
            FROM players
            ORDER BY total_souls DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
