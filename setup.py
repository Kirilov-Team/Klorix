from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': ["pyttsx3", "win11toast", "tkinter.simpledialog", "geopy", "folium", "speech_recognition", "pyttsx3", "pywhatkit", "datetime", "wikipedia", "pyjokes", "requests", "pyperclip",
                              "webbrowser", "PIL", "python_weather", "asyncio", "deep_translator", "ollama", "subprocess", "langchain_ollama", "playsound"], 'excludes': []}




base = 'gui'

executables = [
    Executable('dist/main_private_pro.py', base=base, target_name = 'QwenCore', icon="app.ico")
]

setup(name='QwenCore',
      version = '3.1',
      description = 'QwenCore Hungary',
      options = {'build_exe': build_options},
      executables = executables)
