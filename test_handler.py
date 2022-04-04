import acord
import os
bot = acord.Bot(prefix="ab!",intents=acord.Intents.ALL)
# access the acord bot object by:
@bot.bot.on("ready")
def awake():
  print(f"{bot.bot.user} has logged in")
@bot.command()
async def test(ctx):
  return await ctx.author.send(content="ping!")

bot.run(token="OTQ3NDM5Mzg5OTM4Njc5ODEw.YhtRsQ.hbtjE7CwxhDxv8vF1rII0UiwSos")