from win11toast import toast
import threading

def push(txt):
    toast(txt, duration='short', audio={'silent': 'true'})

t = threading.Thread(target=push, args=("Klorix Indítása...",))
t.start()

import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import deep_translator as dt
from playsound import playsound
import subprocess
from langchain_ollama import ChatOllama

# Globális változók
escape_word = "exit"
recognizer = sr.Recognizer()
engine = pyttsx3.init()
llm = ChatOllama(model="qwen:0.5b", temperature=0)

# Hang beállítása
engine.setProperty('rate', 180)
voices = engine.getProperty('voices')
for voice in voices:
    if "hu" in voice.id:
        engine.setProperty('voice', voice.id)

# Beszédszintetizálás
def talk(text):
    engine.say(text)
    engine.runAndWait()

# Parancs feldolgozása (mikrofonon keresztül)
def take_command():
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio, language="hu-HU").lower()
            return command
    except (sr.UnknownValueError, sr.RequestError, Exception):
        return None

# Válasz generálása (fordítással és AI-val)
def generate_response(user_input):
    send_button.configure(state=ctk.DISABLED)
    try:
        send_button.configure(state=ctk.DISABLED)
        start_button.configure(state=ctk.DISABLED)
        prompt = dt.GoogleTranslator(source="hu", target="en").translate(user_input)
        messages = [("system", f"{prompt}"), ("human", f"{prompt}, short")]
        ai_msg = llm.invoke(messages)
        response = dt.GoogleTranslator(source="en", target="hu").translate(ai_msg.content)
        send_button.configure(state=ctk.NORMAL)
        return response
    except:
        send_button.configure(state=ctk.NORMAL)
        return "Nem sikerült választ generálni."


# GUI visszacsatolás
def indicate_listening():
    feedback_label.configure(text="🎙️ Hallgat...", text_color="green")
    root.update()

def stop_listening_feedback():
    feedback_label.configure(text="", text_color="blue")
    root.update()

# Parancs feldolgozása és válasz megjelenítése
def run_voice_command():
    global listening_active, last_response
    listening_active = True  # Jelzés, hogy hallgatásban van a rendszer
    indicate_listening()  # Vizuális visszacsatolás: Hallgat...
    command = take_command()
    stop_listening_feedback()  # Ne jelenjen meg a "Kész" üzenet, ha leáll a hallgatás
    listening_active = False  # Leállítjuk a hallgatást

    if command:

        output_box.insert(ctk.END, f"Te: {command}\n")
        if escape_word in command:
            close_application()
            start_button.configure(text="🎤 Beszédindítás")
        else:
            send_button.configure(state=ctk.DISABLED)
            start_button.configure(state=ctk.DISABLED)
            response = generate_response(command)
            output_box.insert(ctk.END, f"Klorix: {response}\n")
            output_box.yview(ctk.END)  # Auto-scroll to the latest output
            start_button.configure(text="🎤 Beszédindítás")
            talk(response)
            last_response = response  # Tároljuk az utolsó választ

    else:
        start_button.configure(text="🎤 Beszédindítás")
    send_button.configure(state=ctk.NORMAL)
    start_button.configure(state=ctk.NORMAL)

# Kilépés a programból
def close_application():
    talk("Viszlát!")
    play_sound("lib/close.wav")
    root.destroy()
    subprocess.call("TASKKILL /F /IM Klorix.exe", shell=True)
    exit()

# Hang lejátszása
def play_sound(path):
    playsound(path)

# Új funkció: Válasz ismétlésének funkciója
def repeat_last_response():
    global last_response
    if last_response:
        t = threading.Thread(target=talk, args=(last_response,))
        t.start()
    else:
        t = threading.Thread(target=talk, args=("Még nem kaptál választ!",))
        t.start()

# Szöveges bemenet kezelése
def handle_text_input():
    global last_response

    # Bemenet beolvasása
    user_input = text_input.get().strip()
    if not user_input:
        talk("Kérlek, adj meg egy parancsot szövegesen!")
        return

    # Szöveg megjelenítése az output_box-ban és mező törlése
    output_box.insert(ctk.END, f"Te: {user_input}\n")
    text_input.delete(0, ctk.END)  # Töröljük az adatokat
    output_box.yview(ctk.END)  # Auto-scroll
    send_button.configure(state=ctk.DISABLED)
    start_button.configure(state=ctk.DISABLED)

    # Válasz generálása külön szálon
    def generate_and_display_response():
        if escape_word in user_input:
            close_application()
        else:
            response = generate_response(user_input)
            output_box.insert(ctk.END, f"Klorix: {response}\n")
            output_box.yview(ctk.END)  # Auto-scroll
            talk(response)
            last_response = response  # Tároljuk az utolsó választ
            send_button.configure(state=ctk.NORMAL)
            start_button.configure(state=ctk.NORMAL)

    threading.Thread(target=generate_and_display_response, daemon=True).start()


# GUI beállítások
ctk.set_appearance_mode("dark")  # Sötét mód bekapcsolása
ctk.set_default_color_theme("dark-blue")  # Kék színű téma

root = ctk.CTk()  # CustomTkinter ablak
root.title("Klorix AI Asszisztens")
root.geometry("600x500")
root.resizable(False, False)

# Szövegkimenet
output_frame = ctk.CTkFrame(root, corner_radius=10)
output_frame.pack(fill="both", expand=True, padx=10, pady=10)

output_box = ctk.CTkTextbox(output_frame, wrap="word", width=70, height=20, font=("Arial", 11))
output_box.pack(fill="both", expand=True)

# Visszacsatolás (hallgatás)
feedback_label = ctk.CTkLabel(root, text="", font=("Arial", 12, "bold"))
feedback_label.pack(pady=5)

# Gombok
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

# Globális változó a hallgatás állapotának kezelésére
listening_active = False
last_response = ""  # Az utolsó válasz tárolása

# Gomb indítása vagy leállítása
def toggle_listening():
    global listening_active
    if listening_active:
        listening_active = False
        stop_listening_feedback()  # Töröljük a "Kész" üzenetet
        start_button.configure(text="🎤 Beszédindítás")
    else:
        threading.Thread(target=run_voice_command, daemon=True).start()
        start_button.configure(text="❌ Stop")

# Válasz ismétlés gomb
repeat_button = ctk.CTkButton(button_frame, text="🔁 Ismétlés", command=repeat_last_response)
repeat_button.grid(row=0, column=2, padx=10)

start_button = ctk.CTkButton(button_frame, text="🎤 Beszédindítás", command=toggle_listening)
start_button.grid(row=0, column=0, padx=10)

exit_button = ctk.CTkButton(button_frame, text="❌ Kilépés", command=close_application)
exit_button.grid(row=0, column=1, padx=10)

# Szöveges input mező és gomb
text_input_frame = ctk.CTkFrame(root)
text_input_frame.pack(fill="x", padx=10, pady=10)

text_input = ctk.CTkEntry(text_input_frame, placeholder_text="Írj be egy parancsot...", width=400)
text_input.grid(row=0, column=0, padx=10)

send_button = ctk.CTkButton(text_input_frame, text="📩 Küldés", command=handle_text_input)
send_button.grid(row=0, column=1, padx=10)

# Kezdeti üdvözlés
output_box.insert(ctk.END, "Klorix: Üdvözlöm!\n")

t = threading.Thread(target=talk, args=("Üdvözlöm!",))
t.start()

# GUI futtatása
root.mainloop()
