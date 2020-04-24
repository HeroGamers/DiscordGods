import os

# Bot Setup
os.environ["prefix"] = "COMMAND PREFIX HERE"
os.environ["token"] = "TOKEN HERE"
os.environ["botlog"] = "CHANNEL ID FOR LOGS"
os.environ["debugEnabled"] = "True OR False"

# Database Setup
os.environ["db_type"] = "FLAT"  # Either MySQL or Flat (or just leave empty for Flat SQLite)
os.environ["db_user"] = "USERNAME"  # Defaults to root if empty
os.environ["db_pword"] = "PASSWORD"  # Defaults to none if empty
os.environ["db_host"] = "HOST"  # Defaults to localhost if empty
os.environ["db_port"] = "PORT"  # Defaults to 3306

# Bot list API tokens
os.environ["top.gg_token"] = ""
os.environ["discord.bots.gg_token"] = ""
os.environ["discordbotlist.com_token"] = ""
os.environ["bots.ondiscord.xyz_token"] = ""
