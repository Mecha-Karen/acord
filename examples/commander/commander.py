

import acord
import os
bot = acord.Commander(prefix="ab!",intents=acord.Intents.ALL)
# access the acord bot object by:

@bot.command()
async def test(ctx):
  return await ctx.author.send(content="ping!")

bot.run(token=...)
