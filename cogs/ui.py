"""
Interactive Discord UI components (Buttons, Dropdown Menus, Embed Generators) for Charon Simulator.
Theme: Bleak, solemn, poetic Underworld.
"""

import discord
import time
import database
import config
from config import (
    UPGRADES, TOTAL_HUMAN_SOULS, ENCOUNTERS, MYTHIC_ARTIFACTS, VOYAGES,
    format_number, get_progress_bar, SURGE_THRESHOLD
)


def create_ferry_embed(player: dict, offline_earned: float = 0.0, click_earned: float = 0.0) -> discord.Embed:
    """Generates a dark, poetic Ferrying embed."""
    user_name = player["username"]
    obols = player["obols"]
    souls = player["total_souls"]
    upgrades = player["upgrades"]
    prestige = player["prestige"]
    artifacts = player.get("artifacts", {})
    surge_active = database.is_surge_active(player)

    opc, ops = database.calculate_rates(upgrades, prestige, artifacts, surge_active)

    color = config.COLOR_SURGE if surge_active else config.COLOR_DEFAULT
    surge_tag = " 🔥" if surge_active else ""

    embed = discord.Embed(
        title=f"Your Ferry Upon the Shores of Acheron {surge_tag}",
        description=f"The fog hangs heavy over black waters. Countless shades linger at the shoreline of **{user_name}**, "
                    f"their eyes vacant, waiting for passage into quiet darkness.",
        color=color
    )

    embed.add_field(name="🪙 Obols Vaulted", value=f"`{format_number(obols)}`", inline=True)
    embed.add_field(name="💀 Souls Delivered", value=f"`{format_number(souls)}` / {format_number(TOTAL_HUMAN_SOULS)}", inline=True)
    embed.add_field(name="🔥 Ashen Embers", value=f"`{player.get('ashen_embers', 0)}`", inline=True)

    rate_text = f"`+{format_number(opc)}` /stroke\n`+{format_number(ops)}` /sec"
    if surge_active:
        rate_text += f"\n*(15x Frenzy)*"
    embed.add_field(name="Passage Rates", value=rate_text, inline=True)

    # Surge Meter Bar
    if surge_active:
        rem_sec = max(0, int(player.get("surge_expires", 0) - time.time()))
        surge_bar = f"🔥 **ACHERON'S WAKE ACTIVE!** `{rem_sec}s remaining`"
    else:
        meter = player.get("surge_meter", 0.0)
        pct = min(1.0, max(0.0, meter / SURGE_THRESHOLD))
        filled = int(round(pct * 10))
        surge_bar = f"`[{'■'*filled}{'□'*(10-filled)}]` `{meter:.0f}%` (Row to ignite 15x Frenzy)"
    embed.add_field(name="⚡ Acheron's Wake (Fever Meter)", value=surge_bar, inline=True)

    gear_notes = []
    combo = player.get("stats", {}).get("rhythm_combo", 0)
    if combo:
        gear_notes.append(f"🌊 Rhythm Combo: **{combo}x**")
    if time.time() < player.get("stats", {}).get("overseer_expires", 0):
        gear_notes.append("💀 Shade Rowers Inspired: **+500% OPS**")
    if gear_notes:
        embed.add_field(name="Active Build Effects", value=" · ".join(gear_notes), inline=False)

    # Total Souls Progress Bar
    progress_bar = get_progress_bar(souls)
    remaining = max(0, TOTAL_HUMAN_SOULS - souls)
    embed.add_field(
        name=f"{format_number(TOTAL_HUMAN_SOULS)} human souls ferried to afterlife",
        value=f"{progress_bar}\nRemaining: `{config.format_exact(remaining)}` shades awaiting the crossing",
        inline=False
    )

    if souls >= TOTAL_HUMAN_SOULS:
        embed.add_field(
            name="⸸ ALL MORTAL SOULS FERRIED",
            value="The banks of Acheron stand empty. No more human souls remain to be ferried in this cycle.\n"
                  "Use `/ascend` to dissolve into the void and begin a new cycle with permanent prestige!",
            inline=False
        )

    if player.get("pending_encounter"):
        enc_id = player["pending_encounter"]
        enc_title = ENCOUNTERS.get(enc_id, {}).get("title", "A Spectral Anomaly")
        embed.add_field(
            name="⚠️ RIVER ANOMALY DETECTED!",
            value=f"**{enc_title}** has emerged from the dark fog!\nClick **[Engage Encounter]** below to make your decision.",
            inline=False
        )

    status_notes = []
    if souls >= TOTAL_HUMAN_SOULS:
        status_notes.append("The river is quiet. All human history has passed into the shadow.")
    elif click_earned > 0:
        status_notes.append(f"You dip the oar into dark waters. {format_number(click_earned)} souls ferried into shadow.")
    if offline_earned > 0:
        status_notes.append(f"✦ In your absence, the dark currents carried {format_number(offline_earned)} souls across.")

    if status_notes:
        embed.set_footer(text="\n".join(status_notes))
    else:
        embed.set_footer(text="Row the vessel forward to carry them into the dark.")

    return embed


