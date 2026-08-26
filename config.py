"""
Configuration and constants for Charon Simulator Discord Bot.
Theme: Bleak, solemn, poetic Underworld.
"""

# Total estimated human souls ever lived on Earth (117,182,993,899)
TOTAL_HUMAN_SOULS = 117_182_993_899

# Color Palette (Bleak Obsidian / Ashen Aesthetic)
COLOR_DEFAULT = 0x1F1F24  # Deep Obsidian Void
COLOR_GOLD = 0x9A8C73     # Tarnished Bronze Obols
COLOR_VICTORY = 0x6E1414  # Ashen Blood Crimson
COLOR_ERROR = 0x4A1515    # Dark Iron
COLOR_SURGE = 0x8B0000    # Blood Styx Frenzy
COLOR_ENCOUNTER = 0x4A2E68 # Abyssal Violet
COLOR_MYTHIC = 0x2A52BE   # Olympian Starlight Blue
COLOR_VOYAGE = 0x1A3636   # Murky River Teal

# Styx Surge Configuration
SURGE_CHARGE_PER_ROW = 5.0       # Percent charged per manual stroke
SURGE_THRESHOLD = 100.0          # Max meter to trigger
SURGE_DURATION_SECONDS = 45.0    # Duration of the surge frenzy
SURGE_MULTIPLIER = 15.0          # Multiplier during active surge

# Build-crafting market. Gear is unique: buying a piece binds it and equips it
# into its vessel slot, replacing the previously equipped piece in that slot.
GEAR_SLOTS = ("hull", "oars", "lantern", "figurehead", "crew")
VESSEL_LEVELS = {
    1: "Splintered Skiff", 2: "Pitch-Coated Ferry", 3: "Shade Galley",
    4: "Barge of Wailing", 5: "Iron Mortuary Vessel", 6: "Abyssal Skimmer",
    7: "Dreadnought of Lethe", 8: "Cocytus' Aircraft Carrier", 9: "Hades' Grand Liner",
    10: "The One Ship to Ferry Them All",
}

def vessel_upgrade_cost(level: int) -> tuple[int, int]:
    """Cost to advance from level to level + 1; level 10 is the cap."""
    return 5_000 * (6 ** (level - 1)), 10 * (level ** 2)
RIVER_CURRENTS = (
    {"id": "phlegethon", "name": "Phlegethon Fire Rapids", "icon": "🔥", "favored": "marauder", "penalty": "necromancer", "description": "Marauder gear cuts through the boiling current; fleet engines labour in its heat."},
    {"id": "cocytus", "name": "Cocytus Frost Fog", "icon": "❄️", "favored": "fate", "penalty": "speed", "description": "Fate-weaving pierces the white silence; rhythm is harder to hold."},
    {"id": "lethe", "name": "Lethe Memory Mists", "icon": "🌫️", "favored": "necromancer", "penalty": "marauder", "description": "Bound crews remember their oaths; anomaly hunters lose the trail."},
)

