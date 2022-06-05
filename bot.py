import discord
from discord.ext import commands
from discord.ui import Button, View
from config import TOKEN, ID,FIRSTROLE,days
from my_sql_db import mysql
from datetime import datetime, date, time
import random
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

def get_kind():
    f = open('kind.txt', encoding='utf-8', mode='r')
    var=f.read().split(',')
    f.close()
    return var[random.randint(0, 3)]
@bot.event
async def on_ready():
    print('bot connected')

@bot.command(pass_context=True)
async def helpme(ctx):
    await ctx.send('''
    !report отправить 
!need показать нужные дисциплины для сдачи    
!week - показать расписание на неделю
    ''')
    if ctx.author.roles[1]=='Администратор':
        await ctx.send('''
        !clear(adm) - очищение в канале выдача-ролей
        !start(adm) - загрузка кнопок
            ''')

# add_role_auto
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, id=FIRSTROLE)  # выдача роли
    await member.add_roles(role)
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def clear(ctx):
    if str(ctx.channel) == 'выдача-ролей':
        await ctx.channel.purge(limit=1000)
        await ctx.channel.send('Для получения роли напишите свои ФИО (в порядке: Фамилия, Имя, Отчество)')

@bot.command(pass_context=True)
async def report(ctx,text:str):
    print('Сообщение об ошибке: ',text)

@bot.command(pass_context=True)
async def need(ctx,text:str=''):
    get = mysql(f"SELECT discipline FROM directs WHERE direct='{text}'")
    if len(get)>0:
        print(get)
        await ctx.send(f'Тебе нужно будет сдать: {get[0][0]}')
    else:
        get = mysql(f"SELECT direct FROM directs")
        text = ''
        for i in get:
            text += str(i[0]) + ', '
        await ctx.send('напишите !need и номер группы: '+text)
        return
@bot.command(pass_context=True)
async def week(ctx,text:str=''):
    text=text.lower()
    dayweek=datetime.today().weekday()
    if text=='today':
        get = mysql(f"SELECT {days[dayweek]} FROM directs WHERE direct='{ctx.author.roles[1]}'")
        if str(get[0][0]).startswith('0:00'):
            await ctx.send(f"Сегодня: Отдых")
            return
        data=datetime.today().time()
        if int(str(get[0][0])[0:int(str(get[0][0]).find(':'))])<int(str(data)[0:int(str(data).find(':'))]):
            await ctx.send(f"Сегодня начало в: {get[0][0]}")
        else:
            if dayweek==6:
                dayweek=1
            else:dayweek+=1
            print('was')
            get = mysql(f"SELECT {days[dayweek]} FROM directs WHERE direct='{ctx.author.roles[1]}'")
            await ctx.send(f"Завтра начало в: {get[0][0]}")
    elif text=='' or text==' ':
        print('empty')
        get = mysql(f"SELECT monday,tuesday,wednesday,thursday,friday,saturday,sunday FROM directs WHERE direct='{ctx.author.roles[1]}'")
        final=[]
        out= """
        Timetable:
        {0:<10}  {1:<10}  {2:<10}  {3:<10} {4:<10}  {5:<10}  {6:<10}
        {7:<10}  {8:<10}  {9:<10}  {10:<10} {11:<10}  {12:<10}  {13:<10}"""
        for i in range(0,len(get[0])):
            if str(get[0][i]).startswith('0:00'):
                final.append("Отдых")
            else:
                final.append(str(get[0][i]))
        await ctx.send(out.format(days[0],days[1],days[2],days[3],days[4],days[5],days[6],final[0],final[1],final[2],final[3],final[4],final[5],final[6]))
    else:
        await ctx.send("напишите !week и ['today'/оставить пустым]")
    return

class MyView(View):
    @discord.ui.button(label="Похвалить", style=discord.ButtonStyle.green)
    async def button_callback(self,button,interaction):
        button.disabled =True
        print('first')
        await interaction.response.send_message(get_kind())

    @discord.ui.button(label="Расписание", style=discord.ButtonStyle.danger)
    async def danger_button_callback(self, button, interaction):
        await interaction.user.send("Расписание твоих дисциплин!", file=discord.File('image/table.jpg'))
        await interaction.response.send_message('sent')
        await interaction.channel.purge(limit=1)

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
#@commands.has_role("Admin")
async def start(ctx):
    await ctx.channel.purge(limit=1000)
    view=MyView()
    await ctx.send('!helpme - команда для помощи',view=view)
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    msg = message.content.lower()
    # при написании ФИО в чате выдача-ролей
    if str(message.channel) == 'выдача-ролей':

        PD=message.content.split()
        if not message.content.startswith('!'):
            if len(PD)!=3:
                await message.channel.purge(limit=1)
                return
            if len(mysql(f"SELECT * FROM users WHERE first='{PD[1]}' and middle='{PD[2]}' and last='{PD[0]}'"))>0:
                role=mysql(f"SELECT * FROM users WHERE first='{PD[1]}' and middle='{PD[2]}' and last='{PD[0]}'")
                await message.channel.send(embed=discord.Embed(description=f"Пользователь {message.author} ожидает получения роли ``{role[0][4]}``!",color=0x0c0c0c))
                print(f'выдать роль {message.author}')
    await bot.process_commands(message)

bot.run(TOKEN)


#"SELECT * FROM users LEFT JOIN directs ON users.direct = directs.direct"