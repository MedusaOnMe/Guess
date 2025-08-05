from twitchio.ext import commands
import queue_manager
import os
from dotenv import load_dotenv
print("[BOT] Starting bot initialization...")

class Bot(commands.Bot):
    def __init__(self):
        print("[BOT] Initializing Twitch bot...")
        token = os.getenv("TWITCH_TOKEN")
        channel = os.getenv("TWITCH_CHANNEL")
        print(f"[BOT] Token exists: {token is not None}")
        print(f"[BOT] Channel: {channel}")
        super().__init__(
            token=token,
            prefix="!",
            initial_channels=[channel]
        )
        print("[BOT] Bot initialized successfully")

    async def event_ready(self):
        print(f"[BOT] ✅ CONNECTED! Logged in as: {self.nick}")
        print(f"[BOT] Bot is ready and listening for !guess commands")

    @commands.command()
    async def guess(self, ctx):
        print(f"[BOT] ❗ COMMAND RECEIVED from {ctx.author.name}")
        print(f"[BOT] Full message: '{ctx.message.content}'")
        
        place = ctx.message.content[len("!guess "):].strip()
        print(f"[BOT] Extracted place: '{place}'")
        
        if not place:
            print(f"[BOT] ❌ Empty place name, ignoring")
            await ctx.send(f"{ctx.author.name} please provide a location! Example: !guess Paris")
            return
            
        print(f"[BOT] Adding to queue: user={ctx.author.name}, place={place}")
        queue_manager.add_to_queue(ctx.author.name, place)
        print(f"[BOT] ✅ Added to queue successfully")
        
        # Check queue status by loading from file
        try:
            queue = queue_manager._load_queue()
            queue_size = len(queue)
            print(f"[BOT] Current queue size: {queue_size}")
        except:
            queue_size = "?"
            print(f"[BOT] Could not determine queue size")
        
        await ctx.send(f"{ctx.author.name} submitted a guess for: {place} (Queue: {queue_size})")
        print(f"[BOT] Response sent to chat")

if __name__ == "__main__":
    print("[BOT] Loading environment variables...")
    load_dotenv()
    print("[BOT] Creating bot instance...")
    bot = Bot()
    print("[BOT] Starting bot... (this will block)")
    try:
        bot.run()
    except Exception as e:
        print(f"[BOT] ❌ FATAL ERROR: {e}")
        raise
