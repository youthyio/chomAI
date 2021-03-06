from dotenv import load_dotenv
import os

load_dotenv()

# SECRETS
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENAI_TOKEN = os.environ.get("OPENAI_TOKEN")
PASSCODE = os.environ.get("PASSCODE")
# BOT CONFIGS
PREFIX = "!"
# Use this for not letting others change avatars
MAGIC_SECRET = "avatarist"

NICKNAMES = {
    'normal' : 'Sister Margaret',
    'hood' : 'Jay ZZZ',
    'bain' : 'Joe Mitchells'
}
