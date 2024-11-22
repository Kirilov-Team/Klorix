import threading
import time
started = False
start_time = 0


def start_timer():
    global start_time
    while not started:
        start_time += 0.1
        time.sleep(0.1)



t = threading.Thread(target=start_timer)
t.start()

print("[Starting] Initialization...")
from win11toast import toast

done = False


def push(txt):
    toast(txt, duration='short', audio={'silent': 'true'})


try:
    with open(f'lib/isInstalled', 'r') as a:
        escape = a.read()
    t = threading.Thread(target=push, args=("Klorix indítása...",))
    t.start()
except:
    t = threading.Thread(target=push, args=("Nyelvi modell letöltése...",))
    t.start()

    import os
    os.system("ollama pull qwen:0.5b")

    with open(f'lib/isInstalled', 'w') as a:
        a.write(" ")




import tkinter.simpledialog
import speech_recognition as sr
import pyttsx3
import deep_translator as dt
import subprocess
from langchain_ollama import ChatOllama
from playsound import playsound




def play_sound(path):
    playsound(path)
    




t = threading.Thread(target=play_sound, args=("lib/start.wav",))
t.start()


from sys import exit

username = ""
loc = ""


listener = sr.Recognizer()
listener.pause_threshold = 0.5

print("Speech Recognition OK")

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

print("Synthetic Voice OK")


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
    talk("Klorix vagyok!!")
    talk("Elsőnek is, köszönöm, hogy telepítettél!")
    talk("Boldog vagyok, hogy téged is megismerhetlek!")
    talk("Kérlek adj meg egy biztonsági szót, hogy tudjam, mikor kell kikapcsolnom magam!")

    t = threading.Thread(target=play_sound, args=("lib/popup.wav",))
    t.start()
    escape = tkinter.simpledialog.askstring(title="Klorix Interface", prompt="Ha ezt a szót kimondja bezárom magam : ")
    with open(f'lib/escape.safeword', 'w') as a:
        a.write(escape)
    t = threading.Thread(target=play_sound, args=("lib/gotit.wav",))
    t.start()

print("Profile OK")

llm = ChatOllama(
    model="qwen:0.5b",
    temperature=0,
    # other params...
)

print("Large Language Model OK")


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
                    print("A felhasználó nem beszél!")
        except sr.UnknownValueError:
            command = ""
            print("Beszélj hangosabban, érthetőbben!")
            #talk("Hiba történt!")
        except sr.RequestError:
            talk("A hangfelismerés a Google szolgáltatását használja.")
            talk("Ellenőrizze a hálózati kapcsolatot!")
        except:
            print("ERR")



def close_u():
    talk("Viszlát!")
    playsound("lib/close.wav")
    subprocess.call(f"TASKKILL /F /IM QwenCore.exe", shell=True)
    exit()

def generate_response(text):
    pass


def run_seal():
    command = ""
    # try:
    while command == "" or command == False:
        command = take_command()
    try:
        if escape in command:
            close_u()
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

    except:
        pass

started = True
print(f"Started in {start_time} seconds!")

talk(f"Sikeres indítás.")
talk(f"Elkezdhetsz beszélni.")


while True:
    run_seal()

generating = False