def create_profile_embed(player: dict) -> discord.Embed:
    """Generates a solemn player record card."""
    user_name = player["username"]
    obols = player["obols"]
    souls = player["total_souls"]
    upgrades = player["upgrades"]
    prestige = player["prestige"]
    artifacts = player.get("artifacts", {})
    embers = player.get("ashen_embers", 0)
    encounters = player.get("encounters_completed", 0)

    opc, ops = database.calculate_rates(upgrades, prestige, artifacts)

    embed = discord.Embed(
        title=f"{user_name}'s Ferryman Record",
        description="A tally etched into ancient cypress wood, counting the passage of mortals from light into shadow.",
        color=config.COLOR_GOLD
    )

    embed.add_field(name="🪙 Obol Vault", value=f"`{format_number(obols)}`", inline=True)
    embed.add_field(name="💀 Total Souls Ferried", value=f"`{config.format_exact(souls)}` / {config.format_exact(TOTAL_HUMAN_SOULS)}", inline=True)
    embed.add_field(name="🔥 Ashen Embers", value=f"`{embers}`", inline=True)

    embed.add_field(name="Ascension Cycle", value=f"`Prestige {prestige}` (+{prestige * 100}% yield)", inline=True)
    embed.add_field(name="Stroke Power (OPC)", value=f"`+{format_number(opc)}` per stroke", inline=True)
    embed.add_field(name="Abyssal Flow (OPS)", value=f"`+{format_number(ops)}` per second", inline=True)
    
    total_upgrades_owned = sum(upgrades.values())
    unlocked_arts = [MYTHIC_ARTIFACTS[a]["name"] for a, v in artifacts.items() if v and a in MYTHIC_ARTIFACTS]
    arts_str = ", ".join(unlocked_arts) if unlocked_arts else "None bound"

    embed.add_field(name="Bound Relics", value=f"`{total_upgrades_owned}` upgrades", inline=True)
    embed.add_field(name="River Encounters Overcome", value=f"`{encounters}` perils", inline=True)
    embed.add_field(name="Mythic Artifacts", value=f"{arts_str}", inline=False)

    progress_bar = get_progress_bar(souls)
    embed.add_field(
        name=f"The Great Threshold ({config.format_exact(TOTAL_HUMAN_SOULS)} Souls)",
        value=f"{progress_bar}",
        inline=False
    )
    return embed


def create_leaderboard_embed(player: dict) -> discord.Embed:
    """Generates server leaderboard and profile embed."""
    top_players = database.get_leaderboard(10)
    
    embed = discord.Embed(
        title="⸸ Ferryman Leaderboard",
        description="Tally of ferrymen who have carried the most human souls into eternal dark:\n"
                    f"Goal: `{config.format_exact(TOTAL_HUMAN_SOULS)}` ({config.format_number(TOTAL_HUMAN_SOULS)}) human souls.",
        color=config.COLOR_DEFAULT
    )

    ranks = ["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX.", "X."]
    lb_text = []

    if not top_players:
        lb_text.append("The shores are silent. No souls have been ferried yet.")
    else:
        for idx, p in enumerate(top_players, 0):
            prefix = f"`{ranks[idx]}`" if idx < len(ranks) else f"`#{idx+1}`"
            souls_str = format_number(p["total_souls"])
            prestige_str = f" — Prestige `{p['prestige']}`" if p['prestige'] > 0 else ""
            embers_str = f" — `{p.get('ashen_embers', 0)}` embers" if p.get('ashen_embers', 0) > 0 else ""
            lb_text.append(f"{prefix} **{p['username']}**{prestige_str}{embers_str} — `{souls_str}` souls")

    embed.add_field(name="Top Ferrymen", value="\n".join(lb_text), inline=False)

    # Personal Summary
    obols = player["obols"]
    souls = player["total_souls"]
    prestige = player["prestige"]
    embers = player.get("ashen_embers", 0)
    opc, ops = database.calculate_rates(player["upgrades"], prestige, player.get("artifacts", {}))

    progress_bar = get_progress_bar(souls)
    embed.add_field(
        name=f"Your Record",
        value=f"🪙 Vault: `{format_number(obols)}` | 💀 Delivered: `{format_number(souls)}`\n"
              f"🔥 Embers: `{embers}` | 🏆 Prestige: `{prestige}` (+{prestige*100}% boost)\n"
              f"⚡ Stroke: `+{format_number(opc)}` | Flow: `+{format_number(ops)}`/s\n"
              f"Progress: {progress_bar}",
        inline=False
    )

    return embed


