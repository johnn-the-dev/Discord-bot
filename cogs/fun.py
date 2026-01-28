from discord.ext import commands
import discord
import random
import os
import json

ECONOMY_FILE = "economy.json"

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

class Fun(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="8ball")
    async def magicball(self, ctx, *, question):
        responses = [
            "Absolutely yes!",
            "Absolutely not!",
            "Maybe...",
            "Ask me later.",
            "Count on it!",
            "I wouldn't do that.",
            "Stars are saying yes."
        ]

        answer = random.choice(responses)

        embed = discord.Embed(title=" Magic 8-Ball", color=0x9b59b6)
        embed.add_field(name="Question:", value=question, inline=False)
        embed.add_field(name="Answer:", value=answer, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="coinflip")
    async def coinflip(self, ctx):
        choices = ["Heads", "Tails"]
        result = random.choice(choices)
        
        embed = discord.Embed(title="Coin flip", description=f"It is: {result}", color=0xf1c40f)
        await ctx.send(embed=embed)

    @commands.command(name="rps")
    async def rockpaperscissors(self, ctx, amount: int | None = None, choice: str | None = None):
        if amount is None or choice is None:
            await ctx.send("In order to play, you have to input an amount you want to bet and your choice.")
            return
        
        if amount <= 0:
            await ctx.send("You have to bet more money than 0.")
            return

        data = load_economy_json()
        user_id = str(ctx.author.id)
        choices = ["rock", "paper", "scissors"]
        choice = choice.lower()
        AI_choice = random.choice(choices)
        result = ""
        losses = {
            "rock":"paper",
            "paper":"scissors",
            "scissors":"rock"
        }

        if choice not in choices:
            await ctx.send("Wrong input. Check your spelling. Choices are: 'rock', 'paper', 'scissors'.")
            return

        if user_id not in data or data[user_id]["balance"] < amount:
            await ctx.send("You're broke. Go !work a bit.")
            return

        if losses[choice] == AI_choice:
            data[user_id]["balance"] -= amount
            result = f"Lost. You lost {amount} gold."
            color = 0xff0000
            save_economy(data)

        elif choice == AI_choice:
            result = f"Draw. You keep your money."
            color = 0x0000ff
        else:
            data[user_id]["balance"] += amount
            color = 0x00ff00
            save_economy(data)
            result = f"Win. You win {amount} gold."

        embed = discord.Embed(title="Rock, Paper, Scissors", color=color)
        embed.add_field(name="You", value=f"You chose {choice}.", inline=True)
        embed.add_field(name="Opponent", value=f"Your opponent chose {AI_choice}.", inline=True)
        embed.add_field(name="Result", value=result, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))