You are Charon, ferryman of the dead, condemned to carry the souls of humanity across the black waters of Acheron. Every passenger pays a single Obol. There are 117,182,993,899 of them. O, the world has ended, Charon. And yet your workload remains. You have a boat, river, and — presumably — an eternity.

So take up your oar, and ferry them all.

# Charon Simulator

An idle/incremental Discord bot game about ferrying the entire dead population of humanity across the rivers of the Underworld.

Row manually. Buy things. Hire dead people to row for you. Upgrade your boat with increasingly unreasonable mythological artifacts. Go on expeditions through the other three rivers of the Underworld. There's more but I'm not adding them all... yet. Oh, and you can gamble all your money away with Thanatos.

Eventually, somehow, ferry all 117,182,993,899 human souls across the river and then... do it all over again. I'm not sure why you would, but you can.

## Play

I've yet to make an official bot for this with all the hosting so please bear with me and run it locally for now.

| Command | Aliases | Description |
| :--- | :--- | :--- |
| `/charon` | `!charon`, `!ferry`, `!game`, `!play` | Open the unified interactive Underworld Helm |

## Setup

### 1. Prerequisites
- **Python 3.10+** installed.
- Dependencies (`discord.py`, `python-dotenv`).

```bash
pip install -r requirements.txt
```

### 2. Create a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application**, name it **Charon Simulator**, and click **Create**.
3. In the left menu, click **Bot**.
4. Click **Reset Token** to copy your bot token.
5. Under **Privileged Gateway Intents**, enable **MESSAGE CONTENT INTENT** and click **Save Changes**.

### 3. Invite the Bot to Your Server

1. In the Discord Developer Portal, go to **OAuth2** -> **URL Generator**.
2. Select scopes: `bot` and `applications.commands`.
3. Select Bot Permissions:
   - `Send Messages`
   - `Embed Links`
   - `Manage Messages` (for auto-cleaning command triggers)
   - `Read Message History`
4. Open the generated URL in your browser to invite the bot to your server.

### 4. Configure Environment Variables

Create a `.env` file in the root folder (or copy from `.env.example`):

```env
DISCORD_TOKEN=your_actual_discord_bot_token_here
COMMAND_PREFIX=!
```

### 5. Run the Bot

Launch Charon Simulator!

```bash
py bot.py
```

## License
MIT License. 
