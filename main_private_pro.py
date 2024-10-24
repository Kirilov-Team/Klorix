print("Importálás...")
from win11toast import toast
import threading
done = False


def push(txt):
    toast(txt, duration='short', audio={'silent': 'true'})


try:
    with open(f'lib/isInstalled', 'r') as a:
        escape = a.read()
    t = threading.Thread(target=push, args=("QwenCore indítása...",))
    t.start()
except:
    t = threading.Thread(target=push, args=("Nyelvi modell letöltése...",))
    t.start()

    import os
    os.system("ollama pull qwen:0.5b")

    with open(f'lib/isInstalled', 'w') as a:
        a.write(" ")




import tkinter.simpledialog
import geopy
import folium
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests as req
import pyperclip
import webbrowser as wb
from PIL import ImageGrab
import python_weather
import asyncio
import deep_translator as dt
import ollama
import subprocess
from langchain_ollama import ChatOllama
from playsound import playsound



def play_sound(path):
    playsound(path)

t = threading.Thread(target=play_sound, args=("lib/start.wav",))
t.start()


from sys import exit


print("Kész")

username = ""
loc = ""


print("[INDÍTÁS] Beszédfelismerés indítása...")

listener = sr.Recognizer()
listener.pause_threshold = 0.5



engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('rate', 180)
done = False
for voice in voices:
    # to get the info. about various voices in our PC
    if "hu" in voice.id:
        print(voice.id)
        engine.setProperty('voice', voice.id)
        done = True
    print("[INDÍTÁS] Hang telepítve!")




def talk(text):
    done = False
    engine.say(text)
    engine.runAndWait()

#talk("Szia! kvenkor vagyok!") //qwencore

try:
    with open(f'lib/escape.safeword', 'r') as a:
        escape = a.read()
except:
    talk("Szia!")
    talk("A Kvenkor projekt mesterséges intelligenciája vagyok!")
    talk("Elsőnek is, köszönöm, hogy telepítettél!")
    talk("Boldog vagyok, hogy téged is megismerhetlek!")
    talk("De elsőnek is, kérlek adj meg egy biztonsági szót, hogy tudjam, mikor kell kikapcsolnom magam!")

    t = threading.Thread(target=play_sound, args=("lib/popup.wav",))
    t.start()
    escape = tkinter.simpledialog.askstring(title="QwenCore Interface", prompt="Ha ezt a szót kimondja bezárom magam : ")
    with open(f'lib/escape.safeword', 'w') as a:
        a.write(escape)
    t = threading.Thread(target=play_sound, args=("lib/gotit.wav",))
    t.start()


llm = ChatOllama(
    model="qwen:0.5b",
    temperature=0,
    # other params...
)

async def getweather():
    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        # fetch a weather forecast from a city
        place = loc
        try:
            weather = await client.get(place)

            # returns the current day's forecast temperature (int)
            temperature = round(((weather.temperature-32)*5)/9)
            #print(weather.datetime)
            #print(weather.kind)
            time_ = datetime.datetime.now().strftime('%I:%M %p')

            talk(f"{place}ban az időjárás {dt.GoogleTranslator(source='auto', target='hu').translate(str(weather.kind))}, a hőmérséklet {temperature} fok, és az idő {datetime.datetime.now().strftime('%I:%M %p')}.")
        except:
            print("[IDŐJÁRÁS] Hiba a profil beállításaival, vagy a klienssel!")
            talk("Hiba a profil beállításaival, vagy a klienssel!")


def play(song):
    print(f'[VIDEO] {song} lejátszása')
    talk(f"{song} lejátszása!")
    pywhatkit.playonyt(song)


def weather():
    asyncio.run(getweather())


def time():
    time_ = datetime.datetime.now().strftime('%I:%M %p')
    print(f'[IDŐ] {time} van')
    talk(time_ + " van")


