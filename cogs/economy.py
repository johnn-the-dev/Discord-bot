from discord.ext import commands
import os
import discord
import random
import json

SHOP_ITEMS = {
    "cookie": {
        "name": "Cookie", 
        "price": 50, 
        "description": "Sweet snack. Adds 50XP.",
        "type": "xp",
        "value": 50
    },
    "potion": {
        "name": "Money Potion", 
        "price": 500, 
        "description": "Unknown potion. Adds money (500-1500).",
        "type": "money",
        "value": 0
    },
    "vip": {
        "name": "VIP Role",
        "price": 5000,
        "description": "Gives you VIP role in this server.",
        "type": "role",
        "role_name": "VIP"
    },
    "lock": {
        "name": "A Lock", 
        "price": 2000, 
        "description": "Keeps you safe from stealing. Breaks after an attempt of robbery.",
        "type": "passive", 
        "value": 0
    },
}

ECONOMY_FILE = "economy.json"
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

def load_economy_json():
    if not os.path.exists(ECONOMY_FILE):
        return {}
    try:
        with open(ECONOMY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_economy(data):
    with open(ECONOMY_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance")
    async def balance(self, ctx):
        data = load_economy_json()
        user_id = str(ctx.author.id)

        if user_id in data:
            await ctx.send(f"Your balance: {data[user_id]}.")
        else:
            await ctx.send("Your balance: 0")

    @commands.command(name="work")
    async def work(self, ctx):
        data = load_economy_json()
        random_number = random.randint(1, 1000)    
        user_id = str(ctx.author.id)

        if user_id in data:
            data[user_id]["balance"] += random_number
        else:
            data[user_id] = {"balance": 0, "inventory": []}
            data[user_id]["balance"] += random_number
        
        save_economy(data)
        await ctx.send(f"You worked and made {random_number} gold.")

    @commands.command(name="gamble")
    async def gamble(self, ctx, amount: int | None = None):
        data = load_economy_json()
        user_id = str(ctx.author.id)
        
        if amount is None:
            await ctx.send("Input an amount of money to gamble.")
            return
        if amount <= 0:
            await ctx.send("Bet more than 0 amount of money.")
            return

        if user_id in data:
            if data[user_id]["balance"] < amount:
                embed = discord.Embed(title=f"{ctx.author.name}, Gambling failed.", description=f"You don't have enough money to gamble {amount}.", color=0xff0000)
                await ctx.send(embed=embed)

            else:
                result = random.randint(1, 10)
                if result > 2:
                    data[user_id]["balance"] -= amount
                    embed = discord.Embed(title=f"{ctx.author.name}, Lost The Gamble!", description=f"You lost {amount} of money gambling.", color=0xff0000)
                    await ctx.send(embed=embed)
                    save_economy(data)
                else:
                    won_amount = 2 * amount
                    data[user_id]["balance"] += amount
                    embed = discord.Embed(title=f"{ctx.author.name}, Won The Gamble!", description=f"You won {won_amount} of money gambling.", color=0x00ff00)
                    await ctx.send(embed=embed)
                    save_economy(data)
        else:
            embed = discord.Embed(title=f"{ctx.author.name} doesn't have any money.", description="You don't have any money", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name="shop")
    async def shop(self, ctx):
        embed = discord.Embed(title="Shop", description="What do you want to buy?", color=0xe91e63)
        
        for key, item in SHOP_ITEMS.items():
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            
            embed.add_field(name=f"{name} — {price} Gold", value=f"Code: `{key}`\n{desc}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, item_code: str | None = None):
        if item_code is None:
            await ctx.send("Choose what do you want to buy.")
            return
        
        item_code = item_code.lower()

        if item_code not in SHOP_ITEMS:
            await ctx.send("This item isn't available.")
            return
        
        item_info = SHOP_ITEMS[item_code]
        price = item_info["price"]
        item_display_name = item_info["name"]

        data = load_economy_json()
        user_id = str(ctx.author.id)

        if user_id not in data:
            await ctx.send("You're not on the server data.")
            return
        
        if data[user_id]["balance"] < price:
            await ctx.send("You don't have any money. Go !work a bit.")
            return
        
        data[user_id]["balance"] -= price

        if item_info["type"] == "role":
            role_name = item_info["role_name"]
            role = discord.utils.get(ctx.guild.roles, name=role_name)

            if role:
                if role in ctx.author.roles:
                    await ctx.send("You already have this role. Money returned.")
                    data[user_id]["balance"] += price
                    return
                await ctx.author.add_roles(role)
                await ctx.send(f"You now own {role_name}")
            else:
                await ctx.send("Error: Role isn't on this server.")
                data[user_id]["balance"] += price
                return
        else:
            data[user_id]["inventory"].append(item_code)
            await ctx.send(f"You now own {item_display_name} for {price}")

        save_economy(data)

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        data = load_economy_json()

        sorted_data = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)
        leaderboard_text = ""
        for i, (user_id, amount) in enumerate(sorted_data[:10], start=1):
            member = ctx.guild.get_member(int(user_id))

            if member:
                name = member.display_name
            else:
                name = "Unknown user"
            
            if i == 1: rank = "🥇"
            elif i == 2: rank = "🥈"
            elif i == 3: rank = "🥉"
            else: rank = f"#{i}"

            leaderboard_text += f"{rank} **{name}**: {amount}\n"

        embed = discord.Embed(title="Top 10 of the richest members.", description=leaderboard_text, color=0xffd700)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

    @commands.command(name="inventory")
    async def inventory(self, ctx):
        data = load_economy_json()
        user_id = str(ctx.author.id)
        listed = ""
        if user_id not in data:
            await ctx.send("Your inventory is empty. You aren't even in the data.")
            return
        
        inventory_list = data[user_id]["inventory"]

        if not inventory_list:
            await ctx.send("Your inventory is empty.")
        else:
            for item in inventory_list:
                listed += f"{item};"

            embed = discord.Embed(title=f"Inventory: {ctx.author.name}", description=f"Items in inventory: {listed}", color= 0x0099ff)
            await ctx.send(embed=embed)

    @commands.command(name="use")
    async def use(self, ctx, *, item_code: str | None = None):
        if item_code is None:
            await ctx.send("You have to specify what you want to use.")
            return
        
        data = load_economy_json()
        levels = load_levels_json()

        user_id = str(ctx.author.id)
        item_code = item_code.lower()

        if user_id not in data or item_code not in data[user_id]["inventory"]:
            await ctx.send("You dont own this item.")
            return
        
        if item_code not in SHOP_ITEMS:
            await ctx.send("This item isn't in our database.")
            return
        
        item_info = SHOP_ITEMS[item_code]
        item_type = item_info["type"]

        used = False

        if item_type == "xp":
            levels = load_levels_json()
            if user_id not in levels: levels[user_id] = {"xp": 0, "level": 1}

            amount = item_info["value"]
            levels[user_id]["xp"] += amount
            save_levels(levels)

            await ctx.send(f"Item used successfully. You gained {amount} XP.")
            used = True

        elif item_type == "money":
            reward = random.randint(500, 1500)
            data[user_id]["balance"] += reward
            await ctx.send(f"Item used successfully. You gained {reward} gold.")
            used = True
        
        elif item_type == "role":
            await ctx.send("Role activates automatically when bought.")
            used = False
        
        if used:
            data[user_id]["inventory"].remove(item_code)
            save_economy(data)

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def rob(self, ctx, member: discord.Member | None = None):
        if member is None:
            await ctx.send("You have to say who you want to rob.")
            return
        
        if member.id == ctx.author.id:
            await ctx.send("You can't rob yourself.")
            return
        
        data = load_economy_json()
        robber_id = str(ctx.author.id)
        victim_id = str(member.id)

        if robber_id not in data:
            await ctx.send("You can't steal, because you don't have where to put what you stole (you're not in the database).")
            return
        
        if victim_id not in data or data[victim_id]["balance"] < 10:
            await ctx.send("You can't steal from someone who's broke.")
            return
        
        victim_inventory = data[victim_id]["inventory"]

        if "lock" in victim_inventory:
            victim_inventory.remove("lock")
            save_economy(data)

            await ctx.send(f"You didn't steal anything because {member.name} made precautions.")
            return
        
        success_chance = random.randint(1, 100)

        if success_chance <= 40:
            steal_percent = random.randint(10, 40) / 100
            steal_amount = int(data[victim_id]["balance"] * steal_percent)

            data[victim_id]["balance"] -= steal_amount
            data[robber_id]["balance"] += steal_amount
            save_economy(data)

            embed = discord.Embed(title="Robbery successful", description=f"You robbed {member.name} and took {steal_amount} gold.", color=0x00ff00)
            await ctx.send(embed=embed)
        
        else:
            fine = 500

            current_balance = data[robber_id]["balance"]
            if current_balance < fine:
                fine = current_balance
            
            data[robber_id]["balance"] -= fine
            save_economy(data)

            embed = discord.Embed(title="You were caught.", description=f"You were caught by the police and fined {fine} gold.", color=0xff0000)
            await ctx.send(embed=embed)

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            seconds = int(error.retry_after % 60)
            await ctx.send(f"You have to wait to try to rob someone again. Try in {minutes}m and {seconds}s.")

async def setup(bot):
    await bot.add_cog(Economy(bot))