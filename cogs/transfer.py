import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from discord.ui import Select
from discord.utils import get
import asyncio
from typing import Optional
import json
from discord.ext import tasks
import re 
import asyncpg
from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar

# with open("cogs/jsons/settings.json") as json_file:
#     data_dict = json.load(json_file)
guild_id = 617136488840429598
    # book_sharing_id = data_dict["book_sharing"]
    # audio_sharing_id = data_dict["audio_sharing"]
    # vn_sharing_id = data_dict["vn_sharing"]


# TEST_ID = 1068270953194323968
# TEST2_ID = 1068271983671918692
# image_formats = ['bmp','jpeg','jpg','png']
# file_formats = ['epub', 'm4b', '7z', 'zip']
# BACKUP_AUDIO_SHARING_ID = 1067456267397894225

# class MyView(discord.ui.View):
#     def __init__(self, *, timeout: Optional[float] = 1800, data, beginning_index: int, end_index: int, request):
#         super().__init__(timeout=timeout)
#         self.data: list = data
#         self.beginning_index: int = beginning_index
#         self.ending_index: int = end_index
#         self.request = request
    
    
#     async def edit_embed(self, data, request, beginning_index, ending_index):
#         myembed = discord.Embed(title=f'{len(data)} results for {request}')
#         for result in data[beginning_index:ending_index]:
#             myembed.add_field(name=f'{result[0]}: {result[2]}',value=f'{result[1]}', inline=False)
#         if len(data) >= 2:
#             myembed.set_footer(text="... not all results displayed but you can pick any index.\n"
#                                     "Pick an index to retrieve a scene next.")
#         else:
#             myembed.set_footer(text="Pick an index to retrieve a scene next.")
#         return myembed
        
        
#     @discord.ui.button(label='≪', style=discord.ButtonStyle.grey, row=1)
#     async def go_to_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index -= 2
#         self.ending_index -= 2
#         if self.beginning_index >= len(self.data):
#             self.beginning_index = 0
#             self.ending_index = 2
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)
        
        
#     @discord.ui.button(label='Back', style=discord.ButtonStyle.blurple, row=1)
#     async def go_to_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index -= 1
#         self.ending_index -= 1
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)
    
    
#     @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple, row=1)
#     async def go_to_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index += 1
#         self.ending_index += 1
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)        
        
        
#     @discord.ui.button(label='≫', style=discord.ButtonStyle.grey, row=1)
#     async def go_to_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.beginning_index += 2
#         self.ending_index += 2
#         if self.beginning_index >= len(self.data):
#             self.beginning_index -= 2
#             self.ending_index -= 2
#         myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
#         await interaction.response.edit_message(embed=myembed)
        
        
#     @discord.ui.button(label='Quit', style=discord.ButtonStyle.red, row=1)
#     async def stop_pages(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.delete_original_response()

        
class Transfer_V2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = []
        self.batch_update.add_exception_type(asyncpg.PostgresConnectionError)
        self.batch_update.start()
        
    def cog_unload(self):
        self.batch_update.cancel()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.tmw = self.bot.get_guild(617136488840429598)
        self.selfmute = self.tmw.get_role(1294660039747047425)
        self.fullselfmute = self.tmw.get_role(1294661079032528948)
        self.batch_update.start()
    #     self.upload = get(self.tmw.channels, name='test') or self.tmw.get_channel(TEST_ID)
    #     self.lofn = get(self.tmw.channels, name='test2') or self.tmw.get_channel(TEST2_ID)
    #     self.backup = self.bot.get_guild(1067455416902090752)
    #     self.storage = get(self.backup.channels, name='backups') or self.backup.get_channel(BACKUP_AUDIO_SHARING_ID)
    
    
    # async def get_backuped_file(self, selected_files, data):
    #     messages = []
    #     print(selected_files)
    #     for i, file in enumerate(data):
    #         if selected_files[0] == file[2]:
    #             message = await self.storage.fetch_message(data[i][7])
    #             messages.append(message)
        #download_files: list[discord.File] = [[await attachment.to_file(filename=attachment.filename) for attachment in message.attachments] async for message in messages]
        # download_files: list[discord.File] = []
        # for message in messages:
        #     for attachment in message.attachments:
        #         file = await attachment.to_file(filename=attachment.filename)
        #         download_files.append(file)
        # return download_files

    async def store_roles(self, id, roles, date):
        print(id, roles, date)
        con = sqlite3.connect('mutes.db')
        cur = con.cursor()
        cur.execute("INSERT INTO mutes (user_id, roles, time) VALUES (?,?,?)", (int(id), str(roles), str(date)))
        con.commit()
        cur.close()
    
    async def get_muted_members(self):
        con = sqlite3.connect('mutes.db')
        cur = con.cursor()
        query = """SELECT * FROM mutes"""
        cur.execute(query)
        con.commit()
        mutes = cur.fetchall()
        con.close()
        
        return mutes
    
    async def delete_mute(self, user_id):
        con = sqlite3.connect('mutes.db')
        cur = con.cursor()
        query = """DELETE FROM mutes WHERE user_id = ?"""
        data = ([int(user_id)])
        cur.execute(query, data)
        con.commit()
        cur.close()
        print("success")

    @app_commands.command(name="fullselfmute", description="Mute yourself. UTC")
    async def fullselfmute(self, interaction: discord.Interaction, hours: Optional[int] = 0, minutes: Optional[int] = 0, seconds: Optional[int] = 0):   
        # for role in interaction.user.roles:
        #     if role.id not in [1027706897731702846, 1026924690029170718, 1026922492884951121, 834998819241459722, 834999083512758293, 795698879227887678, 795698963494731806, 795699064409948210, 795699163144126474, 795699221365260359, 1026918330566721576, 1026918224266280960]:
        #         return await interaction.response.send_message(content='You have to pass any level of the quiz to use this command.', ephemeral=True)
        import datetime
        if self.selfmute in interaction.user.roles:
            return await interaction.response.send_message(content='''You can't fullmute and selfmute''', ephemeral=True)
        elif self.fullselfmute in interaction.user.roles:
            return await interaction.response.send_message(content='''You can't fullmute while fullmuted''', ephemeral=True)

        time = hours * 60 * 60 + minutes * 60 + seconds
        if time < 10:
            return await interaction.response.send_message(content='''You can't mute for less than 10 seconds.''', ephemeral=True)
        date = discord.utils.utcnow() + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)       
        roles = [role.id for role in interaction.user.roles]
        # from datetime import datetime
        await interaction.response.send_message(f'''Alright {interaction.user.mention}, fullselfmute till <t:{calendar.timegm(date.utctimetuple())}:R> \n<t:{calendar.timegm(date.utctimetuple())}>''', ephemeral=True)
        await self.store_roles(interaction.user.id, roles, date)
        date = date.strftime("%H:%M:%S")
        await asyncio.sleep(3)
        for id in roles:
            role = self.tmw.get_role(id)
            if role.name == "@everyone" or role.id == 675081968458792975:
                continue
            try:
                await interaction.user.remove_roles(role)
            except Exception:
                continue
        selfmute_role = interaction.guild.get_role(1294661079032528948)
        await interaction.user.add_roles(selfmute_role)

    @app_commands.command(name="selfmute", description="Mute yourself. UTC")
    async def selfmute(self, interaction: discord.Interaction, hours: Optional[int] = 0, minutes: Optional[int] = 0, seconds: Optional[int] = 0):   
        # for role in interaction.user.roles:
        #     if role.id not in [1027706897731702846, 1026924690029170718, 1026922492884951121, 834998819241459722, 834999083512758293, 795698879227887678, 795698963494731806, 795699064409948210, 795699163144126474, 795699221365260359, 1026918330566721576, 1026918224266280960]:
        #         return await interaction.response.send_message(content='You have to pass any level of the quiz to use this command.', ephemeral=True)
        import datetime
        if self.selfmute in interaction.user.roles:
            return await interaction.response.send_message(content='''You can't selfmute while selfmuted''', ephemeral=True)
        elif self.fullselfmute in interaction.user.roles:
            return await interaction.response.send_message(content='''You can't fullmute while selfmuted''', ephemeral=True)
        
        time = hours * 60 * 60 + minutes * 60 + seconds
        if time < 10:
            return await interaction.response.send_message(content='''You can't mute for less than 10 seconds.''')
        date = discord.utils.utcnow() + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        roles = [role.id for role in interaction.user.roles]
        # from datetime import datetime
        await interaction.response.send_message(f'''Alright {interaction.user.mention}, selfmute till <t:{calendar.timegm(date.utctimetuple())}:R> \n<t:{calendar.timegm(date.utctimetuple())}>''', ephemeral=True)
        await self.store_roles(interaction.user.id, roles, date)
        date = date.strftime("%H:%M:%S")
        await asyncio.sleep(3)
        for id in roles:
            role = self.tmw.get_role(id)
            if role.name == "@everyone" or role.id == 675081968458792975:
                continue
            try:
                await interaction.user.remove_roles(role)
            except Exception:
                continue
        selfmute_role = interaction.guild.get_role(1294660039747047425)

        await interaction.user.add_roles(selfmute_role)
        
    @app_commands.command(name="check_mute", description="Removes your mute if the specified time has already pasted")
    async def check_mute(self, interaction: discord.Interaction):   
        await interaction.response.defer(ephemeral=True)
        selfmute_role = interaction.guild.get_role(1294660039747047425)
        fullselfmute_role = interaction.guild.get_role(1294661079032528948)
        if selfmute_role in interaction.user.roles:
            mutes = await self.get_muted_members()
            now = discord.utils.utcnow()
            for mute in mutes:
                id = mute[0]
                when = mute[2]
                member = interaction.guild.get_member(int(id))
                try:
                    print(member.name, id)
                except Exception:
                    continue
                else:
                    if int(id) == interaction.user.id or member.id == interaction.user.id:
                        myembed = discord.Embed(title=f'Selftimeout')
                        myembed.add_field(name='Remaining', value=f'''<t:{calendar.timegm(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z").utctimetuple())}:R> \n<t:{calendar.timegm(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z").utctimetuple())}>''', )
                        pfp = self.bot.user.avatar.url
                        myembed.set_footer(icon_url=pfp, text=f'From {self.bot.user.name}')
                        await interaction.edit_original_response(embed=myembed)
                    try:
                        print(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z") < now)
                        print(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z"))
                        print(id, when)
                        if datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z") < now:
                            self.tmw = self.bot.get_guild(guild_id)
                            member = self.tmw.get_member(int(id))
                        else:
                            continue
                    except Exception:
                        continue
                    else:
                        print(member)
                        if selfmute_role in member.roles:
                            await member.remove_roles(selfmute_role)
                        elif fullselfmute_role:
                            await member.remove_roles(fullselfmute_role)
                        print("removed selfmute role")
                        for role_id in mute[1].strip('][').split(', '):
                            if int(role_id) == 617136488840429598:
                                continue
                            try:
                                role = self.tmw.get_role(int(role_id))
                                print("got role")
                            except Exception:
                                continue
                            else:
                                print(role)
                                try:
                                    await member.add_roles(role)
                                except Exception:
                                    print(f'{member} ({member.id}) - {role} not added')
                        await self.delete_mute(int(id))
            return await interaction.edit_original_response(content='Updated mutes')
        elif fullselfmute_role in interaction.user.roles:
            mutes = await self.get_muted_members()
            now = discord.utils.utcnow()
            for mute in mutes:
                id = mute[0]
                when = mute[2]
                member = interaction.guild.get_member(int(id))
                try:
                    print(member.name, id)
                except Exception:
                    continue
                else:
                    if int(id) == interaction.user.id or member.id == interaction.user.id:
                        myembed = discord.Embed(title=f'Selftimeout')
                        myembed.add_field(name='Remaining', value=f'''<t:{calendar.timegm(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z").utctimetuple())}:R> \n<t:{calendar.timegm(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z").utctimetuple())}>''', )
                        pfp = self.bot.user.avatar.url
                        myembed.set_footer(icon_url=pfp, text=f'From {self.bot.user.name}')
                        await interaction.edit_original_response(embed=myembed)
                    try:
                        print(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z") < now)
                        print(datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z"))
                        print(id, when)
                        if datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z") < now:
                            self.tmw = self.bot.get_guild(guild_id)
                            member = self.tmw.get_member(int(id))
                        else:
                            continue
                    except Exception:
                        continue
                    else:
                        print(member)
                        if selfmute_role in member.roles:
                            await member.remove_roles(selfmute_role)
                        elif fullselfmute_role:
                            await member.remove_roles(fullselfmute_role)
                        print("removed selfmute role")
                        for role_id in mute[1].strip('][').split(', '):
                            if int(role_id) == 617136488840429598:
                                continue
                            try:
                                role = self.tmw.get_role(int(role_id))
                                print("got role")
                            except Exception:
                                continue
                            else:
                                print(role)
                                try:
                                    await member.add_roles(role)
                                except Exception:
                                    print(f'{member} ({member.id}) - {role} not added')
                        await self.delete_mute(int(id))
            return await interaction.edit_original_response(content='Updated mutes')
        
        else:
            interaction.edit_original_responses(content='''You need to be selfmuted or fullmuted''')

    
    # @app_commands.command(name="check_roles", description="Removes your mute if the specified time has already pasted")
    # async def check_roles(self, interaction: discord.Interaction):   
    #     if not self.selfmute in interaction.user.roles:
    #         return
    #     mutes = await self.get_muted_members()
    #     now = discord.utils.utcnow()
    #     for mute in mutes:
    #         id = mute[0]
    #         when = mute[2]
    #         member = self.tmw.get_member(int(id))
    #         print(member)
    #         for role_id in mute[1].strip('][').split(', '):
    #             role = self.tmw.get_role(int(role_id))
    #             print(role)    


        
        # bool, data = await self.check_existing(request)
        # if not bool:
        #    return await interaction.response.send_message(ephemeral=True, content=f'''{request} does not exist.''') 
        # myembed = discord.Embed(title=f'{len(data)} results for {request}')
        # for result in data[0:2]:
        #     myembed.add_field(name=f'{result[0]}: {result[2]}',value=f'{result[1]}', inline=False)
        # if len(data) >= 2:
        #     myembed.set_footer(text="... not all results displayed but you can pick any index.\n"
        #                        "Pick an index to retrieve a scene next.")
        # else:
        #     myembed.set_footer(text="Pick an index to retrieve a scene next.")
        # beginning_index = 0
        # end_index = 2
        
        # options = []
        # for file in data:
        #     item = discord.SelectOption(label=f'{file[2]}')
        #     options.append(item)
            
        # select = Select(min_values = 1, max_values = int(len(options)), options=options)   
        # async def my_callback(interaction):
        #     selected_files = "\n".join(select.values)
        #     await interaction.response.send_message(ephemeral=True, content=f'Downloading the folling files:\n{selected_files}')
        #     download_files = await self.get_backuped_file(select.values, data)
        #     await interaction.channel.send(files=download_files, content=f'''{[file][0][2][:1999]}''')

        # select.callback = my_callback
        # view = MyView(data=data, beginning_index=beginning_index, end_index=end_index, request=request)
        
        # view.add_item(select)
        # await interaction.response.send_message(embed=myembed, view=view)
    @tasks.loop(minutes=5)
    async def batch_update(self):
        #await asyncio.sleep(5)
        selfmute_role = self.tmw.get_role(1294660039747047425)
        fullselfmute_role = self.tmw.get_role(1294661079032528948)
        mutes = await self.get_muted_members()
        now = discord.utils.utcnow()
        for mute in mutes:
            id = mute[0]
            when = mute[2]
            try:
                if datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z") < now:
                    member = self.tmw.get_member(int(id))
                    print(member.name)
                else:
                    continue
            except Exception:
                continue
            else:
                member = self.tmw.get_member(int(id))
                print(member)
                if selfmute_role in member.roles:
                    await member.remove_roles(selfmute_role)
                else:
                    await member.remove_roles(fullselfmute_role)
                print("removed selfmute role")
                for role_id in mute[1].strip('][').split(', '):
                    if int(role_id) == 617136488840429598:
                        continue
                    try:
                        role = self.tmw.get_role(int(role_id))
                        print("got role")
                    except Exception:
                        continue
                    else:
                        print(role)
                        try:
                            await member.add_roles(role)
                        except Exception:
                            print(f'{member} ({member.id}) - {role} not added')
                await self.delete_mute(int(id))
    # async def store_file_info(self, message, filename):
    #     con = sqlite3.connect('files.db')
    #     cur = con.cursor()
    #     query = """INSERT INTO files (filename, description, member, date, guild, channel) VALUES (?,?,?,?,?,?)"""
    #     data = (filename[0], message.content, message.author.id, message.created_at, message.guild.id, message.channel.id)
    #     cur.execute(query, data)
    #     con.commit()
    #     cur.close()
        
    # async def check_existing(self, message_content):
    #     con = sqlite3.connect('files.db')
    #     cur = con.cursor()
    #     message_content = '%'+message_content+'%'
    #     query = """SELECT EXISTS(
    #     SELECT * FROM files WHERE description LIKE ?
    #     ) AS didTry"""
    #     cur.execute(query, [message_content])
    #     bool = cur.fetchall()[0][0] == 1
    #     query = """SELECT ROW_NUMBER() OVER(ORDER BY description DESC) as num_row, * FROM files WHERE description LIKE ?"""
    #     cur.execute(query, [message_content])
    #     data = cur.fetchall()

    #     return bool, data
    
    # async def delete_upload(self, message):
    #     await message.add_reaction('❌')
    #     await asyncio.sleep(2)
    #     await message.delete()
    
    
    # async def update_link(self, message, filename, msg):
    #     con = sqlite3.connect('files.db')
    #     cur = con.cursor()
    #     query = '''UPDATE files SET link = ? WHERE filename = ? AND description = ?'''
    #     data = (msg.id, filename[0], message.content)
    #     cur.execute(query, data)
    #     con.commit()
    #     cur.close()
        
        
    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.channel != self.upload:
    #         return
        
    #     if message.author.bot:
    #         return
        
    #     bool, data = await self.check_existing(message.content)
    #     if bool:
    #         return

    #     if message.attachments:
    #         try:
    #             upload_files: list[discord.File] = [await attachment.to_file(filename=attachment.filename) for attachment in message.attachments if attachment.filename.endswith('.epub') or attachment.filename.endswith(".7z") or attachment.filename.endswith(".zip")]
    #             if upload_files == []:
    #                 return
    #             await self.store_file_info(message, [attachment.filename for attachment in message.attachments if attachment.filename.endswith('.epub') or attachment.filename.endswith(".7z") or attachment.filename.endswith(".zip")])
    #             msg = await self.storage.send(files=upload_files, content=f'''{message.content[:1999]}''')
    #             await self.update_link(message, [attachment.filename for attachment in message.attachments if attachment.filename.endswith('.epub') or attachment.filename.endswith(".7z") or attachment.filename.endswith(".zip")], msg)
    #             cover: list[discord.File] = [await attachment.to_file(filename=attachment.filename) for attachment in message.attachments if attachment.filename.endswith('.png') or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".jpg") or attachment.filename.endswith(".bmp")]
    #             await self.lofn.send(files=cover, content=f'{message.content}')
    #             await message.delete()
    #         except Exception as e:
    #             await self.delete_upload(message)
    #             print(f'File too large: {e}')

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Transfer_V2(bot))
