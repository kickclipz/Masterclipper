# 🧭 MasterClipper Bot — Runbook (v0.1)

**Purpose:**  
Run the MasterClipper bot locally to count clips and assign milestone roles on your Discord server.  
This runbook assumes the bot has already been created in the Discord Developer Portal and that you have the token.

---

## ⚙️ 1️⃣ Prerequisites

✅ Windows 11  
✅ Internet connection  
✅ Discord account with **Manage Server** permission  
✅ **Python 3.10 or newer** installed  
✅ **Bot token** ready (from Discord Developer Portal)  
✅ A text editor (Notepad or VS Code recommended)

---

## 🧩 2️⃣ Folder Setup

1. Create a folder for the bot:
```

C:\clipbot

```

2. Inside this folder, you will have:
```

main.py
requirements.txt
.env
clipbot.db   (auto-created)
logs\        (for runtime logs)
README.md
Runbook.md

```

3. (Optional) Add a `.gitignore` file if using GitHub:
```

.env
*.db
**pycache**/
logs/

```

---

## 🔐 3️⃣ Configure the Environment File

1. In `C:\clipbot`, create a new file called `.env`.  
2. Paste your bot token:
```

DISCORD_TOKEN=your_discord_bot_token_here

````
3. Save it as **UTF-8 (no quotes, no spaces)**.  
4. Never share or upload this file.

---

## 🧠 4️⃣ Install Python and Dependencies

1. Download Python from [https://www.python.org/downloads/](https://www.python.org/downloads/)  
2. During installation, check ✅ “Add Python to PATH.”  
3. Open **PowerShell** and create a virtual environment:

```powershell
cd C:\clipbot
python -m venv venv
.\venv\Scripts\activate
````

4. Install dependencies:

   ```powershell
   pip install discord.py
   ```

---

## 🪪 5️⃣ Invite the Bot to Your Server

1. Go to [Discord Developer Portal](https://discord.com/developers/applications).

2. Select **MasterClipper** → **OAuth2 → URL Generator**.

3. Under **Scopes**, tick:

   * `bot`
   * `applications.commands`

4. Under **Bot Permissions**, tick:

   * View Channels
   * Read Message History
   * Send Messages
   * Manage Roles

5. Copy the generated URL and paste it into your browser.

6. Choose your Discord server and confirm the invite.

7. You should now see the bot (offline) in your server members list.

---

## ▶️ 6️⃣ Running the Bot

1. Open **PowerShell** and navigate to the bot folder:

   ```powershell
   cd C:\clipbot
   .\venv\Scripts\activate
   python main.py
   ```

2. If the setup is correct, you should see:

   ```
   MasterClipper is online and counting clips!
   ```

3. In Discord:

   * Post a Kick, Twitch, or YouTube clip link in **#clips**.
   * The bot should count it.
   * Once thresholds are met (5, 25, 50 clips), it will assign the corresponding role.

---

## 🧰 7️⃣ Basic Commands (for future use)

*(Future updates will add slash commands like `/clips me` or `/clips top`.)*
For now, the bot runs automatically and logs events in console and `logs\` folder.

---

## 🧼 8️⃣ Stopping and Restarting the Bot

* To stop:
  Close the PowerShell window or press **Ctrl + C**.

* To restart:
  Reopen PowerShell, navigate to `C:\clipbot`, activate the virtual environment, and run:

  ```powershell
  python main.py
  ```

---

## 🔒 9️⃣ Security & Maintenance

| Task                     | Frequency | Notes                                   |
| ------------------------ | --------- | --------------------------------------- |
| Rotate Discord bot token | If leaked | Reset token via Developer Portal        |
| Keep repo private        | Always    | No `.env` or `.db` files pushed         |
| Review permissions       | Quarterly | Ensure only required roles are assigned |
| Clear logs               | Optional  | Keep disk clean if run often            |

---

## 🧾 10️⃣ Quick Troubleshooting

| Issue                  | Possible Cause                 | Fix                                   |
| ---------------------- | ------------------------------ | ------------------------------------- |
| Bot stays offline      | Wrong token or missing intents | Check `.env` and Developer Portal     |
| Bot can’t assign roles | Role hierarchy too low         | Move bot’s role above target roles    |
| Bot ignores messages   | Missing Message Content Intent | Enable in Developer Portal            |
| No logs appear         | Missing `logs` folder          | Create manually                       |
| Duplicate counting     | URL filtering not yet enforced | Improve regex or counting rules later |

---

## ✅ 11️⃣ Checklist Summary

☑️ Python installed
☑️ Bot created and token copied
☑️ `.env` file added
☑️ Virtual environment set up
☑️ Dependencies installed
☑️ Bot invited to server
☑️ PowerShell command tested
☑️ Clip counting confirmed

---

**Maintainer:** Spiro
**Host:** Kick_Clipz (Windows 11)
**Version:** v0.1
**Last Updated:** 2025-10-05
**Purpose:** MVP bot to count clips and assign roles — simple, local, fun.

---