def create_encounter_embed(player: dict, encounter_id: str) -> discord.Embed:
    """Generates River Encounter embed."""
    enc = ENCOUNTERS[encounter_id]
    embed = discord.Embed(
        title=f"⚠️ River Anomaly: {enc['title']}",
        description=f"{enc['description']}\n\n**Choose your Underworld response:**",
        color=config.COLOR_ENCOUNTER
    )
    for choice_id, cdata in enc["choices"].items():
        if choice_id == "extort" and not database.equipped(player, "stygian_harpoon"):
            continue
        embed.add_field(
            name=f"• {cdata['label']}",
            value=f"_{cdata['desc']}_",
            inline=False
        )
    return embed


def create_shop_embed(player: dict, selected_item_id: str = None) -> discord.Embed:
    """Generates the build-crafting vessel forge."""
    obols = player["obols"]
    equipment = player.get("equipment", {})
    owned = player.get("owned_gear", [])
    current = database.current_river()
    vessel_rank = database.vessel_level(player)
    vessel_name = config.VESSEL_LEVELS[vessel_rank]

    embed = discord.Embed(
        title="⸸ Vessel Forge & Synergy Market",
        description=f"🪙 Vaulted Obols: `{format_number(obols)}`\n"
                    f"{current['icon']} **Current: {current['name']}**\n_{current['description']}_",
        color=config.COLOR_DEFAULT
    )

    loadout = []
    for slot in config.GEAR_SLOTS:
        gear_id = equipment.get(slot)
        loadout.append(f"**{slot.title()}**: {config.GEAR[gear_id]['name'] if gear_id in config.GEAR else 'Empty'}")
    pacts = database.get_active_pacts(player)
    embed.add_field(name="🛶 Equipped Vessel", value="\n".join(loadout) + (f"\n\n✨ **{', '.join(pacts)}** — 5x Frenzy duration" if pacts else "\n\n_Equip matching relics to awaken Ancient Pacts._"), inline=False)
    next_refit = "**MAX RANK — colossal Underworld cruise ship**" if vessel_rank >= 10 else f"Next refit: `{format_number(config.vessel_upgrade_cost(vessel_rank)[0])}` Obols + `{config.vessel_upgrade_cost(vessel_rank)[1]}` Embers"
    embed.add_field(name=f"⛴️ Vessel Rank {vessel_rank}/10 · {vessel_name}", value=f"{next_refit}\nHigher ranks unlock the matching gear bands, voyages, and rarer anomalies.", inline=False)

    if selected_item_id and selected_item_id in config.GEAR:
        item = config.GEAR[selected_item_id]
        is_owned = selected_item_id in owned
        status = "**BOUND** — choose Equip" if is_owned else f"**Forge Cost:** `{format_number(item['cost'])}` Obols"
        modifier = player.get("stats", {}).get("gear_mods", {}).get(selected_item_id)
        level = player.get("stats", {}).get("gear_levels", {}).get(selected_item_id, 0)
        next_upgrade = 10 * (level + 1) ** 2 if level < 10 else None

        embed.add_field(
            name=f"{item['icon']} {item['name']} · {item['archetype'].title()} {status}",
            value=f"_Slot: {item['slot'].title()} · Vessel Rank {item['vessel_req']}_\n{item['description']}\n\n⬆️ Level: **{level}/10**" + (f" · next: `{next_upgrade}` Embers" if next_upgrade else " · **MAX**") + (f"\n🔥 Soulfire modifier: **+{modifier:.0%} stroke yield**" if modifier else "\n🔥 Transmute for 25 Embers to roll a +10–30% stroke modifier."),
            inline=False
        )
    else:
        for slot in config.GEAR_SLOTS:
            forge_lines = [f"{item['icon']} **{item['name']}** · {item['archetype'].title()} · `{format_number(item['cost'])}`" for item in config.GEAR.values() if item['slot'] == slot]
            embed.add_field(name=f"{slot.title()} Components", value="\n".join(forge_lines), inline=False)

    return embed


def create_voyage_embed(player: dict, voyage_id: str = None) -> discord.Embed:
    """Generates Underworld Voyage expedition embed."""
    active = player.get("active_voyage", {})
    if not active or "voyage_id" not in active:
        embed = discord.Embed(
            title="🗺️ Underworld River Expeditions",
            description="Depart the safe shoreline on perilous journeys down the legendary rivers of Hades.\n"
                        "Overcome mythical guardians to claim **Ashen Embers** and heaps of Obols.",
            color=config.COLOR_VOYAGE
        )
        for v_id, v in VOYAGES.items():
            rank_req = config.VOYAGE_VESSEL_REQUIREMENTS.get(v_id, 1)
            req_met = "✅ Ready" if player["total_souls"] >= v["min_souls"] and database.vessel_level(player) >= rank_req else f"🔒 Requires {format_number(v['min_souls'])} souls & Vessel Rank {rank_req}"
            embed.add_field(
                name=f"{v['icon']} {v['name']} ({req_met})",
                value=f"_{v['description']}_\nRewards: `+{v['reward_embers']} Embers` | Stages: `{len(v['stages'])}`",
                inline=False
            )
        return embed

    v_id = active["voyage_id"]
    v_cfg = VOYAGES[v_id]
    stage_idx = active["stage"]
    stage = v_cfg["stages"][stage_idx]

    embed = discord.Embed(
        title=f"🗺️ Expedition: {v_cfg['name']} ({stage_idx + 1}/{len(v_cfg['stages'])})",
        description=f"**{stage['title']}**\n\n{stage['text']}",
        color=config.COLOR_VOYAGE
    )
    for c in stage["choices"]:
        embed.add_field(
            name=f"• {c['label']}",
            value=f"Tactical Focus: `{c['stat'].upper()}`",
            inline=True
        )
    return embed


