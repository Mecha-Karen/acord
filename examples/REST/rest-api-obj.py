# REST API with the RestApi Object
from acord.rest import RestApi

# Put your actual token here
REST_API = RestApi(token=...)
loop = REST_API.loop

async def main():
    await REST_API.setup()

    guild = await REST_API.fetch_guild(...)
    # Actual guild ID goes above

    print("Fetched guild called", guild.name)

# Now we run as a task to prevent random Runtime Errors from aioHTTP
# Bug with asyncio - For users running versions <3.10
loop.run_until_complete(loop.create_task(main()))
