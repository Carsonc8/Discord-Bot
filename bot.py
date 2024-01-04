import datetime, discord, os, disnake, requests
from typing import List, Optional
from discord.components import SelectOption
from discord.utils import MISSING
from discord.ui import Select, View
from discord.ext import commands, tasks
from dataclasses import dataclass
from dotenv import find_dotenv, load_dotenv


#find .env automatically by "walking" up directories until it is found
dotenv_path = find_dotenv()

#load up the entries as enviroment variables
load_dotenv(dotenv_path)

MAX_SESSION_TIME_MINUTES = 1
CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0

#Creates bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
#Creates session
session = Session()

@bot.event
async def on_ready():
    print("The bot is up and running!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced{len(synced)} commands")
    except Exception as e:
        print(e)
    

#name="Hello"
@bot.tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention} This is a slash command!", ephemeral=True)

#Stored as an array so it can take any amount of inputs and then adds them and returns the total
@bot.command()
async def add(ctx, *arr):
    result = 0
    for nums in arr:
        result += int(nums)
    await ctx.send(f"Total Sum = {result}")

#For the Session command which starts a session
@bot.command()
async def start(ctx):
    if session.is_active:
        await ctx.send("A session is already active")
        return  
    
    session.is_active = True
    session.start_time = ctx.message.created_at.timestamp()
    human_readable_time = ctx.message.created_at.strftime("%H:%M:%S")
    break_reminder.start()
    await ctx.send(f"Study session started at ! {human_readable_time}")

#For the Session command which ends a session
@bot.command()
async def end(ctx):
    if not session.is_active:
        await ctx.send("A session has not been started yet!")
        return

    session.is_active = False
    end_time = ctx.message.created_at.timestamp()
    duration = end_time - session.start_time
    human_readable_duration = str(datetime.timedelta(seconds=duration))
    break_reminder.stop()
    await ctx.send(f"Session ended after {human_readable_duration} seconds")

#Count is the number of times the task will run. It is also MD compatible so you can make it bold, italicized, etc.
@tasks.loop(minutes=MAX_SESSION_TIME_MINUTES, count=2)
async def break_reminder():
    #Ignoore the first execution of this command
    if break_reminder.current_loop == 0:
        return
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"**Take a break!** You've been studying for {MAX_SESSION_TIME_MINUTES} minutes!")


@bot.command()
async def pb(ctx):
    r = requests.get(url="https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=2073850")
    d = r.json()
    index = d['response']
    player_count = index["player_count"]
    embed = disnake.Embed(title=f"The Final's Player Base!", 
                       description=f"Total Players: {player_count}", 
                       color = disnake.Colour.random(),
                       timestamp=datetime.datetime.now(),)
    embed.set_image(url="https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQuYQlQJ3RSdshlbZP2otBaYkze_JmPvKVSAxEflabXtcoijRqY")
    
    await ctx.send(embed=embed)

class AnimalSelect(Select):
    def __init__(self) -> None:
        super().__init__(
            min_values=1,
            max_values=2,
            placeholder="Pick a Game!",
            options=[
            discord.SelectOption(
                label="Cow", 
                description="cow"
            ),
            discord.SelectOption(
                label="Chicken", 
                description="chicken"
            ),
            ]
        )
         
    async def callback(self, interaction):
        new_return = str(self.values)[1:-1].replace("'", "")
        await interaction.response.send_message(f"You chose: {new_return}")

@bot.command()
async def dd(ctx):
    select = AnimalSelect()
    view = View()
    view.add_item(select)

    await ctx.send("Choose one! ", view=view)

    

#Runs the bot
bot.run(BOT_TOKEN)