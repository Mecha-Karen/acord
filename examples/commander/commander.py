
# Welcome to ACords getting started guide!
import acord



bot = acord.Bot(prefix="ab!",intents=acord.Intents.ALL)
@bot.command()
async def test(ctx):
  return await ctx.author.send(content="ping!")
@bot.on("ready")
async def awake():
    print(f"{bot.bot.user}")
bot.launch(token="OTQ3NDM5Mzg5OTM4Njc5ODEw.YhtRsQ.hbtjE7CwxhDxv8vF1rII0UiwSos")