def who_is(person):
    print("[WIKI] Wikipédia adatok beszerzése...")
    try:
        info = wikipedia.summary(person, 1)
        print("[WIKI] " + person + " : " + dt.GoogleTranslator(source='auto', target='hu').translate(info))
        talk(dt.GoogleTranslator(source='auto', target='hu').translate(info))
    except:
        response = ollama.generate(model='llama2',
                                   prompt=f"{dt.GoogleTranslator(source='auto', target='en').translate(f'who is / what is {person}')} (only answer in short answers, not anything else)")

        response_ = response['response']
        print(dt.GoogleTranslator(source='auto', target='hu').translate(response_))
        talk(dt.GoogleTranslator(source='auto', target='hu').translate(response_))


def joke():
    joke = pyjokes.get_joke()
    print("[VICC] " + dt.GoogleTranslator(source='auto', target='hu').translate(joke))
    talk(dt.GoogleTranslator(source='auto', target='hu').translate(joke))


def map_():
    print("[TÉRKÉP] Térkép megnyitása!")
    talk("Térkép megnyitása az Ön hozzávetőleges tartózkodási helyéhez!")

    object = geopy.Nominatim(user_agent="Nikki")
    location = loc
    h = object.geocode(location)

    map = folium.Map(location=[h.latitude, h.longitude], zoom_start=13)
    folium.Marker([h.latitude, h.longitude], popup='My Home').add_to(map)
    map.save("lib/map/map.html")
    os.system(f'start lib/map/map.html')


def search_for(query):
    print('[GOOGLE] Rákeresés : ' + query)
    talk(f"Rákeresés a {query}re")
    pywhatkit.search(query)


def open_app(app):
    print(f'[OPEN] {app} megnyitása')
    talk('{app} megnyitása')
    os.system(f'start {app}')


def shut_up():
    print("[SZÜNET] Foka leállítva!")
    talk('Oké, akkor megyek.')
    while not take_command() == "fóka":
        pass
    print("[SZÜNET] Foka is visszatért!")
    talk("Visszatértem!")


def screenshot_this():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    screenshot.close()
    print("[KÉPERNYŐKÉP] Képernyőkép elkészítve!")
    talk("Képernyőkép elmentve!")


def ip():
    url: str = 'https://checkip.amazonaws.com'
    requ = req.get(url)
    ip: str = requ.text
    print(ip)
    pyperclip.copy(ip)
    print("[IP] IP cím kimásolva!")
    talk("IP cím kimásolva!")


def play_music():
    print("[ZENE] Zene megnyitása!")
    talk("Igenis!")
    wb.open("https://www.youtube.com/watch?v=N9qYF9DZPdw")


def clone():
    talk("Ez a funkció még nem elérhető! ")
    # talk("Oké, mondd meg a forrás nevét")
    # project_name = input("[PROJEKT KLÓNOZÁSA] Forrás neve : ")
    # project_name = askstring('Foka', 'Forrás neve')
    # source_dir = f"D:/$_Docs/python/PycharmProjects/{project_name}"
    # talk("Kérem add meg a klón nevét!")
    # clone_name = input("[PROJEKT KLÓNOZÁSA] Klón neve : ")
    # clone_name = askstring('Foka', 'Klón neve')
    # destination_dir = f"D:/$_Docs/python/PycharmProjects/{clone_name}"
    # try:
        # talk("Klónozás elkezdése!")
        # print("[PROJEKT KLÓNOZÁSA] Klónozás elkezdése...")
        # shutil.copytree(source_dir, destination_dir, dirs_exist_ok=False)
        # talk("Projekt sikeresen klónozva!")
        # print("[PROJEKT KLÓNOZÁSA] Siker!")
    # except:
        # talk("Hiba!")
        # print("[PROJEKT KLÓNOZÁSA] Hiba!")


