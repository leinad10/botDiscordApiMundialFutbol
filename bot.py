# This example requires the 'message_content' intent.
import os
import sqlite3
from urllib import response
import discord
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv
import json
from table2ascii import table2ascii

con = sqlite3.connect("quihago.db")
cur = con.cursor()
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
intents = discord.Intents.all()
load_dotenv() 
intents = discord.Intents.default()
intents.message_content = True

@bot.command()
async def test(ctx, arg):
    await ctx.message.send(arg)
    print('aja')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
     
@client.event
async def on_message(message):
    
    if message.author == client.user:
        return
    if message.content.startswith('!registro'):
        id = message.author.id
        if len(message.content.split(" ", 1)) == 1 or len(message.content.split(" ")) >= 6 :
            print("aja")
            await message.channel.send(f"<@{id}> Para registrarte solo coloca tu informacion asi: !registro nombre email contraseña contraseña (deben ser iguales las contraseñas) ")
            
        else: 
            if len(message.content.split(" ")) > 5 :
                    
                name = message.content.split(" ")[1] + " " + message.content.split(" ")[2]
                email = message.content.split(" ")[3]
                password = message.content.split(" ")[4]
                confirmPassword = message.content.split(" ")[5]
            elif len(message.content.split(" ")) > 4 :
                name = message.content.split(" ")[1]
                email = message.content.split(" ")[2]
                password = message.content.split(" ")[3]
                confirmPassword = message.content.split(" ")[4]
            else:
                await message.channel.send(f"<@{id}> Para registrarte solo coloca tu informacion asi: !registro nombre email contraseña contraseña (deben ser iguales las contraseñas) ")

            print (id, name, email, password, confirmPassword)
                
            registro = {
                "name" : name,
                "email": email,
                "password" : password,
                "passwordConfirm" : confirmPassword
            }
            
            
            registroJSON = json.dumps(registro)
            header = {
                "Content-Type" : "application/json"
            }
            print(registroJSON)
                
            
            aja = requests.post("http://api.cup2022.ir/api/v1/user", data=registroJSON, headers=header ) 
            verga = aja.json()
            
            
            if verga["status"] == "success":
                token = verga["data"]["token"]
                print(verga["data"])
                print(token)
                await message.channel.send(f"Registro satisfactorio! Bienvenido <@{id}>")
                cur.execute("""
                        INSERT INTO users (discord_id, name, email, password, token) VALUES (?, ?, ?, ?, ?)
                    """, (id, name, email, password, token))
                con.commit()
                await message.channel.send(f"<@{id}> Escribe '!!!help' para mas informacion")
            elif verga["status"] == "error":
                if verga["message"].__contains__("valid email"):
                    await message.channel.send(f"<@{id}>Error en datos: email invalido")
                elif verga["message"].__contains__("shorter than the minimum allowed length"):
                    await message.channel.send(f"<@{id}>Error en datos: Contraseña muy corta, debe tener un minimo de 8 caracteres")
                elif verga["message"].__contains__("Password does not match"):
                    await message.channel.send(f"<@{id}>Error en datos: La confirmacion de contraseña y la contrase;a no son iguales")
                elif verga["message"].__contains__("duplicate key error collection"):
                    await message.channel.send(f"<@{id}>Ya existe un usuario con registrado con este email")
                else:
                    
                    print(verga)
    if message.content.startswith('!!help'):
        
        embed = discord.Embed(
            title="CAC",
            description="Centro de ayuda de comandos",
        )
        embed.add_field(name="!registro", value="Registra tu usuario para una mejor experiencia", inline=False)
        embed.add_field(name="!login", value="Inicia secion si ya tienes un usuario creado", inline=False)
        embed.add_field(name="!equipo", value="Ve informacion de un equipo", inline=False)
        embed.add_field(name="!partidos", value="Ve los partidos de un equipo", inline=False)
        embed.add_field(name="!grupo", value="Ve informacion de un grupo", inline=False)
        await message.channel.send(embed=embed)
    if message.content.startswith('!login'):
        id = message.author.id
        print("a")
        
        resEmail = cur.execute("SELECT email FROM users WHERE discord_id = ?", (id,))
        email = resEmail.fetchone()
        resPassword = cur.execute("SELECT password FROM users WHERE discord_id = ?", (id,))
        password = resPassword.fetchone()
        print (email)
        print (password)
        login = {
            "email" : email[0],
            "password" : password[0]
        }
        header = {
            'Content-Type' : 'application/json'
        }
        loginJSON = json.dumps(login)
        
        aja = requests.post("http://api.cup2022.ir/api/v1/user/login", data=loginJSON, headers=header)
        verga = aja.json()
        
        if verga["status"] == "success":
            token = verga["data"]["token"]
            print(verga["data"])
            print(token)
            await message.channel.send(f"Inicio de sesion Existoso! Bienvenido <@{id}>")
            cur.execute("""
                   UPDATE users
                   SET token = ?
                   WHERE discord_id = ?
                   
                   """,(token,id,))
            con.commit() 
             
        else:
            print(verga["status"])
    if message.content.startswith("!equipo "):
        team = str.lower(message.content.split(" ")[1])
        print(team)
        print("hola")
        id = message.author.id
        resToken = cur.execute("SELECT token FROM users WHERE discord_id = ?", (id,))
        tokenRaw = resToken.fetchone()
        token = tokenRaw[0]
        print(token)
        verToken = f"Bearer {token}"
        print(verToken)
        headerToken = {
            "Authorization": verToken,
            "Content-Type" : "application/json"
        } 
        print(headerToken)
        api = requests.get("http://api.cup2022.ir/api/v1/team", headers=headerToken)
        print("peo")
        verga = api.json()
        culo = verga["data"]
        equipo = []
        for x in culo:
            if str.lower(x["name_en"]) == team:
                equipo = x
        if not equipo:
            await message.channel.send(f"<@{id}> Este pais no esta en el mundial, prueba con otro")
            print ("nada") 
        else:
            grupo = equipo["groups"]
            flag = equipo["flag"]
            print (equipo["flag"])
            embed = discord.Embed(title= team.capitalize(), description=f"Grupo {grupo}")
            embed.set_thumbnail(url=flag)
            await message.channel.send(embed=embed)
        print(equipo) 
            
    if message.content.startswith("!partidos"):
        team = str.lower(message.content.split(" ")[1])
        id = message.author.id
        resToken = cur.execute("SELECT token FROM users WHERE discord_id = ?", (id,))
        tokenRaw = resToken.fetchone()
        token = tokenRaw[0]
        print(token)
        verToken = f"Bearer {token}"
        print(verToken)
        headerToken = {
            "Authorization": verToken,
            "Content-Type" : "application/json"
        } 
        print(headerToken)
        api = requests.get("http://api.cup2022.ir/api/v1/team", headers=headerToken)
        print("peo")
        verga = api.json()
        culo = verga["data"]
        equipo = []
        for x in culo:
            if str.lower(x["name_en"]) == team:
                equipo = x
        if not equipo:
            await message.channel.send(f"<@{id}> Este pais no esta en el mundial, prueba con otro")
            print ("nada") 
        idd = equipo["id"]
        fflag = equipo["flag"]
        print(idd)
        apii = requests.get("http://api.cup2022.ir/api/v1/match", headers=headerToken)
        ajaa = apii.json()
        aja = ajaa["data"]
        maTches = []
        for x in aja:
            if x["away_team_id"] == idd or x["home_team_id"] == idd:
                maTches.append(x)      
        print(maTches)
        for x in maTches:
            
            visitantGoals = x["away_score"]
            homeGoals = x["home_score"]
            visitantAnotador = x["away_scorers"]
            homeAnotador = x["home_scorers"]
            finished = x["time_elapsed"]
            visitant = x["away_team_en"]
            home = x["home_team_en"]
            Home = str.lower(home)
            date = x["local_date"]
            grupo = x["group"]
            tyype = x["type"]
            tipo = tyype.capitalize()
            print(team)
            print(Home)
            if team == Home:
                if homeGoals > visitantGoals:
                    color = 0x2ecc71
                elif homeGoals == visitantGoals:
                    color = 0xFEE75C
                else:
                    color = 0xe74c3c
            else:
                if visitantGoals > homeGoals:
                    color = 0x2ecc71
                elif homeGoals == visitantGoals:
                    color = 0xFEE75C
                else:
                    color = 0xe74c3c
            print(grupo)
            print(tyype)
            print(tipo)
            if tipo != "Group":
                grupo = ""
            embed = discord.Embed(title= f"{home} VS {visitant}" , description=f"{tipo} {grupo}", colour=color)
            embed.set_thumbnail(url=fflag)
            embed.add_field(name="Casa", value=home, inline=True)
            embed.add_field(name="Visitante", value=visitant, inline=True)
            embed.add_field(name="Date", value=date, inline=True)
            embed.add_field(name="Goles Casa", value=homeGoals, inline=False)
            embed.add_field(name="Goles Visitante", value=visitantGoals, inline=False)
            embed.add_field(name="Anotadores (casa)", value=homeAnotador, inline=True)
            embed.add_field(name="Anotadores (visitante)", value=visitantAnotador, inline=True)
            embed.add_field(name="Status", value=finished, inline=True)
            await message.channel.send(embed=embed)               
                
    if message.content.startswith("!grupo"):
        id = message.author.id
        grupo = message.content.split(" ")[1].capitalize()
        if len(grupo) == 1:
            resToken = cur.execute("SELECT token FROM users WHERE discord_id = ?", (id,))
            tokenRaw = resToken.fetchone()
            token = tokenRaw[0]
            print(token)
            verToken = f"Bearer {token}"
            print(verToken)
            headerToken = {
                "Authorization": verToken,
                "Content-Type" : "application/json"
            } 
            print(headerToken)
            api = requests.get("http://api.cup2022.ir/api/v1/standings", headers=headerToken)
            
            grupos = []
            aja = api.json()
            ajaa = aja["data"]
            for x in ajaa:
                if x["group"] == grupo:
                    grupos.append(x)  
            print(grupos)
            cadaGrupo = grupos[0]["teams"]
            equiposGroup = []
            for x in cadaGrupo:
                equiposGroup.append(x)
            print(equiposGroup)
            equipo1 = equiposGroup[0]["name_en"]
            equipo2 = equiposGroup[1]["name_en"]
            equipo3 = equiposGroup[2]["name_en"]
            equipo4 = equiposGroup[3]["name_en"]
            w1 = equiposGroup[0]["w"]
            w2 = equiposGroup[1]["w"]
            w3 = equiposGroup[2]["w"]
            w4 = equiposGroup[3]["w"]
            p1 = equiposGroup[0]["mp"]
            p2 = equiposGroup[1]["mp"]
            p3 = equiposGroup[2]["mp"]
            p4 = equiposGroup[3]["mp"]
            l1 = equiposGroup[0]["l"]
            l2 = equiposGroup[1]["l"]
            l3 = equiposGroup[2]["l"]
            l4 = equiposGroup[3]["l"]
            puntos1 = equiposGroup[0]["pts"]
            puntos2 = equiposGroup[1]["pts"]
            puntos3 = equiposGroup[2]["pts"]
            puntos4 = equiposGroup[3]["pts"]
            diferencia1 = int(w1) + int(l1)
            diferencia2 = int(w2) + int(l2)
            diferencia3 = int(w3) + int(l3)
            diferencia4 = int(w4) + int(l4)
            e1 = int(p1) - diferencia1
            e2 = int(p2) - diferencia2
            e3 = int(p3) - diferencia3
            e4 = int(p4) - diferencia4
            print(list(w1))
            output = table2ascii(
            header=["Equipos", "PJ", "PG", "PP", "PE", "Puntos"],
            body=[[equipo1, p1, w1, l1, e1, puntos1], [equipo2, p2, w2, l2, e2, puntos2],
            [equipo3, p3, w3, l3, e3, puntos3], [equipo4, p4, w4, l4, e4, puntos4]])
            await message.channel.send(f"```\n{output}\n```")
        else:
            team = str.lower(message.content.split(" ")[1])
            resToken = cur.execute("SELECT token FROM users WHERE discord_id = ?", (id,))
            tokenRaw = resToken.fetchone()
            token = tokenRaw[0]
            print(token)
            verToken = f"Bearer {token}"
            print(verToken)
            headerToken = {
                "Authorization": verToken,
                "Content-Type" : "application/json"
            } 
            print(headerToken)
            api = requests.get("http://api.cup2022.ir/api/v1/standings", headers=headerToken)
            teamApi = requests.get("http://api.cup2022.ir/api/v1/team", headers=headerToken)
        
            print("peo")
            apiJson =teamApi.json()
            fubo = apiJson["data"]
            equipo = []
            for x in fubo:
                if str.lower(x["name_en"]) == team:
                    equipo = x
            print(equipo)
            if not equipo:
                await message.channel.send(f"<@{id}> Este pais no esta en el mundial, prueba con otro")
            else:
                grupo = equipo["groups"]
            print(equipo)
            print ("nada") 
            grupos = []
            aja = api.json()
            ajaa = aja["data"]
            for x in ajaa:
                if x["group"] == grupo:
                    grupos.append(x)  
            print(grupos)
            cadaGrupo = grupos[0]["teams"]
            equiposGroup = []
            for x in cadaGrupo:
                equiposGroup.append(x)
            print(equiposGroup)
            equipo1 = equiposGroup[0]["name_en"]
            equipo2 = equiposGroup[1]["name_en"]
            equipo3 = equiposGroup[2]["name_en"]
            equipo4 = equiposGroup[3]["name_en"]
            w1 = equiposGroup[0]["w"]
            w2 = equiposGroup[1]["w"]
            w3 = equiposGroup[2]["w"]
            w4 = equiposGroup[3]["w"]
            p1 = equiposGroup[0]["mp"]
            p2 = equiposGroup[1]["mp"]
            p3 = equiposGroup[2]["mp"]
            p4 = equiposGroup[3]["mp"]
            l1 = equiposGroup[0]["l"]
            l2 = equiposGroup[1]["l"]
            l3 = equiposGroup[2]["l"]
            l4 = equiposGroup[3]["l"]
            puntos1 = equiposGroup[0]["pts"]
            puntos2 = equiposGroup[1]["pts"]
            puntos3 = equiposGroup[2]["pts"]
            puntos4 = equiposGroup[3]["pts"]
            diferencia1 = int(w1) + int(l1)
            diferencia2 = int(w2) + int(l2)
            diferencia3 = int(w3) + int(l3)
            diferencia4 = int(w4) + int(l4)
            e1 = int(p1) - diferencia1
            e2 = int(p2) - diferencia2
            e3 = int(p3) - diferencia3
            e4 = int(p4) - diferencia4
            # print(w1,w2,w3,w4,p1,p2,p3,p4)
            # print(w1[0],w1[1], w1[2])
            print(list(w1))
            # print(equipo1, equipo2,equipo3,equipo4)
            output = table2ascii(
            header=["Equipos", "PJ", "PG", "PP", "PE", "Puntos"],
            body=[[equipo1, p1, w1, l1, e1, puntos1], [equipo2, p2, w2, l2, e2, puntos2],
            [equipo3, p3, w3, l3, e3, puntos3], [equipo4, p4, w4, l4, e4, puntos4]])
            await message.channel.send(f"```\n{output}\n```")       
client.run(os.environ['TOKEN'])
