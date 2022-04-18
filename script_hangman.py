#!/usr/bin/env python
# coding: utf-8

# In[2]:


#librerias 
from bs4 import BeautifulSoup
import requests
import numpy as np 
import matplotlib.pyplot as plt 
import unidecode
import re 
import telebot 


# In[9]:


HANGMANPICS = ['''
  +------+
  |      |
         |
         |
         |
         |
=========''', '''
  +------+
  |      |
 O     |
         |
         |
         |
=========''', '''
  +------+
  |      |
 O     |
  |      |
         |
         |
=========''', '''
  +------+
  |      |
 O     |
 /|     |
         |
         |
=========''', '''
  +------+
  |      |
 O     |
 /|\    |
         |
         |
=========''', '''
  +------+
  |      |
 O     |
 /|\    |
 /       |
         |
=========''', '''
  +------+
  |      |
 O     |
 /|\    |
 / \     |
         |
=========''']


# In[10]:


#el diccionario de palabras lo vamos a sacar de 
#https://es.wiktionary.org/wiki/Ap%C3%A9ndice:1000_palabras_b%C3%A1sicas_en_espa%C3%B1ol  
#con webscraping
url="https://es.wiktionary.org/wiki/Ap%C3%A9ndice:1000_palabras_b%C3%A1sicas_en_espa%C3%B1ol  "
r=requests.get(url)
soup=BeautifulSoup(r.content,parser="html.parser")


# In[11]:


lis=soup.find_all("li",class_="")
palabras=[]
for i in lis:
    try:
        if (len(i.a.text)>=6 and len(i.a.text.split())==1):
            palabras.append(i.a.text)
        else:
            pass
    except:
        pass
#quito las ultimas 4 porque parecen un eror o algo
palabras=palabras[:-4]
palabras=[unidecode.unidecode(i).lower() for i in palabras]
palabras


# In[12]:


#luego hacemos las funciones necesarias para que no completen los huevos de letras 

def complete_letters(letters,word):
    word=list(word)
    cuales=[True if i in letters else False for i in word]
    final=[word[i] if cuales[i] else "_ " for i in range(len(cuales))]
    return "".join(final)


# In[13]:


#el bot tiene que tener diferentes stages, y debe ir evolucionando conforme se juega
#y además saber cuando se termina 
KEY="5125128580:AAEfu8BO-mJvYYOI2hX8C8wo-EDF1AhqioA"
bot = telebot.TeleBot(KEY, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

#vamos a tener muchas callbacks pero solo se activaran cuando se le indique


 



#luego al adivinar se deben de pasar las letras una a una 
#pero si se pasa algo más largo de debe de detectar la palabra.

palabra=palabras[np.random.randint(0,len(palabras))]
jugando=False
letras=[]
hang_count=0
intentos_adiv=0
intentos_adiv_max=2


#primero debemos empezar
@bot.message_handler(commands=["start"])
def empezar(message):
    global jugando
    global palabra
    global palabras
    global letras
    global hang_count
    global intentos_adiv
    
    if jugando == False:
        jugando=True
        bot.send_message(message.chat.id, "Este es el juego del ahorcado.\n Para pedir letra simplemente escribela en el chat. \n Y para adivinar la palabra pon: 'Respuesta: {la palabra}'\n Y tienes 2 intentos.")
    elif jugando == True:
        bot.send_message(message.chat.id, "Reiniciamos el juego")
    letras=[]
    hang_count=0
    intentos_adiv=0
    intentos_adiv_max=2
    palabra=palabras[np.random.randint(0,len(palabras))]
    print(letras,palabra,complete_letters(letras,palabra))
    bot.send_message(message.chat.id, f"La palabra a adivinar es: \n {complete_letters(letras,palabra)}")
    bot.send_message(message.chat.id, f"{HANGMANPICS[0]}")





def enter_oneletter(message):
    x=message.text
    #funcion que activa la respueta si estamos jungando y se ha enviado una letra
    global jugando
    if jugando and len(x.strip())==1 and x.strip().isalpha():
        return True
    else:
        return False

@bot.message_handler(func=enter_oneletter)
def oneletter(message):
    x=message.text
    global palabra
    global letras
    global hang_count
    #entra si le he pasado una letra y estamos jugando

    #comprobamos si esta la letra en la palabra y sino sumamos una al moñeco
    if x.strip().lower() in letras:
        bot.send_message(message.chat.id, "Esa letra ya la ha dicho. Di otra venga.")

    elif x.strip().lower() in list(palabra):
        #si esta entonces palante y no sumamos
        letras.append(unidecode.unidecode((x.strip().lower())))
        
        bot.send_message(message.chat.id, f"La letra sí está, la palabra queda así: \n {complete_letters(letras,palabra)}")
        print(letras,palabra,complete_letters(letras,palabra))

    else:
        letras.append(unidecode.unidecode((x.strip().lower())))

        #si no esta sumamos una y printeamos
        hang_count+=1
        bot.send_message(message.chat.id, f"Esa letra NO está en la palabra: \n {complete_letters(letras,palabra)}")

        #comprobacion de que no hemos llegado al final de intentos
        bot.send_message(message.chat.id, f"{HANGMANPICS[hang_count]}")

        if hang_count>=6:
            #ha perdido
            jugando=False
            bot.send_message(message.chat.id,f"Has perdido, escribe '/start' para empezar una nueva partida.La palabra era '{palabra}'.")
            


#y si nos dice la palabra pues pasamo con eso a ver si la acierta
def enter_word(message):
    x=message.text
    global palabra
    global jugando
    #si metemos Respuesta: palabra
    #entonces comprobamos
    regex_aux=re.findall("^(.+):",x)
    if regex_aux:
        start_aux=regex_aux[0].lower().strip()
        intento_aux=re.findall(":(.+)$",x)[0]
        if intento_aux:
            palabra_intento=intento_aux.lower().strip()
        else:
            palabra_intento=None
        if jugando and len(x.strip())!=1 and start_aux=="respuesta" and palabra_intento is not None:
            return True
        else:
            return False
    else:
        return False
    
@bot.message_handler(func=enter_word)
def word(message):
    x=message.text
    global palabra
    global intentos_adiv
    #comprobamos si la palabra es
    palabra_intento=re.findall(":(.+)$",x)[0].lower().strip()
    if palabra_intento == palabra:
        #si es, terminamos y todo guay, se reinicia todo y damos la oportunidad de volver a empezar
        bot.send_message(message.chat.id, "Muy bien, la has adivinado, si quieres jugar otra vez pon '/start'")
        jugando=False

    else:
        #si no es, sumamos uno a lo de los intentos y le avisamo que no es.
        intentos_adiv+=1
        bot.send_message(message.chat.id, f"NO! ERROR, MAL!!, {palabra_intento} NO ES LA PALABRA.")

        #si no la a avinado y ya estamos en el máximo le avisamo y volvemos a comentar
        if intentos_adiv>=intentos_adiv_max:
            #terminamos
            jugando=False
            bot.send_message(message.chat.id, "Has agotado los intentos para adivinar la palabra, se reiniciará el juego.")

        

#tenemos que tener una funcion que compruebe que no se han pasado los intentos de letras y de palabras 





# In[14]:


bot.polling()


# In[ ]:





# In[ ]:




