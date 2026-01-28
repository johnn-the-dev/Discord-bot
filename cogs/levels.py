from discord.ext import commands
import os
import discord
import random
import json
from typing import Optional

LEVELS_FILE = "levels.json"

def load_levels_json():
        if not os.path.exists(LEVELS_FILE):
            return {}
        try:
            with open(LEVELS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

def save_levels(data):
    with open(LEVELS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        data = load_levels_json()
        user_id = str(message.author.id)
        XP = 25

        if user_id not in data:
            data[user_id] = {"xp": 0, "level": 1}
        
        data[user_id]["xp"] += random.randint(5, 10)

        current_xp = data[user_id]["xp"]
        current_level = data[user_id]["level"]
        level_threshold = current_level * 100

        if current_xp >= level_threshold:
            excess = current_xp - level_threshold
            data[user_id]["level"] += 1
            data[user_id]["xp"] = excess

            embed = discord.Embed(title=f"{message.author.name} leveled up!", description=f"{message.author.mention} is now level {data[user_id]['level']}.", color=0x00ff00)
            await message.channel.send(embed=embed)

        save_levels(data)

    @commands.command(name="rank", aliases=["level"])
    async def rank(self, ctx, member: Optional[discord.Member] = None):
        target = member or ctx.author
        data = load_levels_json()
        user_id = str(target.id)
 
        if user_id in data:
            lvl = data[user_id]["level"]
            xp = data[user_id]["xp"]
            threshold = lvl * 100
            
            embed = discord.Embed(title=f"Rank: {target.name}", color=0x3498db)
            embed.add_field(name="Level", value=str(lvl), inline=True)
            embed.add_field(name="XP", value=f"{xp}/{threshold}", inline=True)
            embed.set_thumbnail(url=target.display_avatar.url)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("This user doesn't have any level yet.")

async def setup(bot):
    await bot.add_cog(Levels(bot))