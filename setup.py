from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': ["pyttsx3", "win11toast", "customtkinter", "speech_recognition", "deep_translator", "playsound", "langchain_ollama", "subprocess"], 'excludes': []}




base = 'gui'

executables = [
    Executable('dist/main_gui.py', base=base, target_name = 'Klorix', icon="app.ico")
]

setup(name='Klorix',
      version = '0.0',
      description = 'Klorix',
      options = {'build_exe': build_options},
      executables = executables)
