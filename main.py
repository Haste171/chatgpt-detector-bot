import load
import interactions
import os
from dotenv import load_dotenv
load_dotenv()

token = os.environ.get('BOT_TOKEN')

bot = interactions.Client(token=token)

load.extensions(bot, "cogs")
 
bot.start()