GEAR = {
    # Progression bands: early (hundreds), established (thousands), deep river
    # (millions), and endgame (hundreds of millions to billions).
    "fury_oarlock": {"name": "Fury-Carved Oarlock", "icon": "🌊", "slot": "oars", "archetype": "speed", "cost": 250, "vessel_req": 1, "description": "Rapid strokes build Rhythm Combo, up to 10x manual yield."},
    "bone_diviner_oar": {"name": "Bone-Diviner Oar", "icon": "🎲", "slot": "oars", "archetype": "fate", "cost": 10_000, "description": "12% chance per stroke for a 3x Critical Dice Roll."},
    "siren_bait_net": {"name": "Siren-Bait Net", "icon": "🕸️", "slot": "lantern", "archetype": "marauder", "cost": 250, "description": "Quadruples anomaly chance and doubles ember hauls from river events."},
    "chthonic_overseer": {"name": "Chthonic Overseer", "icon": "💀", "slot": "crew", "archetype": "necromancer", "cost": 250, "description": "A manual stroke inspires shade rowers: +500% passive flow for 10 seconds."},
    "bellowing_drums": {"name": "Bellowing Drums", "icon": "🥁", "slot": "crew", "archetype": "speed", "cost": 25_000_000, "description": "Each stroke during Acheron's Wake extends it by 1 second."},
    "moirai_spindle": {"name": "Moirai Spindle", "icon": "🧵", "slot": "lantern", "archetype": "fate", "cost": 10_000, "description": "Knuckle-bone rewards are 4x; Fate Cards recharge twice as fast."},
    "stygian_harpoon": {"name": "Stygian Harpoon", "icon": "🔱", "slot": "figurehead", "archetype": "marauder", "cost": 250, "description": "Unlocks high-risk extortion against river bosses."},
    "soul_siphon_hull": {"name": "Soul Siphon Hull", "icon": "🛶", "slot": "hull", "archetype": "necromancer", "cost": 250, "description": "Converts 15% of passive souls into instant bonus Obols."},
    "king_hull": {"name": "Hull of the Underworld King", "icon": "👑", "slot": "hull", "archetype": "pact", "cost": 3_000_000_000, "description": "The late-game anchor piece of the Pact of the Underworld King."},
    "king_figurehead": {"name": "Crowned Prow Figurehead", "icon": "⚜️", "slot": "figurehead", "archetype": "pact", "cost": 3_000_000_000, "description": "A multi-billion capstone that completes the Underworld King's Pact."},
    "obsidian_hull": {"name": "Obsidian Keel", "icon": "🪨", "slot": "hull", "archetype": "speed", "cost": 10_000, "description": "A balanced second-tier hull for relentless cadence builds."},
    "leviathan_hull": {"name": "Leviathan Rib Hull", "icon": "🐋", "slot": "hull", "archetype": "marauder", "cost": 500_000, "description": "A deep-river chassis for anomaly hunters."},
    "lethe_hull": {"name": "Lethe Memory Hull", "icon": "🌫️", "slot": "hull", "archetype": "fate", "cost": 25_000_000, "description": "A late hull that favors careful Fate-weaving."},
    "titan_oar": {"name": "Titan's Shoulder Oar", "icon": "⚓", "slot": "oars", "archetype": "marauder", "cost": 500_000, "description": "A heavy third-tier oar for perilous river choices."},
    "lethe_oar": {"name": "Oar of Forgotten Names", "icon": "🪶", "slot": "oars", "archetype": "necromancer", "cost": 25_000_000, "description": "A late oar that channels the tireless dead."},
    "king_oar": {"name": "Scepter-Oar of Hades", "icon": "👑", "slot": "oars", "archetype": "pact", "cost": 3_000_000_000, "description": "An endgame oar fit for an eternal ferryman."},
    "ember_beacon": {"name": "Ember Beacon", "icon": "🔥", "slot": "lantern", "archetype": "speed", "cost": 500_000, "description": "A third-tier beacon that rewards furious rowing."},
    "oracle_lantern": {"name": "Oracle's Star Lantern", "icon": "🔮", "slot": "lantern", "archetype": "necromancer", "cost": 25_000_000, "description": "A late beacon for commanding spectral fleets."},
    "king_lantern": {"name": "Eclipse Lantern", "icon": "🌑", "slot": "lantern", "archetype": "pact", "cost": 3_000_000_000, "description": "An endgame beacon that eclipses mortal sight."},
    "siren_figurehead": {"name": "Siren Prow", "icon": "🧜", "slot": "figurehead", "archetype": "fate", "cost": 10_000, "description": "A second-tier prow that tempts chance and fate."},
    "cerberus_figurehead": {"name": "Cerberus Figurehead", "icon": "🐕", "slot": "figurehead", "archetype": "necromancer", "cost": 500_000, "description": "A third-tier prow that steadies your bound crew."},
    "phlegethon_figurehead": {"name": "Phlegethon Ram", "icon": "🌋", "slot": "figurehead", "archetype": "speed", "cost": 25_000_000, "description": "A late prow that refuses to yield to fire rapids."},
    "soul_crown": {"name": "Crown of a Thousand Shades", "icon": "👻", "slot": "crew", "archetype": "fate", "cost": 10_000, "description": "A second-tier crew complement guided by the Moirai."},
    "argonaut_crew": {"name": "Bound Argonauts", "icon": "🛡️", "slot": "crew", "archetype": "marauder", "cost": 500_000, "description": "A third-tier crew trained for hostile waters."},
    "king_crew": {"name": "Royal Dead Legion", "icon": "⚔️", "slot": "crew", "archetype": "pact", "cost": 3_000_000_000, "description": "An endgame crew complement of Hades' own legion."},
}

# Every component follows the same five-rank vessel gate unless explicitly set.
for _gear in GEAR.values():
    _gear.setdefault("vessel_req", {250: 1, 10_000: 3, 500_000: 5, 25_000_000: 7, 3_000_000_000: 10}[_gear["cost"]])

