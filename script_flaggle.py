import os 
import matplotlib.pyplot as plt 
import telebot 
import numpy as np 
import json
import re
import wikipedia as wk
from telebot import types

#codigo preliminar para cargar las banderas, codigos y seleccionar solo paises completos (no colonias) 
#y para no seleccionar aquellos paises con página erronea de wikipedia.

#cargamos los códigos
with open("codigos_banderas.json") as fil:
    codes=json.load(fil)
    
#cargamos los nombres de las flags
flags_dirs_aux=os.listdir("./flags/")
flags_dirs={re.findall(r"(.+)\.jpg",i)[0]:i for i in flags_dirs_aux}

#vamos a filtrar tambien aquellos con un nombre de mas de 2 palabras
flags_dirs_complete={i:{"file":flags_dirs[i],"name":codes[i]} for i in flags_dirs if (len(codes[i].split(" "))<3)}


# se escoge aleatoriamente de todas las que no tienen una barra intermedia y que tienen wikipedia
pais_codes=list(flags_dirs_complete.keys())
random_list=[i for i in pais_codes if "-" not in i]


wk.set_lang("es")

with open("codigos_paises_con_wiki.txt","r") as fil:
    final_list=fil.read().strip("\n").split("\n")

#final_list=[]
# for i in random_list:
#     nombre_aux=flags_dirs_complete[i]["name"]
#     try:
#         p=wk.page(nombre_aux)
#         if p is not None:
#             final_list.append(i)
#         else:
#             #se descarta
#             print("vacia",i,nombre_aux)
#             #pass
#     except wk.DisambiguationError as e:
#         print(e.options)
#         try:
#             p = wk.page(e.options[0])
#             if p is not None:
#                 final_list.append(i)
#             else:
#                 #se descarta
#                 print("vacia",i,nombre_aux)
#                 #pass
#         except:
#             pass
#     except:
#         print(i,nombre_aux)
#         #se descarta porque no tiene pagina de wiki
#         #pass  



pais_random=final_list[np.random.randint(0,len(final_list))]
print(pais_random)

#vamos a la lista completa y sacamos la bandera y el nombre
print(flags_dirs_complete[pais_random],final_list)



#se define el bot
KEY=
bot = telebot.TeleBot(KEY, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN


#variables para el proceso (si estamos jugando, o con una pista o que )
NO_HAY_JUEGO=True


#FUNCIONES

def resolver(palabra,guess):
    final=""
    aux=[True if i in guess.lower() else False for i in palabra.lower()]
    for i,letra in enumerate(palabra):
        if aux[i]:
            final+=f" {letra} "
        else:
            final+=" _ "
    
    return final

#empieza el juego e informamos de lo que va 
    
@bot.message_handler(commands=["start"])
def start(message):
    global idioma
    idioma="es"
    global NO_HAY_JUEGO
    NO_HAY_JUEGO=True
    #deberíamos permitir que se seleccione el idioma
    #bot.send_message(message.chat.id,"Select the lenguage (elige el idioma).")
    #esto para después....
    
    #mensaje de bienvenida
    bot.send_message(message.chat.id, "Esto es FLAGGLE, un juego donde tienes que adivinar el pais que corresponde\
    con la bandera. Tendrás 3 pistas en caso de que sea muy dificil (pero cada pista restará puntos):\n\n\
 -La primera pista es el número de letras (contando espacios en blanco) que tiene el nombre del país.\n\
 -La segunda es la primera letra.\n-Y la tercerá será un extracto de la wikipedia del país.\n\n\n\
 Cuando quieras comenzar simplemente pidelo con educación, y empezamos.")
    
    
#ahora tenemos que esperar a que nos pida empezar 
def empezar(message):
    #comprobamos tanto si lo pide por favor como si no se ha empezado aun
    pedido_por_favor=(("por favor" in message.text.lower()) | ("porfavor" in message.text.lower())|
                      ("porfa"in message.text.lower()))
    global NO_HAY_JUEGO
    if (NO_HAY_JUEGO & pedido_por_favor):
        NO_HAY_JUEGO=False
        return True
    elif NO_HAY_JUEGO:
        bot.send_message(message.chat.id,"Di la palabra mágica")
        return False
    else:
        #bot.send_message(message.chat.id,"Estas jugando ya. Si quieres reiniciar el juego escribe /start")
        return False
        
    

@bot.message_handler(func=empezar)
def empezar2(message):
    #ahora que entra dentro, podemos enviar el mensaje con la bandera y dar las opciones de 
    #respuesta
    global pais
    pais=final_list[np.random.randint(0,len(final_list))]
    photo = open(f"./flags/{flags_dirs_complete[pais]['file']}", 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()
    bot.send_message(message.chat.id, "Tienes que adivinar de que país es esta bandera.") 
    print(pais)
    bot.send_message(message.chat.id,wk.page(flags_dirs_complete[pais]["name"]).summary.split("\n")[0].replace(flags_dirs_complete[pais]["name"],"_______"))
    #bot.send_message(message.chat.id, "¿Comodines?", reply_markup=markup)    

def acierto(message):
    #veamos si estamos adivinando
    if not NO_HAY_JUEGO:
        #entonces eelegible para adivinarse
        return True
    else:
        return False
    
    
#ahora queremos ver si ha acertado
@bot.message_handler(func=acierto)
def acierto2(message):
    global respuesta
    respuesta=message.text
    nombre_completo_pais=flags_dirs_complete[pais]['name']
    if (respuesta.lower() in nombre_completo_pais.lower()) or (nombre_completo_pais.lower() in respuesta.lower()): 
        bot.send_message(message.chat.id, f"MUY BIEN!!! Lo has hecho genial, \n eres super listo!!! el pais era {nombre_completo_pais}" )  
        NO_HAY_JUEGO=True
    else:
        bot.send_message(message.chat.id, f"Lo siento pero NO!!\n{resolver(nombre_completo_pais, respuesta)}")  
        


bot.infinity_polling()
