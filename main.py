#!/usr/bin/env python3
# MasterClipper - MVP bot: counts clip links and assigns milestone roles.
# Requirements: discord.py (2.x)

import os
import re
import sys
import time
import json
import sqlite3
import hashlib
from datetime import datetime, timezone, date

import discord

# ---------------------------
# Configuration (env + defaults)
# ---------------------------

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

# Comma-separated channel names to track (e.g., "clips,highlights")
CHANNEL_NAMES = [c.strip().lstrip("#") for c in os.getenv("CHANNEL_NAMES", "clips").split(",") if c.strip()]

# Daily limit per user (default 3)
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "3"))

# Cooldown in seconds between counts per user (default 30)
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "30"))

# SQLite database path
DB_PATH = os.getenv("DB_PATH", "clipbot.db")

# Log to console (always) and optionally to file
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Role milestones (stacking). Format: JSON list of objects or use defaults.
# Example env JSON: [{"threshold":5,"role":"Highlight Hunter"},{"threshold":25,"role":"Clip Master"},{"threshold":50,"role":"Legendary Editor"}]
DEFAULT_MILESTONES = [
    {"threshold": 5, "role": "Highlight Hunter"},
    {"threshold": 25, "role": "Clip Master"},
    {"threshold": 50, "role": "Legendary Editor"},
]
try:
    ROLE_MILESTONES = json.loads(os.getenv("ROLE_MILESTONES", ""))  # may raise
    # Basic validation
    if not isinstance(ROLE_MILESTONES, list) or not all(
        isinstance(x, dict) and "threshold" in x and "role" in x for x in ROLE_MILESTONES
    ):
        raise ValueError
except Exception:
    ROLE_MILESTONES = DEFAULT_MILESTONES

# Accepted domains (simple MVP filter)
ACCEPTED_DOMAINS = set(d.strip().lower() for d in os.getenv(
    "ACCEPTED_DOMAINS",
    "kick.com,twitch.tv,youtube.com,youtu.be"
).split(",") if d.strip())

# ---------------------------
# URL detection
# ---------------------------

URL_REGEX = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)

def extract_first_clip_url(text: str):
    """Return the first URL that matches an accepted domain, else None."""
    if not text:
        return None
    for match in URL_REGEX.findall(text):
        try:
            url = match.strip().strip(".,!?)\"]'")
            # very light parse: check domain by splitting
            domain = url.split("//", 1)[1].split("/", 1)[0].lower()
            # strip 'www.'
            if domain.startswith("www."):
                domain = domain[4:]
            # Allow subdomains like m.youtube.com
            base = ".".join(domain.split(".")[-2:]) if domain.count(".") >= 1 else domain
            # Special-case for youtu.be
            if domain == "youtu.be":
                base = "youtu.be"
            if base in ACCEPTED_DOMAINS or domain in ACCEPTED_DOMAINS:
                return url
        except Exception:
            continue
    return None

def url_key(url: str) -> str:
    """Stable hash key for duplicate checking."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

# ---------------------------
# SQLite persistence
# ---------------------------

def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_counts (
        guild_id TEXT NOT NULL,
        user_id  TEXT NOT NULL,
        total_count INTEGER NOT NULL DEFAULT 0,
        day_date TEXT,             -- YYYY-MM-DD
        day_count INTEGER NOT NULL DEFAULT 0,
        last_ts  INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (guild_id, user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        guild_id  TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        message_id TEXT NOT NULL,
        user_id    TEXT NOT NULL,
        url_hash   TEXT NOT NULL,
        url        TEXT NOT NULL,
        ts         INTEGER NOT NULL,
        counted    INTEGER NOT NULL DEFAULT 1,
        UNIQUE (guild_id, user_id, url_hash)
    )
    """)
    conn.commit()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

