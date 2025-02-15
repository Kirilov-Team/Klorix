import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import re
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    """Loads settings from the settings.json file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}  # Return empty dictionary if no settings are found

def save_settings(settings):
    """Saves settings to the settings.json file."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)


def get_installed_models():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, check=True,
            encoding="utf-8",
            errors="replace"
        )
        lines = result.stdout.splitlines()
        models = [line.split()[0] for line in lines if line.strip() and not line.startswith("MODEL")]
        return models
    except Exception as e:
        print(f"Error getting installed models: {e}")
        return []


def download_model(model_name, output_callback):
    try:
        output_callback(f"Starting download for model: {model_name}\n")
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        for line in process.stdout:
            output_callback(line)
        process.wait()
        if process.returncode == 0:
            output_callback(f"Download of '{model_name}' completed.\n")
        else:
            output_callback(f"Error: Download returned code {process.returncode}\n")
    except Exception as e:
        output_callback(f"Error downloading model: {e}\n")


def chat_with_model(model, prompt, output_callback, timeout):
    """Sends user input to the Ollama model and streams back the response."""
    try:
        output_callback(f"User: {prompt}\n")
        process = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
            encoding="utf-8",  # Ensure UTF-8 encoding
            errors="replace"   # Replace unsupported characters instead of crashing
        )

        if process.stdin:
            process.stdin.write(prompt + "\n")
            process.stdin.flush()
            process.stdin.close()

        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                cleaned_line = re.sub(r'<think>.*?</think>', 'Thinking...', line.rstrip("\n"))
                output_callback(cleaned_line + "\n")

        process.stdout.close()
        returncode = process.wait(timeout=timeout)

        if returncode != 0:
            err = process.stderr.read() if process.stderr else "No error message captured."
            output_callback(f"\nError: Process returned code {returncode}: {err}\n")

    except Exception as e:
        output_callback(f"\nException: {e}\n")


class OllamaChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Klorix")
        self.geometry("900x500")
        self.current_model = None

        # Load settings
        self.settings = load_settings()
        self.auto_refresh = self.settings.get("auto_refresh", True)
        self.timeout = self.settings.get("timeout", 30)
        self.default_model = self.settings.get("default_model", None)

        # Main frame for UI components
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Installed Models Section
        ttk.Label(self.main_frame, text="Installed Models:").pack(anchor=tk.W)
        self.model_listbox = tk.Listbox(self.main_frame, height=6)
        self.model_listbox.pack(fill=tk.X, pady=(0, 10))
        self.model_listbox.bind("<<ListboxSelect>>", self.on_model_select)

        # Button to open the "Download New Model" window
        self.download_new_button = ttk.Button(
            self.main_frame, text="Download New Model", command=self.open_download_window
        )
        self.download_new_button.pack(pady=(0, 10))

        # Button to open the settings window
        self.settings_button = ttk.Button(
            self.main_frame, text="Settings", command=self.open_settings_window
        )
        self.settings_button.pack(pady=(0, 10))

        # Chat Display Section
        ttk.Label(self.main_frame, text="Chat Conversation:").pack(anchor=tk.W)
        self.chat_display = scrolledtext.ScrolledText(self.main_frame, state='disabled', wrap=tk.WORD, height=10)
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Input Section for user prompt
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        self.input_entry = ttk.Entry(self.input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Initial model refresh and periodic auto-refresh
        self.refresh_models()
        if self.auto_refresh:
            self.auto_refresh_models()

    def append_chat(self, text):
        """Appends text to the chat conversation display."""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, text)
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def refresh_models(self):
        """Refreshes the installed models list and excludes the model named 'NAME'."""
        self.model_listbox.delete(0, tk.END)
        models = get_installed_models()
        models = [model for model in models if model != "NAME"]
        for model in models:
            self.model_listbox.insert(tk.END, model)
        if models:
            self.current_model = self.default_model or models[0]
            self.model_listbox.selection_set(0)

    def auto_refresh_models(self):
        """Automatically refresh the model list every 5 seconds."""
        self.refresh_models()
        self.after(5000, self.auto_refresh_models)  # Call this method again after 5 seconds

    def on_model_select(self, event):
        """Handler for when a model is selected from the listbox."""
        selection = self.model_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_model = self.model_listbox.get(index)
            self.append_chat(f"Selected model: {self.current_model}\n")

    def send_message(self):
        """Sends the user prompt to the selected model and displays the response."""
        prompt = self.input_entry.get().strip()
        if not prompt:
            return
        if not self.current_model:
            messagebox.showerror("Error", "No model selected.")
            return
        self.input_entry.delete(0, tk.END)

        # Call the model in a new thread to prevent blocking the UI.
        threading.Thread(target=self.chat_with_model_thread, args=(self.current_model, prompt), daemon=True).start()

    def chat_with_model_thread(self, model, prompt):
        """Threaded function to call the model and process the response."""
        def output_callback(text):
            # Clean up any <think> tags before appending
            result = text.replace("<think>", "").replace("</think>", "")
            self.append_chat(result)
        chat_with_model(model, prompt, output_callback, self.timeout)

    def open_download_window(self):
        """Opens a new window for downloading a new model."""
        download_win = tk.Toplevel(self)
        download_win.title("Download New Model")
        download_win.geometry("400x200")

        # Label and Entry for model name input
        label = ttk.Label(download_win, text="Enter Model Name:")
        label.pack(pady=5)

        model_entry = ttk.Entry(download_win, width=40)
        model_entry.pack(pady=5)
        model_entry.focus()

        # Indeterminate Progressbar (hidden until download starts)
        progress_bar = ttk.Progressbar(download_win, mode="indeterminate")
        progress_bar.pack(pady=5, fill=tk.X, padx=10)

        # Status label to display download messages
        status_label = ttk.Label(download_win, text="")
        status_label.pack(pady=5)

        # Download button
        download_button = ttk.Button(
            download_win, text="Download",
            command=lambda: self.start_download(model_entry.get().strip(), progress_bar, status_label, download_win, download_button, model_entry)
        )
        download_button.pack(pady=5)

    def start_download(self, model_name, progress_bar, status_label, win, download_button, model_entry):
        """Starts the download in a new thread and updates the progress bar and status."""
        if not model_name:
            messagebox.showerror("Error", "Please enter a model name.")
            return

        # Disable the input controls so the user cannot interact during download
        download_button.config(state=tk.DISABLED)
        model_entry.config(state=tk.DISABLED)

        # Start the indeterminate progress bar
        progress_bar.start(10)

        def update_status(message):
            status_label.config(text=message)

        def download_thread():
            def output_callback(text):
                # Update the status label with the latest message from the download process.
                self.after(0, lambda: update_status(text.strip()))
            download_model(model_name, output_callback)
            self.after(0, finish_download)

        def finish_download():
            progress_bar.stop()
            # Refresh the installed models list in the main window.
            self.refresh_models()
            messagebox.showinfo("Download Complete", f"Download of model '{model_name}' completed.")
            win.destroy()

        threading.Thread(target=download_thread, daemon=True).start()

    def open_settings_window(self):
        """Opens a settings window to modify the settings."""
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.geometry("300x250")

        # Enable Auto-Refresh Checkbox
        auto_refresh_var = tk.BooleanVar(value=self.auto_refresh)
        ttk.Checkbutton(settings_win, text="Enable Auto-Refresh", variable=auto_refresh_var).pack(pady=10)

        # Timeout Entry
        timeout_var = tk.IntVar(value=self.timeout)
        ttk.Label(settings_win, text="Model Timeout (seconds):").pack(pady=5)
        timeout_entry = ttk.Entry(settings_win, textvariable=timeout_var, width=10)
        timeout_entry.pack(pady=5)

        # Default Model Entry
        ttk.Label(settings_win, text="Default Model:").pack(pady=5)
        default_model_entry = ttk.Entry(settings_win, width=30)
        default_model_entry.insert(0, self.default_model or "")
        default_model_entry.pack(pady=5)

        def save_settings_btn():
            # Save the settings to settings.json
            self.auto_refresh = auto_refresh_var.get()
            self.timeout = timeout_var.get()
            self.default_model = default_model_entry.get().strip()
            self.settings["auto_refresh"] = self.auto_refresh
            self.settings["timeout"] = self.timeout
            self.settings["default_model"] = self.default_model
            save_settings(self.settings)
            settings_win.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")

        # Save button
        ttk.Button(settings_win, text="Save Settings", command=save_settings_btn).pack(pady=10)

if __name__ == "__main__":
    app = OllamaChatApp()
    app.mainloop()
