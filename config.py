import os

if not os.environ.get('SHAJESHBOT_TOKEN'):
    from dotenv import load_dotenv
    load_dotenv('.env')

BOT_TOKEN = os.environ['SHAJESHBOT_TOKEN']

MENTION_CH_ID = int(os.environ['MENTION_CHANNEL'])
BOT_CH_ID = int(os.environ['BOT_CHANNEL'])

ADMIN_ID = int(os.environ['ADMIN'])
GUILD_ID = int(os.environ['GUILD'])

PROTECTED_ROLE_IDS = [int(role_id) for role_id in os.environ['PROTECTED_ROLES'].split(',')]
CREW_ROLE_ID = int(os.environ['CREW_ROLE'])

STOCKS_API_KEY = os.environ['STOCKS_API_KEY']
STOCKS_API_BASE_URL = os.environ['STOCKS_API_BASE_URL']