# Offline gain cap in seconds (max 24 hours = 86,400 seconds)
MAX_OFFLINE_SECONDS = 86400

# Upgrades Catalog (Bleak Mythological Lore)
UPGRADES = {
    "oar": {
        "id": "oar",
        "name": "Splintered Ash Oar",
        "icon": "⸸",
        "type": "opc",
        "base_cost": 15,
        "power": 1,
        "description": "Worn smooth by centuries of desperate palms. +1 Soul / click"
    },
    "skiff": {
        "id": "skiff",
        "name": "Pitch-Coated Skiff",
        "icon": "†",
        "type": "opc",
        "base_cost": 100,
        "power": 5,
        "description": "Reinforced wood to carry the weight of forgotten names. +5 Souls / click"
    },
    "skeleton": {
        "id": "skeleton",
        "name": "Bound Shade Rower",
        "icon": "✦",
        "type": "ops",
        "base_cost": 50,
        "power": 1,
        "description": "A spirit chained to the oarlock, pulling into oblivion. +1 Soul / sec"
    },
    "cerberus": {
        "id": "cerberus",
        "name": "Hound of the Shore",
        "icon": "⸸",
        "type": "ops",
        "base_cost": 250,
        "power": 5,
        "description": "Its three jaws snap at lingering earthly regrets. +5 Souls / sec"
    },
    "sails": {
        "id": "sails",
        "name": "Shroud-Torn Sails",
        "icon": "†",
        "type": "ops",
        "base_cost": 1200,
        "power": 30,
        "description": "Woven from the burial shrouds of forgotten kings. +30 Souls / sec"
    },
    "galley": {
        "id": "galley",
        "name": "Barge of Wailing",
        "icon": "✦",
        "type": "ops",
        "base_cost": 7500,
        "power": 180,
        "description": "A heavy hull echoing with unuttered last words. +180 Souls / sec"
    },
    "steamboat": {
        "id": "steamboat",
        "name": "Iron Mortuary Vessel",
        "icon": "⸸",
        "type": "ops",
        "base_cost": 50000,
        "power": 1000,
        "description": "Choking black soot over silent subterranean waters. +1,000 Souls / sec"
    },
    "hydrofoil": {
        "id": "hydrofoil",
        "name": "Abyssal Skimmer",
        "icon": "†",
        "type": "ops",
        "base_cost": 350000,
        "power": 6500,
        "description": "Gliding soundlessly across deep void currents. +6,500 Souls / sec"
    },
    "hermes": {
        "id": "hermes",
        "name": "Obelisk of Psychopomp",
        "icon": "✦",
        "type": "ops",
        "base_cost": 2500000,
        "power": 45000,
        "description": "Where Hermes surrenders the newly departed. +45,000 Souls / sec"
    },
    "teleporter": {
        "id": "teleporter",
        "name": "Rift of Tartarus",
        "icon": "⸸",
        "type": "ops",
        "base_cost": 20000000,
        "power": 350000,
        "description": "A yawning tear swallowing thousands into the dark. +350,000 Souls / sec"
    },
    "canals": {
        "id": "canals",
        "name": "Aqueducts of Lethe",
        "icon": "†",
        "type": "ops",
        "base_cost": 150000000,
        "power": 2500000,
        "description": "Black waterways carved through bone and ash. +2,500,000 Souls / sec"
    },
    "portal": {
        "id": "portal",
        "name": "The Final Threshold",
        "icon": "✦",
        "type": "ops",
        "base_cost": 1500000000,
        "power": 25000000,
        "description": "The cosmic vortex consuming all of human history. +25,000,000 Souls / sec"
    }
}


def get_upgrade_cost(upgrade_id: str, count: int) -> int:
    """Calculates upgrade cost with exponential 1.15 multiplier."""
    if upgrade_id not in UPGRADES:
        return 0
    base_cost = UPGRADES[upgrade_id]["base_cost"]
    return int(base_cost * (1.15 ** count))