def create():
    talk("Ez a funkció nem elérhető!")

    # talk("Oké, kérlek mondd meg az új projekt nevét!")
    # project_name = input("[PROJEKT LÉTREHOZÁSA] Projekt név : ")
    # project_name = askstring('Foka', 'Projekt neve')
    # source_dir = r"D:/$_Docs/python/PycharmProjects/default_project"
    # destination_dir = f"D:/$_Docs/python/PycharmProjects/{project_name}"
    # try:
        # print("[PROJEKT LÉTREHOZÁSA] Projekt létrehozása...")
        # talk("Projekt létrehozása...")
        # shutil.copytree(source_dir, destination_dir, dirs_exist_ok=False)
        # print("[PROJEKT LÉTREHOZÁSA] KÉSZ!")
        # talk("Kész!")
    # except:
        # print("[PROJEKT LÉTREHOZÁSA] Hiba!")
        # talk("Hiba!")

def take_command():
    if True:
        try:
            with sr.Microphone() as source:
                audio = listener.listen(source)
                command = listener.recognize_google(audio, language="hu-HU")  # language="hu-HU"
                command = command.lower()
                print(f"Észlelt szöveg : {command}")
                if command != "" and command:
                    return command
                else:
                    command = ""
                    print("Nothing")
        except sr.UnknownValueError:
            command = ""
            print("Nothing")
            #talk("Hiba történt!")
        except sr.RequestError:
            talk("Hiba történt a szolgáltató elérésekor!")
            talk("Ellenőrizze a hálózati kapcsolatot!")


def osint():
    talk("A nyílt forráskódú hírszerzés funkció jelenleg kikapcsolva.")


def close(command):
    name = command.replace("zárd be a ", "")
    name = command.replace("zárdd be a ", "")
    name = command.replace("exét", "exe")
    subprocess.call(f"TASKKILL /F /IM {name}", shell=True)
    talk(f"{name} bezárva!")


def good_morning():

    talk(f"Jó reggelt uram!")
    talk("Sajnálom, de a időjáráselőrejelzés még nem hozzáférhető")
    talk("Ideje nekilátni a munkához?")
    talk("Állok segítségére")


def close_u():
    talk("Viszlát!")
    playsound("lib/close.wav")
    subprocess.call(f"TASKKILL /F /IM QwenCore.exe", shell=True)
    exit()



def run_seal():
    command = ""
    # try:
    while command == "" or command == False:
        command = take_command()
    try:
        if escape in command:
            close_u()
        elif "időjárás" in command or "idő" in command and "milyen" in command:
            weather()
        elif 'idő' in command:
            time()
        elif 'keress rá arra hogy ' in command or 'keress rá hogy ' in command:
            command = command.replace('keress rá arra hogy ', '').replace('keress rá hogy ', '')
            search_for(command)
        elif 'nyisd meg a ' in command or 'nyissál meg egy ' in command:
            app = command.replace('nyisd meg a ', '').replace('nyissál meg egy ', '').replace('ot', '')
            open_app(app)
        elif 'maradj csöndben' in command or "kuss" in command:
            shut_up()
        elif 'képernyőkép' in command:
            screenshot_this()
        elif "ip" in command:
            ip()
        elif "zene" in command or "zenét" in command:
            play_music()
        else:
            t = threading.Thread(target=play_sound, args=("lib/gotit.wav",))
            t.start()
            if True:
                print("Generating response...")
                prompt2 = dt.GoogleTranslator(source='hu', target='en').translate(command)
                text = prompt2
                messages = [
                    (
                        "system",
                        f"{text}",
                    ),
                    ("human", f"{text}, short"),
                ]
                ai_msg = llm.invoke(messages)
                result = dt.GoogleTranslator(source='en', target='hu').translate(ai_msg.content)
                print(result)
                talk(result)
                print("done")
            command = None
    except:
        pass



talk(f"Sikeres indítás.")
talk(f"Elkezdhetsz beszélni.")


while True:
    run_seal()



