import acord
import os
bot = acord.Commander(prefix="ab!",intents=acord.Intents.ALL)
# access the acord bot object by:
@bot.bot.on("ready")
def awake():
  print(f"{bot.bot.user} has logged in")
@bot.command()
async def test(ctx):
  return await ctx.author.send(content="ping!")

bot.run(token=...)