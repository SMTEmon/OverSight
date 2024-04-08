import discord
from discord import app_commands
from discord.ext import commands, tasks
import yt_dlp
import asyncio
import datetime
#from dotenv import load_dotenv
from youtubesearchpython import VideosSearch
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Set up your Spotify API credentials
client_id = ''
client_secret = ''

# Authenticate with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



pause_func = 0

q = []

p = 0

voice_channel= ()

channel_id = int()

#load_dotenv()


bot = commands.Bot(command_prefix="j!" , intents = discord.Intents.all())



@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands(s)")
        update_status.start()  # Start the timer task

        

    except Exception as e:
        print(e)



######################################################################################
# Function to extract songs and artists from a playlist
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


#######################################################################################



#***********************************Music Bot Setup****************************************


ydl_opts = {
    'format': 'bestaudio/best',  # Choose the best audio format
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = yt_dlp.YoutubeDL(ydl_opts)

class YTDLSource(discord.PCMVolumeTransformer):
    def _init_(self, source, *, data, volume=0.5):
        super()._init_(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ''

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # Take the first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename




#***********************************************Music Bot Commands********************************************************


@bot.tree.command(name='play')
async def play(interaction: discord.Interaction): 
    pause_func = 0
    p = 1
    channel = interaction.user.voice.channel
    channel_id = bot.get_channel(interaction.channel_id)
    duration_in_seconds = 0
    try:
        await channel.connect()
    except:
        pass   

        #await interaction.channel.(embed=embed)
    @tasks.loop(seconds=10)
    async def play_music():
        for a in q:
                try:
                    await channel.connect()
                except:
                    pass
    
    
                server = interaction.user.guild
                voice_channel = server.voice_client

                url = a['result'][0]['link']
                title = a['result'][0]['title']
                filename = await YTDLSource.from_url(url, loop=bot.loop)
                channel_name = a['result'][0]['channel']['name']
                embed = discord.Embed(title=f'Now Playing: {title}', description=channel_name)
                embed.set_image(url=a['result'][0]['thumbnails'][0]['url'])


                try:
                    voice_channel.play(discord.FFmpegPCMAudio(executable = 
                                                          "C:\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"
                                                          , source=filename))
            
                    q.pop(0)
                    try:
                        try:
                            try:
                                await interaction.response.send_message(embed=embed)
                            except:
                                await channel_id.send(embed=embed)
                            
                        except:
                            await interaction.edit_original_response(embed=embed)
                    except:
                        pass

                

                except Exception:
                    print(Exception)


    play_music.start()
        
    @tasks.loop(seconds=15)
    async def restart_player():
            try:
                play_music.stop()
                play_music.start()
            except:
                pass

    restart_player.start()
              

#queue

@bot.tree.command(name='add_q')
@app_commands.describe(search = "search")
async def add_q(interaction: discord.Interaction, search:str):
    """Adds song to queue"""

    embed = discord.Embed(title=f"**Searching For:** {search}", description=("This might take a while."))
    await interaction.response.send_message(embed=embed)
    try:
        videosSearch = VideosSearch(search, limit=1)
        url = videosSearch.result()['result'][0]['link']
        title = videosSearch.result()['result'][0]['title']
        filename = await YTDLSource.from_url(url, loop=bot.loop)
        channel_name = videosSearch.result()['result'][0]['channel']['name']
        embed = discord.Embed(title=f'Added to queue : {title}', description=channel_name)
        embed.set_image(url=videosSearch.result()['result'][0]['thumbnails'][0]['url'])
        await interaction.edit_original_response(embed=embed)
        q.append(videosSearch.result())
    except Exception:
        print(Exception)



#add Spotify Playlist
        

@bot.tree.command(name='add_spoti_playlist')
@app_commands.describe(playlist = "link")
async def add_q(interaction: discord.Interaction, playlist:str):
    """Adds playlist to queue"""
    # Replace with your playlist ID
    playlist_id = playlist

    # Extract the tracks
    tracks = get_playlist_tracks(playlist_id)

    # Create an array of song and artist names
    songs_artists_array = [{'song': track['track']['name'], 'artist': track['track']['artists'][0]['name']} for track in tracks]

    # Print the array
    playlistss = []
    for item in songs_artists_array:
        playlistss.insert(playlistss.__len__(), f'{item['song']} - {item['artist']}')
    #    print(f"Song: {item['song']}, Artist: {item['artist']}")


    print(playlistss)

    embed = discord.Embed(title=f"**Adding playlist to Queue!**", description=("This might take a while."))
    await interaction.response.send_message(embed=embed)
    try:
        for item in playlistss:
            videosSearch = VideosSearch(item, limit=1)
            url = videosSearch.result()['result'][0]['link']
            title = videosSearch.result()['result'][0]['title']
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            channel_name = videosSearch.result()['result'][0]['channel']['name']
            q.append(videosSearch.result())
        embed = discord.Embed(title=f'Your updated queue : {q}', description=f"Added by {interaction.user.name}")
        #embed.set_image(url=videosSearch.result()['result'][0]['thumbnails'][0]['url'])
        await interaction.edit_original_response(embed=embed)
            
    except Exception:
        print(Exception)


        


@bot.tree.command(name='remove_q')
@app_commands.describe(queue_number = "Serial Number in Queue")
async def remove_q(interaction: discord.Interaction, queue_number:int):

    qq = q.pop(queue_number - 1)
    title = qq['result'][0]['title']
    channel_name = qq['result'][0]['channel']['name']
    embed = discord.Embed(title=f'Deleted from queue : {title}', description=channel_name)
    await interaction.response.send_message(embed=embed)






@bot.tree.command(name='show_queue')
async def show_queue(interaction: discord.Interaction):
    """Shows the queue"""
    if len(q) == 0:
        await interaction.response.send_message('The queue is empty.')
    else:
        n=1
        qq = ''
        for i in q:
            #print(i)
            title = i['result'][0]['title']
            qq = qq + f'{n}. {title} \n'
            n += 1 



        embed = discord.Embed(title=f'Queue', description=qq)
        await interaction.response.send_message(embed=embed)







#join

@bot.tree.command(name='join')
async def join(interaction: discord.Interaction):
    """Joins the Voice Channel the user is in"""
    if not interaction.user.voice:
        await interaction.response.send_message("{} is not connected to a voice channel".format(interaction.user.name))
        return
    else:
        channel = interaction.user.voice.channel
        await interaction.response.send_message(f"Joined!")
        
    await channel.connect()



#pause
@bot.tree.command(name='pause')
async def pause(interaction: discord.Interaction):
    """Pauses the song"""
    voice_client = interaction.user.guild.voice_client
    if voice_client.is_playing():
        await interaction.response.send_message(f"Paused!")
        pause_func = 1
        voice_client.pause()
    else:
        await interaction.response.send_message("The bot is not playing anything at the moment.")
    



#resume
@bot.tree.command(name='resume')
async def resume(interaction: discord.Interaction):

    """Resumes paused song"""
    voice_client = interaction.user.guild.voice_client
    if voice_client.is_paused():
        await interaction.response.send_message(f"Resumed!")
        voice_client.resume()
        pause_func = 0
    else:
        await interaction.response.send_message("The bot was not playing anything before this. Use play_song command")
    



#leave



@bot.tree.command(name='leave')
async def leave(interaction: discord.Interaction):
    """Leaves Voice Channel"""
    voice_client = interaction.user.guild.voice_client
    if voice_client.is_connected():
        await interaction.response.send_message(f"Disconnected!")
        await voice_client.disconnect()
    else:
        await interaction.response.send_message("The bot is not connected to a voice channel.")
    



#skip

@bot.tree.command(name='skip')
async def skip(interaction: discord.Interaction):
    """Skips the song"""
    voice_client = interaction.user.guild.voice_client
    if voice_client.is_playing():
        await interaction.response.send_message(f"Skipped!")
        voice_client.stop()
        
        
    else:
        await interaction.response.send_message("The bot is not playing anything at the moment.")









#stop




@bot.tree.command(name='stop')
async def stop(interaction: discord.Interaction):
    """Stops the Playback"""
    voice_client = interaction.user.guild.voice_client
    if voice_client.is_playing():
        await interaction.response.send_message(f"Stopped!")
        voice_client.stop()
        q.clear()
        
        
    else:
        await interaction.response.send_message("The bot is not playing anything at the moment.")





#*****************************Calculate time left until a specific date*********************
def calculate_time_left():
    target_date = datetime.datetime(2023, 8, 17)
    current_time = datetime.datetime.now()
    time_left = target_date - current_time
    return time_left

#************************************Timer task***************************************
@tasks.loop(seconds=60)  # Run the task every 60 seconds
async def update_status():
    time_left = calculate_time_left()
    #await bot.change_presence(activity=discord.Game(name=f"Countdown: {str(time_left)}"))
    await bot.change_presence(activity=discord.Game(name=f"V3"))




#########################################################################################




# Purge Command
@bot.tree.command(name = "avater")
async def purge(interaction: discord.Interaction):
        """Sends user avatar"""

        embed = discord.Embed(
            colour = 0xEEE600,
            title = f"{interaction.user.name}'s Avatar."
        )
        embed.set_footer(text=f"ID: {interaction.user.id}")
        embed.set_image(url = f"{interaction.user.avatar}")
        await interaction.response.send_message(embed=embed)






#***************************************Mod Commands**********************************************


# Purge Command
@bot.tree.command(name = "purge")
@app_commands.describe(count = "How many Message(s) should I purge?")
@app_commands.checks.has_permissions(manage_messages = True, administrator=True)
async def purge(interaction: discord.Interaction, count:int):
    await interaction.response.send_message(f"Deleting {count} messages" , ephemeral = False)
    await interaction.channel.purge(limit=count,reason=None)



# Ban command
@bot.tree.command(name="ban")
@app_commands.describe(user="The user to ban", reason="Reason for banning")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    if interaction.guild_permissions.ban_members:
        await user.ban(reason=reason)
        await interaction.response.send_message(f"Banned {user.mention}")
    else:
        await interaction.response.send_message("You don't have permission to ban members")

# Unban command
@bot.tree.command(name="unban")
@app_commands.describe(user="The user to unban")
async def unban(interaction: discord.Interaction, user: str):
    if interaction.guild_permissions.ban_members:
        banned_users = await interaction.guild.bans()
        member_name, member_discriminator = user.split("#")

        for ban_entry in banned_users:
            banned_user = ban_entry.user

            if (banned_user.name, banned_user.discriminator) == (member_name, member_discriminator):
                await interaction.guild.unban(banned_user)
                await interaction.response.send_message(f"Unbanned {banned_user.mention}")
                return

        await interaction.response.send_message("Member not found in the ban list")
    else:
        await interaction.response.send_message("You don't have permission to unban members")

# Kick command
@bot.tree.command(name="kick")
@app_commands.describe(user="The user to kick", reason="Reason for kicking")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    if interaction.guild_permissions.kick_members:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {user.mention}")
    else:
        await interaction.response.send_message("You don't have permission to kick members")




bot.run("")







#'uploader_id': self._search_regex(r'/(?:channel|user)/([^/?&#]+)', owner_profile_url, 'uploader id') if owner_profile_url else None,