def create_gamble_embed(player: dict, result_msg: str = None) -> discord.Embed:
    """Generates Knuckle-Bones and Fate Cards embed."""
    obols = player["obols"]
    fate_cooldown = database.fate_card_cooldown(player)
    fate_remaining = max(0.0, fate_cooldown - (time.time() - player.get("last_fate_card", 0.0)))
    fate_status = "**Ready now**" if fate_remaining == 0 else f"Ready in **{int((fate_remaining + 59) // 60)} minutes**"
    embed = discord.Embed(
        title="🎲 Thanatos' Knuckle-Bones & The Loom of Fate",
        description=f"🪙 Vaulted Obols: `{format_number(obols)}`\n"
                    f"Roll the knuckle-bones of fallen heroes with Thanatos, or draw a card from the Moirai.",
        color=config.COLOR_DEFAULT
    )
    embed.add_field(
        name="🎲 Knuckle-Bones Rules",
        value="• Roll 2d6 vs Thanatos' 2d6.\n"
              "• Highest total wins **2x** wager.\n"
              "• Rolling Doubles on victory awards **3x CRIT** payout!",
        inline=True
    )
    embed.add_field(
        name="🎴 The Three Fates (Tarot)",
        value="• Draw from Clotho, Lachesis, & Atropos.\n"
              f"• Free draw every `{fate_cooldown // 60}` minutes for instant surges, obols, or embers.\n"
              f"• {fate_status}",
        inline=True
    )

    if result_msg:
        embed.add_field(name="📜 Outcome", value=result_msg, inline=False)

    return embed


def create_bounty_embed(player: dict, result_msg: str = None) -> discord.Embed:
    """Generates Hades' Decrees & Bounties embed."""
    bounties = player.get("active_bounties", [])
    embers = player.get("ashen_embers", 0)

    embed = discord.Embed(
        title="📜 Royal Decrees of Hades",
        description=f"🔥 Ashen Embers: `{embers}`\n"
                    f"Complete divine decrees to earn Ashen Embers, which can be spent on Mythic Artifacts.",
        color=config.COLOR_GOLD
    )

    for idx, b in enumerate(bounties, 1):
        cur = b.get("current", 0)
        tgt = b["target"]
        pct = min(1.0, cur / tgt)
        filled = int(round(pct * 8))
        bar = f"`[{'■'*filled}{'□'*(8-filled)}]` `{cur}/{tgt}`"
        status = "✨ **COMPLETED!**" if cur >= tgt else bar
        embed.add_field(
            name=f"{idx}. {b['title']} (+{b['reward_embers']} Embers)",
            value=f"{b['desc']}\nProgress: {status}",
            inline=False
        )

    if result_msg:
        embed.set_footer(text=result_msg)

    return embed


def create_artifacts_embed(player: dict, result_msg: str = None) -> discord.Embed:
    """Generates Mythic Reliquary embed."""
    embers = player.get("ashen_embers", 0)
    owned = player.get("artifacts", {})

    embed = discord.Embed(
        title="🏛️ Sanctuary of Mythic Relics",
        description=f"🔥 Available Ashen Embers: `{embers}`\n"
                    f"Surrender Ashen Embers earned from decrees and voyages to forge permanent divine blessings.",
        color=config.COLOR_MYTHIC
    )

    for art_id, art in MYTHIC_ARTIFACTS.items():
        is_owned = owned.get(art_id, False)
        status = "✨ **BOUND TO VESSEL**" if is_owned else f"Cost: `{art['cost_embers']} Embers`"
        embed.add_field(
            name=f"{art['icon']} {art['name']} ({status})",
            value=f"_{art['description']}_",
            inline=False
        )

    if result_msg:
        embed.set_footer(text=result_msg)

    return embed