def format_number(n: float | int) -> str:
    """Formats large numbers into human-readable compact notation (e.g. 1.23M, 117.00B)."""
    n = float(n)
    if n < 0:
        return "-" + format_number(-n)
    if n < 1000:
        return f"{int(n):,}" if n.is_integer() else f"{n:,.1f}"
    
    units = ["", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc"]
    unit_index = 0
    while n >= 1000 and unit_index < len(units) - 1:
        n /= 1000.0
        unit_index += 1
        
    return f"{n:.2f} {units[unit_index]}"


def format_exact(n: float | int) -> str:
    """Formats number as integer with commas."""
    return f"{int(n):,}"


def get_progress_bar(souls: float | int, total_goal: float | int = TOTAL_HUMAN_SOULS, length: int = 12) -> str:
    """Generates a dark, minimalist progress bar for Discord embeds."""
    pct = min(1.0, max(0.0, souls / total_goal))
    filled = int(round(pct * length))
    bar = "■" * filled + "□" * (length - filled)
    return f"`[{bar}]` `{pct * 100:.5f}%`"


# ==========================================
# 1. RANDOM RIVER ENCOUNTERS
# ==========================================
ENCOUNTERS = {
    "gilded_king": {
        "id": "gilded_king",
        "title": "👑 The Gilded King of Lydia",
        "icon": "👑",
        "description": "A shade draped in tarnished golden robes clambers aboard, offering a chest overflowing with minted obols in exchange for skipping the eternal wait.",
        "choices": {
            "bribe": {
                "label": "Accept Golden Bribe",
                "desc": "Gain 20 minutes worth of Obols, but lose 5% of souls ferried this cycle.",
                "style": "success"
            },
            "ferry": {
                "label": "Ferry Ethically",
                "desc": "Refuse special treatment. Gain Souls & +10 Ashen Embers.",
                "style": "primary"
            },
            "extort": {
                "label": "Extort the King",
                "desc": "50% chance to claim double gold, 50% chance he curses your oars (brief slowdown).",
                "style": "danger"
            }
        }
    },
    "siren_cocytus": {
        "id": "siren_cocytus",
        "title": "🌊 Siren of the Frozen Cocytus",
        "icon": "🌊",
        "description": "A mournful, ethereal voice echoes across the mist. The lament threatens to freeze the hearts of mortal ferrymen, yet contains forgotten divine secrets.",
        "choices": {
            "listen": {
                "label": "Listen to the Lament",
                "desc": "50% chance to gain instant 5x Surge Frenzy, 50% chance to lose some obols to despair.",
                "style": "danger"
            },
            "plug_ears": {
                "label": "Plug Ears with Wax",
                "desc": "Safely pass the icy banks with a steady mind (+Safe Obols).",
                "style": "secondary"
            },
            "cast_net": {
                "label": "Cast Stygian Net",
                "desc": "Attempt to dredge relics from the icy riverbed (+Ashen Embers).",
                "style": "primary"
            }
        }
    },
    "charybdis_vortex": {
        "id": "charybdis_vortex",
        "title": "🌪️ Maelstrom of Charybdis",
        "icon": "🌪️",
        "description": "The black waters violently swirl into a roaring subterranean whirlpool. Timber groans beneath your feet.",
        "choices": {
            "power_through": {
                "label": "Row with All Might",
                "desc": "Test your stroke power. Success yields massive soul harvest; failure damages vessel.",
                "style": "danger"
            },
            "sacrifice_cargo": {
                "label": "Cast Shrouds to Water",
                "desc": "Sacrifice 10% of current vaulted obols to safely glide out with a Stygian Shard (+25 Embers).",
                "style": "secondary"
            }
        }
    },
    "wandering_shades": {
        "id": "wandering_shades",
        "title": "⚔️ Phalanx of the Fallen",
        "icon": "⚔️",
        "description": "A regiment of Spartan warriors stands locked in formation upon the shore, weapons lowered in solemn salute.",
        "choices": {
            "bless": {
                "label": "Grant Honorable Rest",
                "desc": "Ferry them peacefully into Elysium (+Large Souls Delivered).",
                "style": "primary"
            },
            "conscript": {
                "label": "Bind as Rowers",
                "desc": "Channel their martial strength into permanent +5 Bound Shade Rowers!",
                "style": "success"
            }
        }
    },
    "thanatos_envoy": {
        "id": "thanatos_envoy",
        "title": "⚖️ Envoy of Thanatos",
        "icon": "⚖️",
        "description": "A winged harbinger wrapped in black feathers lands upon the prow with a pair of silver knuckle-bones.",
        "choices": {
            "gamble": {
                "label": "Roll Fate Dice",
                "desc": "Test your luck in an instant roll of the bones.",
                "style": "danger"
            },
            "tribute": {
                "label": "Offer Dark Tribute",
                "desc": "Spend 1,000 Obols to gain +50% Surge meter instantly.",
                "style": "secondary"
            }
        }
    }
}


# ==========================================
# 2. MYTHIC ARTIFACTS
# ==========================================
MYTHIC_ARTIFACTS = {
    "golden_bough": {
        "id": "golden_bough",
        "name": "The Golden Bough",
        "icon": "🌿",
        "description": "A sacred branch glowing with Apollo's starlight. +25% Souls per stroke & +10% River Encounter chance.",
        "opc_bonus": 0.25,
        "ops_bonus": 0.0,
        "cost_embers": 100
    },
    "helm_shadows": {
        "id": "helm_shadows",
        "name": "Helm of Shadow",
        "icon": "👑",
        "description": "Forged by the Cyclopes for Hades. +50% Passive Soul Flow (OPS) & +15s Acheron's Wake duration.",
        "opc_bonus": 0.0,
        "ops_bonus": 0.50,
        "cost_embers": 250
    },
    "coin_damned": {
        "id": "coin_damned",
        "name": "Coin of the Damned",
        "icon": "🪙",
        "description": "An ancient minted Drachma that never tarnishes. +100% Obol yield from all actions.",
        "opc_bonus": 0.50,
        "ops_bonus": 0.50,
        "cost_embers": 400
    },
    "iron_oarlock": {
        "id": "iron_oarlock",
        "name": "Stygian Iron Oarlock",
        "icon": "⚓",
        "description": "Reinforced with the black metal of Tartarus. Doubles Acheron's Wake meter charge rate.",
        "opc_bonus": 0.30,
        "ops_bonus": 0.10,
        "cost_embers": 180
    },
    "scythe_thanatos": {
        "id": "scythe_thanatos",
        "name": "Scythe of Thanatos",
        "icon": "⚔️",
        "description": "A celestial blade cutting earthly tethers. +200% permanent boost to both OPC and OPS.",
        "opc_bonus": 2.0,
        "ops_bonus": 2.0,
        "cost_embers": 1000
    }
}


# ==========================================
# 3. UNDERWORLD VOYAGES & BOSS EXPEDITIONS
# ==========================================
VOYAGES = {
    "acheron": {
        "id": "acheron",
        "name": "The Muddy Straits of Acheron",
        "icon": "🌫️",
        "min_souls": 0,
        "description": "Navigate the shallow marshlands where weeping shades first arrive.",
        "stages": [
            {
                "title": "Stage I: The Fog of Regret",
                "text": "Dense mist obscures the river channel. Shadows whisper your mortal name.",
                "choices": [
                    {"id": "row_blind", "label": "Row Steady into the Fog", "stat": "opc"},
                    {"id": "chant_oath", "label": "Recite the Ferryman's Oath", "stat": "wisdom"}
                ]
            },
            {
                "title": "Stage II: The Shallows of Grievance",
                "text": "Grasping hands rise from the silt, attempting to drag down the skiff.",
                "choices": [
                    {"id": "strike_oar", "label": "Strike with Heavy Oar", "stat": "opc"},
                    {"id": "scatter_obols", "label": "Scatter Bronze Dust", "stat": "wealth"}
                ]
            },
            {
                "title": "Stage III: Guardian Shade",
                "text": "The hulking shade of an ancient champion blocks the channel narrows.",
                "choices": [
                    {"id": "duel", "label": "Sever the Tether", "stat": "opc"},
                    {"id": "intimidate", "label": "Show the Seal of Hades", "stat": "prestige"}
                ]
            }
        ],
        "reward_embers": 30,
        "reward_obols_mult": 150
    },
    "cocytus": {
        "id": "cocytus",
        "name": "The Frozen Gorge of Cocytus",
        "icon": "❄️",
        "min_souls": 50_000,
        "description": "The River of Wailing, frozen into jagged shards of ice and bitter frost.",
        "stages": [
            {
                "title": "Stage I: The Glacial Crevasse",
                "text": "Sheets of black ice threaten to crush the wooden hull.",
                "choices": [
                    {"id": "ram_ice", "label": "Ram Through the Ice", "stat": "opc"},
                    {"id": "steer_current", "label": "Navigate the Deep Trench", "stat": "ops"}
                ]
            },
            {
                "title": "Stage II: The Shivering Choir",
                "text": "Wailing shades clamor aboard, their freezing touch sapping warmth.",
                "choices": [
                    {"id": "ignite_torch", "label": "Brandish Underworld Torch", "stat": "wealth"},
                    {"id": "quicken_pace", "label": "Double Stroke Cadence", "stat": "opc"}
                ]
            },
            {
                "title": "Stage III: Cryo-Wraith of Lament",
                "text": "A towering specter formed of frozen tears descends upon the prow.",
                "choices": [
                    {"id": "shatter_core", "label": "Shatter its Frost Heart", "stat": "opc"},
                    {"id": "absorb_sorrow", "label": "Channel Sorrow into Surge", "stat": "ops"}
                ]
            }
        ],
        "reward_embers": 75,
        "reward_obols_mult": 500
    },
    "phlegethon": {
        "id": "phlegethon",
        "name": "The Boiling Torrent of Phlegethon",
        "icon": "🔥",
        "min_souls": 5_000_000,
        "description": "The River of Fire, carrying liquid brimstone and raging flames.",
        "stages": [
            {
                "title": "Stage I: The Cataracts of Fire",
                "text": "Cascades of molten pitch rain down upon the ferry.",
                "choices": [
                    {"id": "shield_hull", "label": "Raise Ashen Bulwarks", "stat": "wealth"},
                    {"id": "surge_rapids", "label": "Surge Across the Lava Rapids", "stat": "opc"}
                ]
            },
            {
                "title": "Stage II: Cenotaph of Tyrants",
                "text": "Cursed warlords attempt to wrest the steering oar away.",
                "choices": [
                    {"id": "cast_down", "label": "Cast them into the Fire", "stat": "opc"},
                    {"id": "command_authority", "label": "Invoke Divine Mandate", "stat": "prestige"}
                ]
            },
            {
                "title": "Stage III: Flame Centaur General",
                "text": "A blazing warrior wielding an infernal bow stands guarding the basalt bridge.",
                "choices": [
                    {"id": "extinguish", "label": "Smother with Stygian Water", "stat": "ops"},
                    {"id": "overpower", "label": "Overpower with Titan Strength", "stat": "opc"}
                ]
            }
        ],
        "reward_embers": 160,
        "reward_obols_mult": 2500
    }
}

VOYAGE_VESSEL_REQUIREMENTS = {"acheron": 1, "cocytus": 3, "phlegethon": 6}


# ==========================================
# 4. TAROT / FATE CARDS OF THE MOIRAI
# ==========================================
FATE_CARDS = [
    {
        "id": "clotho_gold",
        "name": "🧵 Clotho's Golden Spindle",
        "description": "The spinner draws forth a thread of untarnished gold.",
        "type": "instant_obols",
        "value": 900  # 15 mins worth of OPS
    },
    {
        "id": "lachesis_boon",
        "name": "📏 Lachesis' Long Allotment",
        "description": "The apportioner measures a generous span of divine favor.",
        "type": "instant_surge",
        "value": 100.0  # Instant full surge trigger
    },
    {
        "id": "atropos_shears",
        "name": "✂️ Atropos' Unyielding Shears",
        "description": "The inevitable sister snips a fraying thread.",
        "type": "embers_gamble",
        "value": 40  # Awards +40 Ashen Embers
    },
    {
        "id": "styx_wheel",
        "name": "🎡 The Wheel of Tartarus",
        "description": "The cosmic wheel spins across the void.",
        "type": "massive_souls",
        "value": 500  # 500x OPC souls instantly
    }
]


# ==========================================
# 5. DYNAMIC BOUNTY TEMPLATES
# ==========================================
BOUNTY_TEMPLATES = [
    {
        "id": "bounty_rows",
        "title": "The Master's Cadence",
        "desc": "Row manually {target} times across Acheron.",
        "target": 50,
        "reward_embers": 20,
        "type": "manual_rows"
    },
    {
        "id": "bounty_surge",
        "title": "Rage of the River",
        "desc": "Trigger Acheron's Wake {target} times.",
        "target": 2,
        "reward_embers": 35,
        "type": "surges_triggered"
    },
    {
        "id": "bounty_voyage",
        "title": "Expedition of Valor",
        "desc": "Successfully triumph in an Underworld Voyage.",
        "target": 1,
        "reward_embers": 40,
        "type": "voyages_completed"
    },
    {
        "id": "bounty_encounter",
        "title": "Perils Overcome",
        "desc": "Resolve {target} River Encounters on the Acheron.",
        "target": 3,
        "reward_embers": 25,
        "type": "encounters_resolved"
    },
    {
        "id": "bounty_bones",
        "title": "Fated Gambler",
        "desc": "Wager in {target} games of Knuckle-Bones with Thanatos.",
        "target": 3,
        "reward_embers": 30,
        "type": "gambles_played"
    }
]