# ---------------------------
# Logging helpers
# ---------------------------

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(os.path.join(LOG_DIR, "clipbot.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ---------------------------
# Discord client
# ---------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # helpful for role assignment

class MasterClipper(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.conn = get_conn()
        init_db(self.conn)
        # Sorted milestones by threshold
        self.milestones = sorted(ROLE_MILESTONES, key=lambda x: x["threshold"])

    async def on_ready(self):
        log(f"✅ MasterClipper online as {self.user} (ID: {self.user.id})")
        log(f"Tracking channels named: {CHANNEL_NAMES}")
        log(f"Daily limit={DAILY_LIMIT}, cooldown={COOLDOWN_SECONDS}s, accepted domains={sorted(list(ACCEPTED_DOMAINS))}")

    # --------------- message handlers ---------------

    async def on_message(self, message: discord.Message):
        await self._handle_message_like(message, is_edit=False)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # If edits are allowed to count, process the edited content
        await self._handle_message_like(after, is_edit=True)

    async def _handle_message_like(self, message: discord.Message, is_edit: bool):
        try:
            if message.author.bot or not message.guild:
                return

            channel_ok = message.channel.name.lower() in [n.lower() for n in CHANNEL_NAMES]
            if not channel_ok:
                return

            url = extract_first_clip_url(message.content or "")
            if not url:
                return

            g = message.guild
            user = message.author
            now_ts = int(time.time())
            ukey = url_key(url)

            # DB ops
            cur = self.conn.cursor()

            # Duplicate check per-user per-url
            cur.execute("""SELECT 1 FROM messages WHERE guild_id=? AND user_id=? AND url_hash=?""",
                        (str(g.id), str(user.id), ukey))
            if cur.fetchone():
                log(f"↩️ Duplicate URL for user {user} ignored: {url}")
                return

            # Get or create user_counts row
            cur.execute("""SELECT total_count, day_date, day_count, last_ts FROM user_counts WHERE guild_id=? AND user_id=?""",
                        (str(g.id), str(user.id)))
            row = cur.fetchone()
            today = date.today().isoformat()

            if row is None:
                total_count = 0
                day_date = today
                day_count = 0
                last_ts = 0
                cur.execute("""INSERT INTO user_counts (guild_id, user_id, total_count, day_date, day_count, last_ts)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (str(g.id), str(user.id), total_count, day_date, day_count, last_ts))
            else:
                total_count, day_date, day_count, last_ts = row
                # Reset day counters if new day
                if day_date != today:
                    day_date = today
                    day_count = 0

            # Enforce cooldown
            if last_ts and (now_ts - last_ts) < COOLDOWN_SECONDS:
                remaining = COOLDOWN_SECONDS - (now_ts - last_ts)
                log(f"⏱️ Cooldown: user {user} must wait {remaining}s")
                # React with hourglass to indicate cooldown (non-intrusive UX)
                try:
                    await message.add_reaction("⏳")
                except Exception:
                    pass
                # Update stored day_date if we shifted dates
                cur.execute("""UPDATE user_counts SET day_date=? WHERE guild_id=? AND user_id=?""",
                            (day_date, str(g.id), str(user.id)))
                self.conn.commit()
                return

            # Enforce daily limit
            if day_count >= DAILY_LIMIT:
                log(f"🚫 Daily limit reached for user {user} ({DAILY_LIMIT}/day)")
                try:
                    await message.add_reaction("🚫")
                except Exception:
                    pass
                # Ensure day_date persists
                cur.execute("""UPDATE user_counts SET day_date=? WHERE guild_id=? AND user_id=?""",
                            (day_date, str(g.id), str(user.id)))
                self.conn.commit()
                return

            # Count it
            total_count += 1
            day_count += 1
            last_ts = now_ts

            # Save message record
            cur.execute("""INSERT OR IGNORE INTO messages
                           (guild_id, channel_id, message_id, user_id, url_hash, url, ts, counted)
                           VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                        (str(g.id), str(message.channel.id), str(message.id), str(user.id), ukey, url, now_ts))

            # Update user_counts
            cur.execute("""UPDATE user_counts SET total_count=?, day_date=?, day_count=?, last_ts=?
                           WHERE guild_id=? AND user_id=?""",
                        (total_count, day_date, day_count, last_ts, str(g.id), str(user.id)))
            self.conn.commit()

            log(f"✅ Counted clip for {user} | total={total_count}, day={day_count}/{DAILY_LIMIT} | {url}")

            # React to acknowledge
            try:
                await message.add_reaction("✅")
            except Exception:
                pass

            # Check milestones and assign roles
            await self._assign_roles_if_needed(g, user, total_count)

        except Exception as e:
            log(f"❌ Error in handler: {e}")

    async def _assign_roles_if_needed(self, guild: discord.Guild, member: discord.Member, total_count: int):
        # Determine which roles the member should have based on milestones
        needed_roles = [m["role"] for m in self.milestones if total_count >= m["threshold"]]
        if not needed_roles:
            return

        # Map role names to Role objects
        role_by_name = {r.name: r for r in guild.roles}
        to_add = []
        for rname in needed_roles:
            role = role_by_name.get(rname)
            if role and role not in member.roles:
                to_add.append(role)

        if not to_add:
            return

        try:
            await member.add_roles(*to_add, reason=f"MasterClipper milestone (total={total_count})")
            log(f"🎖️ Assigned roles to {member}: {', '.join(r.name for r in to_add)}")
        except discord.Forbidden:
            log("⚠️ Missing permissions to add roles. Ensure bot role is above milestone roles.")
        except Exception as e:
            log(f"❌ Failed to assign roles: {e}")

# ---------------------------
# Entry
# ---------------------------

def main():
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN is not set in environment (.env).", file=sys.stderr)
        sys.exit(1)
    client = MasterClipper()
    client.run(TOKEN)

if __name__ == "__main__":
    main()