class RealmSelect(discord.ui.Select):
    """Dropdown for navigating between all game realms."""

    def __init__(self, dashboard: "CharonDashboardView", current_realm: str = "river"):
        self.dashboard = dashboard
        options = [
            discord.SelectOption(label="Shore of Acheron", value="river", emoji="🌊", description="Row manually, build Acheron's Wake, face river perils.", default=(current_realm=="river")),
            discord.SelectOption(label="Market of the Dead", value="shop", emoji="🛒", description="Acquire skiffs, sails, and bind shade rowers.", default=(current_realm=="shop")),
            discord.SelectOption(label="Underworld Expeditions", value="voyages", emoji="🗺️", description="Depart on multi-stage river voyages & boss trials.", default=(current_realm=="voyages")),
            discord.SelectOption(label="Thanatos' Loom & Bones", value="gamble", emoji="🎲", description="Roll knuckle-bones & draw cards from the Moirai.", default=(current_realm=="gamble")),
            discord.SelectOption(label="Royal Decrees of Hades", value="bounties", emoji="📜", description="View and claim active contracts for Ashen Embers.", default=(current_realm=="bounties")),
            discord.SelectOption(label="Sanctuary of Mythic Relics", value="artifacts", emoji="🏛️", description="Bind permanent celestial artifacts with Embers.", default=(current_realm=="artifacts")),
            discord.SelectOption(label="Ferryman Record & Rankings", value="profile", emoji="📊", description="View personal stats, rankings & claim daily tribute.", default=(current_realm=="profile"))
        ]
        super().__init__(placeholder="Navigate Underworld Realm...", min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        dashboard = self.dashboard or self.view
        if not dashboard:
            dashboard = CharonDashboardView(interaction.user.id, "river")

        if interaction.user.id != dashboard.user_id:
            await interaction.response.send_message("This helm belongs to another Ferryman. Use `/charon` to open your own.", ephemeral=True)
            return

        realm = self.values[0] if self.values else "river"
        dashboard.current_realm = realm
        dashboard.status_footer = None
        dashboard.build_ui()
        embed = dashboard.get_embed()
        await interaction.response.edit_message(embed=embed, view=dashboard)


class CharonDashboardView(discord.ui.View):
    """The master all-in-one unified dashboard view for Charon Simulator."""

    def __init__(self, user_id: int, initial_realm: str = "river"):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.current_realm = initial_realm
        self.selected_shop_item = None
        self.selected_shop_slot = "hull"
        self.status_footer = None
        self.build_ui()

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        """Catches and responds to interaction errors to avoid timeouts."""
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"⚠️ An underworld ripple occurred: `{error}`. Type `/charon` to open a fresh helm.", ephemeral=True)
            else:
                await interaction.followup.send(f"⚠️ An underworld ripple occurred: `{error}`. Type `/charon` to open a fresh helm.", ephemeral=True)
        except Exception:
            pass

    def get_embed(self) -> discord.Embed:
        player = database.get_player(self.user_id)
        
        if self.current_realm == "river":
            embed = create_ferry_embed(player)
        elif self.current_realm == "shop":
            embed = create_shop_embed(player, self.selected_shop_item)
        elif self.current_realm == "voyages":
            embed = create_voyage_embed(player)
        elif self.current_realm == "gamble":
            embed = create_gamble_embed(player, self.status_footer)
        elif self.current_realm == "bounties":
            embed = create_bounty_embed(player, self.status_footer)
        elif self.current_realm == "artifacts":
            embed = create_artifacts_embed(player, self.status_footer)
        elif self.current_realm == "profile":
            embed = create_leaderboard_embed(player)
        else:
            embed = create_ferry_embed(player)

        if self.status_footer and self.current_realm not in ("gamble", "bounties", "artifacts"):
            embed.set_footer(text=self.status_footer)
        
        return embed

    def build_ui(self):
        self.clear_items()
        player = database.get_player(self.user_id)

        # Row 0: Realm Navigator
        self.add_item(RealmSelect(self, self.current_realm))

        # Rows 1+: Page Actions
        if self.current_realm == "river":
            self._build_river_actions(player)
        elif self.current_realm == "shop":
            self._build_shop_actions(player)
        elif self.current_realm == "voyages":
            self._build_voyages_actions(player)
        elif self.current_realm == "gamble":
            self._build_gamble_actions(player)
        elif self.current_realm == "bounties":
            self._build_bounties_actions(player)
        elif self.current_realm == "artifacts":
            self._build_artifacts_actions(player)
        elif self.current_realm == "profile":
            self._build_profile_actions(player)

    # 1. River Page Actions
    def _build_river_actions(self, player: dict):
        has_reached_goal = player["total_souls"] >= TOTAL_HUMAN_SOULS
        has_encounter = bool(player.get("pending_encounter"))

        # Row button
        row_btn = discord.ui.Button(
            label="All Souls Ferried" if has_reached_goal else "Row Across",
            style=discord.ButtonStyle.secondary if has_reached_goal else discord.ButtonStyle.primary,
            disabled=has_reached_goal,
            row=1
        )
        row_btn.callback = self._river_row_callback
        self.add_item(row_btn)

        # Encounter button
        enc_btn = discord.ui.Button(
            label="Engage River Anomaly" if has_encounter else "No Anomaly Present",
            style=discord.ButtonStyle.danger if has_encounter else discord.ButtonStyle.secondary,
            disabled=not has_encounter,
            row=1
        )
        enc_btn.callback = self._river_enc_callback
        self.add_item(enc_btn)

        # Ascend button
        asc_btn = discord.ui.Button(
            label="Ascend to Void",
            style=discord.ButtonStyle.success if has_reached_goal else discord.ButtonStyle.secondary,
            disabled=not has_reached_goal,
            row=1
        )
        asc_btn.callback = self._ascend_callback
        self.add_item(asc_btn)

        # Claim Daily
        daily_btn = discord.ui.Button(label="Claim Daily Tribute", style=discord.ButtonStyle.secondary, row=2)
        daily_btn.callback = self._claim_daily_callback
        self.add_item(daily_btn)

    async def _river_row_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
        player, click_earned, offline_earned, surge_trig, new_enc = database.ferry_souls(self.user_id, interaction.user.display_name)
        if surge_trig:
            self.status_footer = "⚡ ACHERON HAS AWAKEN! 15x Frenzy Multiplier active for 45s!"
        elif new_enc:
            self.status_footer = f"⚠️ An anomaly ({ENCOUNTERS[new_enc]['title']}) has appeared on the river!"
        elif player["total_souls"] >= TOTAL_HUMAN_SOULS:
            self.status_footer = "⸸ All mortal souls have been ferried! Click [Ascend to Void] to dissolve."
        else:
            self.status_footer = f"Dipped oar into dark waters. +{format_number(click_earned)} souls ferried."

        self.build_ui()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def _river_enc_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
        player = database.get_player(self.user_id)
        enc_id = player.get("pending_encounter")
        if not enc_id or enc_id not in ENCOUNTERS:
            return await interaction.response.send_message("No river anomaly present.", ephemeral=True)

        view = EncounterView(self.user_id, enc_id, parent_view=self)
        embed = create_encounter_embed(player, enc_id)
        await interaction.response.edit_message(embed=embed, view=view)

    # 2. Shop Page Actions
    def _build_shop_actions(self, player: dict):
        # Five parallel upgrade tracks, one for each vessel part.
        for index, slot in enumerate(config.GEAR_SLOTS):
            btn = discord.ui.Button(label=slot.title(), style=discord.ButtonStyle.primary if self.selected_shop_slot == slot else discord.ButtonStyle.secondary, row=1)
            btn.callback = self._make_slot_callback(slot)
            self.add_item(btn)

        # Dropdown only contains the five choices in the selected track.
        options = []
        owned = player.get("owned_gear", [])
        for item_id, item in config.GEAR.items():
            if item["slot"] != self.selected_shop_slot:
                continue
            status = "Bound" if item_id in owned else f"{format_number(item['cost'])} Obols"
            options.append(discord.SelectOption(
                label=f"{item['name']} ({status})",
                value=item_id,
                description=f"{item['slot'].title()} · {item['archetype'].title()} · {item['description'][:45]}",
                default=(self.selected_shop_item == item_id)
            ))
        select = discord.ui.Select(placeholder=f"Select a {self.selected_shop_slot} component...", options=options, row=2)
        select.callback = self._shop_select_callback
        self.add_item(select)

        forge_btn = discord.ui.Button(label="Forge & Equip", style=discord.ButtonStyle.success, row=3)
        forge_btn.callback = self._make_buy_callback(False)
        self.add_item(forge_btn)
        equip_btn = discord.ui.Button(label="Equip Bound Gear", style=discord.ButtonStyle.secondary, row=3)
        equip_btn.callback = self._make_buy_callback(True)
        self.add_item(equip_btn)
        transmute_btn = discord.ui.Button(label="Transmute (25 Embers)", style=discord.ButtonStyle.danger, row=3)
        transmute_btn.callback = self._make_transmute_callback()
        self.add_item(transmute_btn)
        upgrade_btn = discord.ui.Button(label="Upgrade Bound Gear", style=discord.ButtonStyle.primary, row=3)
        upgrade_btn.callback = self._make_upgrade_callback()
        self.add_item(upgrade_btn)
        vessel_btn = discord.ui.Button(label="Refit Vessel", style=discord.ButtonStyle.success, row=3)
        vessel_btn.callback = self._make_vessel_upgrade_callback()
        self.add_item(vessel_btn)

    def _make_slot_callback(self, slot: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            self.selected_shop_slot = slot
            self.selected_shop_item = None
            self.build_ui()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        return callback

    async def _shop_select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
        self.selected_shop_item = interaction.data["values"][0]
        self.build_ui()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def _make_buy_callback(self, equip: bool):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            if not self.selected_shop_item:
                return await interaction.response.send_message("Select a relic from the dropdown above first.", ephemeral=True)
            action = database.equip_gear if equip else database.buy_gear
            success, msg, player = action(self.user_id, self.selected_shop_item, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    def _make_transmute_callback(self):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            if not self.selected_shop_item:
                return await interaction.response.send_message("Select a bound component first.", ephemeral=True)
            success, msg, player = database.transmute_gear(self.user_id, self.selected_shop_item, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        return callback

    def _make_upgrade_callback(self):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            if not self.selected_shop_item:
                return await interaction.response.send_message("Select a bound component first.", ephemeral=True)
            success, msg, player = database.upgrade_gear(self.user_id, self.selected_shop_item, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        return callback

    def _make_vessel_upgrade_callback(self):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            success, msg, player = database.upgrade_vessel(self.user_id, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        return callback

    # 3. Voyages Page Actions
    def _build_voyages_actions(self, player: dict):
        active = player.get("active_voyage", {})
        if not active or "voyage_id" not in active:
            for v_id, v in VOYAGES.items():
                can_embark = player["total_souls"] >= v["min_souls"] and database.vessel_level(player) >= config.VOYAGE_VESSEL_REQUIREMENTS.get(v_id, 1)
                btn = discord.ui.Button(
                    label=f"Embark: {v['name'][:18]}",
                    style=discord.ButtonStyle.primary if can_embark else discord.ButtonStyle.secondary,
                    disabled=not can_embark,
                    row=1
                )
                btn.callback = self._make_embark_callback(v_id)
                self.add_item(btn)
        else:
            v_id = active["voyage_id"]
            v_cfg = VOYAGES[v_id]
            stage = v_cfg["stages"][active["stage"]]
            for c in stage["choices"]:
                btn = discord.ui.Button(label=c["label"], style=discord.ButtonStyle.primary, row=1)
                btn.callback = self._make_stage_choice_callback(c["id"])
                self.add_item(btn)

    def _make_embark_callback(self, voyage_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            success, msg, player = database.start_voyage(self.user_id, voyage_id, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    def _make_stage_choice_callback(self, choice_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            success, msg, player, completed = database.choose_voyage_action(self.user_id, choice_id, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    # 4. Gamble Actions
    def _build_gamble_actions(self, player: dict):
        for wager in [100, 1000, 10000, 100000]:
            btn = discord.ui.Button(label=f"Roll {format_number(wager)}", style=discord.ButtonStyle.secondary, row=1)
            btn.callback = self._make_roll_callback(wager)
            self.add_item(btn)

        fate_btn = discord.ui.Button(label="🎴 Draw Fate Card (Moirai)", style=discord.ButtonStyle.primary, row=2)
        fate_btn.callback = self._fate_draw_callback
        self.add_item(fate_btn)

    def _make_roll_callback(self, wager: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            success, msg, player = database.roll_knucklebones(self.user_id, wager, interaction.user.display_name)
            self.status_footer = msg
            embed = create_gamble_embed(player, self.status_footer)
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _fate_draw_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
        success, msg, player = database.draw_fate_card(self.user_id, interaction.user.display_name)
        self.status_footer = msg
        embed = create_gamble_embed(player, self.status_footer)
        await interaction.response.edit_message(embed=embed, view=self)

    # 5. Bounties Actions
    def _build_bounties_actions(self, player: dict):
        bounties = player.get("active_bounties", [])
        for idx, b in enumerate(bounties, 1):
            can_claim = b.get("current", 0) >= b["target"]
            btn = discord.ui.Button(
                label=f"Claim Decree #{idx}",
                style=discord.ButtonStyle.success if can_claim else discord.ButtonStyle.secondary,
                disabled=not can_claim,
                row=1
            )
            btn.callback = self._make_claim_bounty_callback(b["id"])
            self.add_item(btn)

    def _make_claim_bounty_callback(self, bounty_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            success, msg, player = database.claim_bounty(self.user_id, bounty_id, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            embed = create_bounty_embed(player, self.status_footer)
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    # 6. Artifacts Actions
    def _build_artifacts_actions(self, player: dict):
        embers = player.get("ashen_embers", 0)
        owned = player.get("artifacts", {})
        for art_id, art in MYTHIC_ARTIFACTS.items():
            is_owned = owned.get(art_id, False)
            can_afford = embers >= art["cost_embers"] and not is_owned
            btn = discord.ui.Button(
                label=f"{art['name'][:16]} ({art['cost_embers']} E)",
                style=discord.ButtonStyle.primary if can_afford else discord.ButtonStyle.secondary,
                disabled=is_owned or not can_afford,
                row=1 if len(self.children) < 5 else 2
            )
            btn.callback = self._make_buy_artifact_callback(art_id)
            self.add_item(btn)

    def _make_buy_artifact_callback(self, art_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
            success, msg, player = database.buy_artifact(self.user_id, art_id, interaction.user.display_name)
            self.status_footer = msg
            self.build_ui()
            embed = create_artifacts_embed(player, self.status_footer)
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    # 7. Profile Actions
    def _build_profile_actions(self, player: dict):
        has_reached_goal = player["total_souls"] >= TOTAL_HUMAN_SOULS
        daily_btn = discord.ui.Button(label="Claim Daily Tribute", style=discord.ButtonStyle.primary, row=1)
        daily_btn.callback = self._claim_daily_callback
        self.add_item(daily_btn)

        asc_btn = discord.ui.Button(
            label="Ascend to Void",
            style=discord.ButtonStyle.success if has_reached_goal else discord.ButtonStyle.secondary,
            disabled=not has_reached_goal,
            row=1
        )
        asc_btn.callback = self._ascend_callback
        self.add_item(asc_btn)

        reset_btn = discord.ui.Button(label="Reset All Data", style=discord.ButtonStyle.danger, row=1)
        reset_btn.callback = self._reset_prompt_callback
        self.add_item(reset_btn)

    async def _claim_daily_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
        success, msg, bonus, player = database.claim_daily(self.user_id, interaction.user.display_name)
        self.status_footer = msg
        self.build_ui()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def _ascend_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)
        success, msg, player = database.ascend(self.user_id, interaction.user.display_name)
        self.status_footer = msg
        self.build_ui()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def _reset_prompt_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Use `/charon` to open your own helm.", ephemeral=True)

        view = ResetConfirmationView(self.user_id, parent_view=self)
        embed = discord.Embed(
            title="💀 A Complete and Utter Destruction of the Ferryman",
            description="Are you certain you wish to dissolve all your progress into the eternal void?\n\n"
                        "• All **Obols** & **Souls Delivered** will be wiped to `0`.\n"
                        "• All **Prestige Levels** & **Permanent Boosts** will be reset to `0`.\n"
                        "• All **Ashen Embers** & **Mythic Artifacts** will be revoked.\n"
                        "• All **Vessels, Oars, & Shade Rowers** will be dissolved.\n\n"
                        "**This action is permanent and cannot be undone.**",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=view)


class ResetConfirmationView(discord.ui.View):
    """Confirmation prompt before obliterating player data."""

    def __init__(self, user_id: int, parent_view: CharonDashboardView):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.parent_view = parent_view

    @discord.ui.button(label="Confirm Wipe & Reset Data", style=discord.ButtonStyle.danger, row=0)
    async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This record belongs to another Ferryman.", ephemeral=True)

        database.reset_player_data(self.user_id, interaction.user.display_name)
        self.parent_view.current_realm = "river"
        self.parent_view.status_footer = "All records dissolved into the void. You stand once more at the beginning of Acheron."
        self.parent_view.build_ui()
        embed = self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, row=0)
    async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This record belongs to another Ferryman.", ephemeral=True)

        self.parent_view.status_footer = "Obliteration cancelled. Your record remains intact."
        self.parent_view.build_ui()
        embed = self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class EncounterView(discord.ui.View):
    """View for making an immediate decision on a river encounter."""

    def __init__(self, user_id: int, encounter_id: str, parent_view: CharonDashboardView = None):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.encounter_id = encounter_id
        self.parent_view = parent_view

        enc = ENCOUNTERS[encounter_id]
        player = database.get_player(user_id)
        styles = {
            "primary": discord.ButtonStyle.primary,
            "success": discord.ButtonStyle.success,
            "danger": discord.ButtonStyle.danger,
            "secondary": discord.ButtonStyle.secondary
        }

        for choice_id, cdata in enc["choices"].items():
            if choice_id == "extort" and not database.equipped(player, "stygian_harpoon"):
                continue
            btn = discord.ui.Button(
                label=cdata["label"],
                style=styles.get(cdata.get("style"), discord.ButtonStyle.secondary),
                custom_id=f"enc_{choice_id}"
            )
            btn.callback = self._make_choice_callback(choice_id)
            self.add_item(btn)

    def _make_choice_callback(self, choice_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This river anomaly belongs to another Ferryman.", ephemeral=True)
                return

            success, msg, player = database.resolve_encounter(
                interaction.user.id, self.encounter_id, choice_id, interaction.user.display_name
            )

            dashboard = self.parent_view or CharonDashboardView(self.user_id, "river")
            dashboard.status_footer = msg
            dashboard.build_ui()
            embed = dashboard.get_embed()
            await interaction.response.edit_message(embed=embed, view=dashboard)

        return callback


# Aliases for backwards-compatibility
FerryView = CharonDashboardView
ShopView = CharonDashboardView
VoyageView = CharonDashboardView
BonesGambleView = CharonDashboardView
BountyView = CharonDashboardView
ArtifactsView = CharonDashboardView
