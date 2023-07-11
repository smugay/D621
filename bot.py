import discord
from discord.ext import commands
import asyncio
import py621

from timeit import default_timer as timer

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='./', intents=intents)
client.remove_command('help')

@client.command(aliases=['e6'])
@commands.max_concurrency(number=1, per=commands.BucketType.user, wait=False)
async def e621(ctx, option=None, *, key=None):

    api = py621.api.apiGet(py621.types.e621)
    api_safe = py621.api.apiGet(py621.types.e926)

    if option == 'search':
        if key is None:
            await ctx.send('Please provide tag(s)!')
            return
        tag = []
        tag.append(key)
        base_fetch = 100
        page_num, post_num, fetch_amount = 1, 0, base_fetch
        try:
            Posts = api.getPosts(tag, fetch_amount, page_num, False)
            fetch_amount = len(Posts)
            Post = Posts[post_num]
        except:
            await ctx.send('Invalid tag(s)!')
            return
        
        try:
            pool_id = Post.pools[0]
        except IndexError:
            pool_id = 'None'

        post_embed = discord.Embed(title="Post Link - e621.net",
        url="https://e621.net/posts/" + str(Post.id), color=0x2b5fb5)
        post_embed.set_author(name=f'e621 search', icon_url="https://files.catbox.moe/vd56e4.png")
        post_embed.set_image(url=Post.file.url)
        post_embed.set_footer(text=f'({post_num}/{fetch_amount}) Page {page_num} - Pool ID ({pool_id})')
        thread = await ctx.send(embed=post_embed)
        
        await thread.add_reaction('◀')
        await thread.add_reaction('▶')
        await thread.add_reaction('🚫')
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=90,
                check=lambda reaction, user: user == ctx.author and reaction.emoji in ["▶", "◀","🚫"])
            except asyncio.TimeoutError:
                await thread.edit(content='`Thread timed out`')
                await thread.clear_reactions()
                return
            if reaction.emoji == "🚫":
                await thread.edit(content='`Thread manually closed`')
                await thread.clear_reactions()
                return
            if reaction.emoji == "▶":
                post_num += 1
                if post_num == base_fetch:
                    post_num = 0
                    page_num += 1
                if post_num == fetch_amount:
                    post_num = 0
                Posts = api.getPosts(tag, fetch_amount, page_num, False)
                Post = Posts[post_num]
                post_embed_edit = discord.Embed(title="Post Link - e621.net",
                url="https://e621.net/posts/" + str(Post.id), color=0x2b5fb5)
                post_embed_edit.set_author(name=f'e621 search', icon_url="https://files.catbox.moe/vd56e4.png")
                post_embed_edit.set_image(url=Post.file.url)
                post_embed_edit.set_footer(text=f'({post_num}/{fetch_amount}) Page {page_num} - Pool ID ({pool_id})')
                await thread.edit(embed=post_embed_edit)
                await thread.remove_reaction("▶", user)
            if reaction.emoji == "◀":
                post_num -= 1
                if post_num < 0:
                    page_num -= 1
                    post_num = fetch_amount-1
                if page_num < 1:
                    page_num = 1
                    post_num = 0
                Posts = api.getPosts(tag, fetch_amount, page_num, False)
                Post = Posts[post_num]
                post_embed_edit = discord.Embed(title="Post Link - e621.net",
                url="https://e621.net/posts/" + str(Post.id), color=0x2b5fb5)
                post_embed_edit.set_author(name=f'e621 search', icon_url="https://files.catbox.moe/vd56e4.png")
                post_embed_edit.set_image(url=Post.file.url)
                post_embed_edit.set_footer(text=f'({post_num}/{fetch_amount}) Page {page_num} - Pool ID ({pool_id})')
                await thread.edit(embed=post_embed_edit)
                await thread.remove_reaction("◀", user)
    
    if option == 'pool':
        if key is None:
            await ctx.send('Please provide pool ID!')
            return
        
        base_fetch = 100
        page_num, post_num = 1, 0

        try:
            pool = api.getPool(key)
            Posts = pool.getPosts()
            Post = Posts[post_num]
        except:
            await ctx.send('Please provide valid pool ID!')
            return
        
        fetch_amount = len(Posts)

        poolname = pool.name
        fixed_poolname = poolname.replace('_', ' ')

        post_embed_edit = discord.Embed(title=f'Pool Link - \'{fixed_poolname}\'',
        url="https://e621.net/pools/" + str(pool.id), color=0x2b5fb5)
        post_embed_edit.set_author(name=f'e621 pool', icon_url="https://files.catbox.moe/vd56e4.png")
        post_embed_edit.set_image(url=Post.file.url)
        post_embed_edit.set_footer(text=f'({post_num}/{fetch_amount}) Page {page_num} - Post ID ({Post.id})')
        await thread.edit(embed=post_embed_edit)
        
        await thread.add_reaction('◀')
        await thread.add_reaction('▶')
        await thread.add_reaction('🚫')
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=90,
                check=lambda reaction, user: user == ctx.author and reaction.emoji in ["▶", "◀","🚫"])
            except asyncio.TimeoutError:
                await thread.edit(content='`Thread timed out`')
                await thread.clear_reactions()
                return
            if reaction.emoji == "🚫":
                await thread.edit(content='`Thread manually closed`')
                await thread.clear_reactions()
                return
            if reaction.emoji == "▶":
                post_num += 1
                if post_num == base_fetch:
                    post_num = 0
                    page_num += 1
                if post_num == fetch_amount:
                    post_num = 0
                Post = Posts[post_num]

                post_embed_edit = discord.Embed(title=f'Pool Link - \'{fixed_poolname}\'',
                url="https://e621.net/pools/" + str(pool.id), color=0x2b5fb5)
                post_embed_edit.set_author(name=f'e621 pool', icon_url="https://files.catbox.moe/vd56e4.png")
                post_embed_edit.set_image(url=Post.file.url)
                post_embed_edit.set_footer(text=f'({post_num}/{fetch_amount}) Page {page_num} - Post ID ({Post.id})')
                await thread.edit(embed=post_embed_edit)
                await thread.remove_reaction("▶", user)

            if reaction.emoji == "◀":
                post_num -= 1
                if post_num < 0:
                    page_num -= 1
                    post_num = fetch_amount-1
                if page_num < 1:
                    page_num = 1
                    post_num = 0
                Post = Posts[post_num]

                post_embed_edit = discord.Embed(title=f'Pool Link - \'{fixed_poolname}\'',
                url="https://e621.net/pools/" + str(pool.id), color=0x2b5fb5)
                post_embed_edit.set_author(name=f'e621 pool', icon_url="https://files.catbox.moe/vd56e4.png")
                post_embed_edit.set_image(url=Post.file.url)
                post_embed_edit.set_footer(text=f'({post_num}/{fetch_amount}) Page {page_num} - Post ID ({Post.id})')
                await thread.edit(embed=post_embed_edit)
                await thread.remove_reaction("◀", user)

    if option == 'status':
        start = timer()
        fullstart = start
        try:
            Posts = api_safe.getPosts('', 1, 1, False)
            Posts[0]
            result_api='UP ✅'
        except:
            result_api='DOWN ❌'
        end = timer()
        unformated_time = "%.1f=- " % (1000 * (end - fullstart))
        formated_time = unformated_time.partition('.')
        icon_file = discord.File("media\e6_icon.png")
        embed=discord.Embed(title=" ", color=0x2b5fb5)
        embed.set_author(name=f'e621 API Status', icon_url="https://files.catbox.moe/vd56e4.png")
        embed.add_field(name=f'e621 API // {result_api}', value=" ", inline=True)
        embed.set_footer(text=f'status information fetched in {formated_time[0]}ms')
        await ctx.send(file=icon_file,embed=embed)

    if option == 'about':

        selected_page = 1

        info_embed = discord.Embed(title="Command usage",
            description="The usage of this command is split between 'options'\nwhich are as follows:")
        info_embed.set_author(name="About D621",
                icon_url="https://files.catbox.moe/6vqud3.png")
        info_embed.add_field(name="search - `<prefix> e621 search <tag(s)>`",
                value="Browse through posts with your selected tag(s)",
                inline=True)
        info_embed.add_field(name="pool - `<prefix> e621 search <Pool ID>`",
                value="Browse a Pool with a Pool ID",
                inline=True)
        info_embed.add_field(name="status - `<prefix> e621 status`",
                value="Fetch the status of the e621 API",
                inline=True)
        info_embed.add_field(name="about - `<prefix> e621 about`",
                value="You're reading it right now! :D",
                inline=True)
        info_embed.set_footer(text=f'Page ({selected_page}/3)')

        threads_embed = discord.Embed(title="About threads",
                    description="Threads are a simple way to prevent spamming the e621 API\nEach user is allowed a single thread to interact with the API")
        threads_embed.set_author(name="About D621",
                icon_url="https://files.catbox.moe/6vqud3.png")
        threads_embed.add_field(name="Q: Why use threads",
                value="A: It prevents clutter and spam\nOther bots use a similar system they just automatically close\nyour thread when you run a new command")
        threads_embed.add_field(name="Q: Why don't you close threads automatically",
                value="A: idk im just quirky like that :3")
        threads_embed.set_footer(text=f'Page ({selected_page}/3)')

        about_embed = discord.Embed(title="Info and credits",
                    description="D621 was made out of spite\nSome french bird made a fork of a shitty e621 bot I made a year ago")
        about_embed.set_author(name="About D621",
                icon_url="https://files.catbox.moe/6vqud3.png")
        about_embed.add_field(name="About",
                value="This is a remake of a bot I made over a year ago\npy621, the wrapper this bot uses is unmaintained and extremely slow",
                inline=True)
        about_embed.add_field(name="Credits",
                value="The source code can be found [here](https://github.com) \n[Luttyz](https://github.com/Luttyz) creator of the fork of my old bot\nThe [fork](https://github.com/Hunter-The-Furry/py621) of py621 this bot uses",
                inline=True)
        about_embed.add_field(name="Integration",
                value="This project was made to be easily integrated with your own bot, its a single command that can be easily copy+pasted into your own bot")
        about_embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/85663797?v=4")
        about_embed.set_footer(text=f'Page ({selected_page}/3)')

        thread = await ctx.send(embed=info_embed)

        await thread.add_reaction('◀')
        await thread.add_reaction('▶')
        await thread.add_reaction('🚫')
        while True:
            


            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=90,
                check=lambda reaction, user: user == ctx.author and reaction.emoji in ["▶", "◀","🚫"])
            except asyncio.TimeoutError:
                await thread.edit(content='`Thread timed out`')
                await thread.clear_reactions()
                return
            if reaction.emoji == "🚫":
                await thread.edit(content='`Thread manually closed`')
                await thread.clear_reactions()
                return
            if reaction.emoji == "▶":
                selected_page += 1
                if selected_page > 3:
                    selected_page = 3
                if selected_page == 1:
                    edit_embed = info_embed
                if selected_page == 2:
                    edit_embed = threads_embed
                if selected_page == 3:
                    edit_embed = about_embed
                info_embed.set_footer(text=f'Page ({selected_page}/3)')
                threads_embed.set_footer(text=f'Page ({selected_page}/3)')
                about_embed.set_footer(text=f'Page ({selected_page}/3)')
                await thread.edit(embed=edit_embed)
                await thread.remove_reaction("▶", user)
            if reaction.emoji == "◀":
                selected_page -= 1
                if selected_page < 1:
                    selected_page = 1
                if selected_page == 1:
                    edit_embed = info_embed
                elif selected_page == 2:
                    edit_embed = threads_embed
                elif selected_page == 3:
                    edit_embed == about_embed
                info_embed.set_footer(text=f'Page ({selected_page}/3)')
                threads_embed.set_footer(text=f'Page ({selected_page}/3)')
                about_embed.set_footer(text=f'Page ({selected_page}/3)')
                await thread.edit(embed=edit_embed)
                await thread.remove_reaction("◀", user)
                
    else:
        await ctx.send('Please select a valid option!\n`search - pool - status - about`')   
        return 
    

client.run('TOKEN')