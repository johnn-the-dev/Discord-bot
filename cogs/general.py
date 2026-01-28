import os
from discord.ext import commands
import discord
import requests

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f'🏓 Pong! ({round(self.bot.latency * 1000)}ms)')

    @commands.command(name="weather")
    async def weather(self, ctx, *, city: str):
        API_KEY = os.getenv('WEATHER_KEY')
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            desc = data["weather"][0]["description"]
            await ctx.send(f"🌤️ **{city.capitalize()}**: {temp}°C, feels like: {feels_like}°C, {desc}, humidity: {humidity}, weather {wind_speed} m/s.")

        elif response.status_code == 401:
            await ctx.send("Error: Unauthorized access.")
        elif response.status_code == 404:
            await ctx.send("Error: City not found.")
        else:
            await ctx.send(f"Unknown error: {response.status_code}")

    @commands.command(name="dog")
    async def dog(self, ctx):
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        data = response.json()
        img_url = data['message']

        embed = discord.Embed(title="Random picture of a dog.", color=0xff9900)
        embed.set_image(url=img_url)
        embed.set_footer(text=f"Requested by: {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member | None = None):
        target_user = member or ctx.author

        embed = discord.Embed(title=f"Avatar of user {target_user.name}", color=0x3498db)
        embed.set_image(url=target_user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))