# Charon Simulator

> *"Mankind is dead.*  
> *The shore is full.*  
> *Ferry them all."*

**Charon Simulator** is an interactive Discord idle/incremental game bot. Players take the helm of **Charon**, legendary ferryman of Hades. Your solemn duty is to ferry every mortal soul across the black waters of Acheron for 1 Obol each, buying mythological upgrades, overcoming river anomalies, venturing into deep river expeditions, and gambling with Thanatos until you have delivered all **117,182,993,899 human souls** who have ever lived.

---

## 🌟 Key Features

- **Master Underworld Helm (`/charon`)**: A single, unified interactive dashboard. Seamlessly switch between all Underworld realms via the built-in Realm Navigator dropdown!
- **🌊 Shore of Acheron**: Manual rhythmic rowing with **Styx Surge (15x Frenzy)** and branching **River Encounters** (The Gilded King, Sirens, Whirlpools).
- **🛒 Market of the Dead**: Forge black skiffs, cypress oars, and bind shade rowers to increase manual stroke power and passive income.
- **🗺️ River Expeditions**: Embark on 3-stage tactical voyages across Acheron, Cocytus, and Phlegethon to defeat river guardians and earn **Ashen Embers**.
- **🎲 Thanatos' Loom & Bones**: Wager obols in 2d6 Knuckle-Bones (with 3x Doubles Crits) and draw tarot Fate cards from the Moirai.
- **📜 Royal Decrees of Hades**: Complete active contracts and earn Ashen Embers.
- **🏛️ Sanctuary of Mythic Relics**: Bind permanent celestial artifacts (*The Golden Bough*, *Helm of Shadow*, *Coin of the Damned*).
- **📊 Ferryman Record & Rankings**: Real-time progress bar toward 117 Billion souls and server Top 10 leaderboards.
- **Anti-Flood Engine**: Automatically deletes triggering text commands and updates responses in-place to keep your Discord channels clean.

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- **Python 3.10+** installed.
- Dependencies (`discord.py`, `python-dotenv`).

```bash
pip install -r requirements.txt
```

---

### 2. Create a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application**, name it **Charon Simulator**, and click **Create**.
3. In the left menu, click **Bot**.
4. Click **Reset Token** to copy your bot token.
5. Under **Privileged Gateway Intents**, enable **MESSAGE CONTENT INTENT** and click **Save Changes**.

---

### 3. Invite the Bot to Your Server

1. In the Discord Developer Portal, go to **OAuth2** -> **URL Generator**.
2. Select scopes: `bot` and `applications.commands`.
3. Select Bot Permissions:
   - `Send Messages`
   - `Embed Links`
   - `Manage Messages` (for auto-cleaning command triggers)
   - `Read Message History`
4. Open the generated URL in your browser to invite the bot to your server.

---

### 4. Configure Environment Variables

Create a `.env` file in the root folder (or copy from `.env.example`):

```env
DISCORD_TOKEN=your_actual_discord_bot_token_here
COMMAND_PREFIX=!
```

---

### 5. Run the Bot

Launch Charon Simulator:

```bash
python bot.py
```

---

## 🎮 How to Play

| Command | Aliases | Description |
| :--- | :--- | :--- |
| `/charon` | `!charon`, `!ferry`, `!game`, `!play` | Open the unified interactive Underworld Helm |

---

## License
MIT License.