# 🎬 MasterClipper Bot

**A simple Discord bot that counts shared clips and rewards users with milestone roles.**

MasterClipper keeps your community fun and active by recognising members who share Kick, Twitch, and YouTube clips.  
Built as a lightweight MVP — easy to run locally, easy to understand, and easy to extend.

---

## 🚀 Features (v0.1 MVP)

- ✅ Counts clip links from **Kick.com**, **Twitch.tv**, and **YouTube.com**
- ✅ Assigns milestone roles automatically:
  - **5 clips:** Highlight Hunter  
  - **25 clips:** Clip Master  
  - **50 clips:** Legendary Editor
- ✅ Users keep all earned roles (stacking progression)
- ✅ Respects daily limits (3 clips per user per day)
- ✅ 30-second cooldown to prevent spam
- ✅ Local logging and simple SQLite storage
- ✅ Manual start/stop — perfect for ad-hoc daily runs

---

## 🧱 Project Structure

```

C:\clipbot
├── main.py
├── requirements.txt
├── .env
├── clipbot.db
├── logs
├── README.md
└── Runbook.md

```

---

## ⚙️ Setup Summary

1. **Create the bot** via [Discord Developer Portal](https://discord.com/developers/applications)
   - Enable **MESSAGE CONTENT INTENT**
   - (Optional) Enable **SERVER MEMBERS INTENT**
   - Copy your **bot token**
2. **Invite the bot** to your server with:
   - View Channels  
   - Read Message History  
   - Send Messages  
   - Manage Roles
3. **Clone this repo** or download the files.
4. **Create `.env` file** with your bot token:
```

DISCORD_TOKEN=your_bot_token_here

````
5. **Install dependencies and run:**
```powershell
cd C:\clipbot
python -m venv venv
.\venv\Scripts\activate
pip install discord.py
python main.py
````

---

## 🪪 Role Hierarchy Reminder

* Bot’s role must be **above** milestone roles (Highlight Hunter, Clip Master, Legendary Editor).
* Create the milestone roles before testing.

---

## 🧩 Configuration Defaults

| Setting                      | Value                            |
| ---------------------------- | -------------------------------- |
| **Tracked Channel**          | #clips                           |
| **Accepted Platforms**       | Kick.com, Twitch.tv, YouTube.com |
| **Duplicate URLs Counted?**  | No                               |
| **Edited Messages Counted?** | Yes                              |
| **Daily Limit per User**     | 3 clips/day                      |
| **Cooldown**                 | 30 seconds                       |
| **Data Store**               | SQLite (local file)              |
| **Logs Folder**              | `C:\clipbot\logs`                |

---

## 🔒 Security Notes

* The `.env` file **must never** be committed or shared publicly.
* If the bot token is exposed, **reset it immediately** in the Discord Developer Portal.
* This project does **not** store message content — only Discord IDs, timestamps, and clip counts.
* Keep the repository **private** unless you intentionally open-source it.

---

## 🧠 Troubleshooting Quick Tips

| Problem                | Likely Cause                    | Fix                                        |
| ---------------------- | ------------------------------- | ------------------------------------------ |
| Bot stays offline      | Wrong token or missing intent   | Check `.env` and Developer Portal settings |
| Bot can’t assign roles | Role hierarchy too low          | Move bot’s role above milestone roles      |
| No clips counted       | Message Content Intent disabled | Enable it in the Developer Portal          |
| Duplicate counts       | URL filter too broad            | Add stricter link validation in code       |

---

## 🗺️ Future Roadmap

| Version  | Planned Features                              |
| -------- | --------------------------------------------- |
| **v0.2** | `/clips me` command, `/clips top` leaderboard |
| **v0.3** | Weekly “Clip of the Week” digest              |
| **v0.4** | Reaction-based quality scoring                |
| **v0.5** | Configurable dashboard or web admin page      |

---

## 👥 Credits

* **Developer:** Spiro
* **Server Owner / Host:** Kick_Clipz (Windows 11)
* **Version:** v0.1
* **Last Updated:** 2025-10-05

---

## 📜 License

This project is intended for **private, non-commercial use** by the Kick_Clipz community.
For open-source or public use, please consult Spiro before redistribution.

---

### ❤️ Thanks for sharing great clips!

MasterClipper exists to make your community more fun — one highlight at a time.

---
