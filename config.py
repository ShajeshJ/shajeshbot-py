import os

BOT_TOKEN = os.environ['SHAJESHBOT_TOKEN']
MENTION_CH_ID = int(os.environ['MENTION_CHANNEL'])
BOT_CH_ID = int(os.environ['BOT_CHANNEL'])
ADMIN_ID = int(os.environ['ADMIN'])
GUILD_ID = int(os.environ['GUILD'])
PROTECTED_ROLE_IDS = [int(role_id) for role_id in os.environ['PROTECTED_ROLES'].split(',')]
CREW_ROLE_ID = int(os.environ['CREW_ROLES'])
