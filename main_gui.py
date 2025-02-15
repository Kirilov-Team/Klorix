import customtkinter as ctk
from langchain_ollama import ChatOllama
import threading
from tkinter import messagebox


def get_available_models():
    # Mock function to list available models
    return ["model-1", "model-2", "model-3"]


def download_model():
    model_name = model_entry.get().strip()
    if not model_name:
        messagebox.showerror("Error", "Please enter a model name!")
        return

    status_label.configure(text=f"Downloading {model_name}...")

    def download():
        try:
            chat_model = ChatOllama(model=model_name)
            status_label.configure(text=f"{model_name} downloaded successfully!")
            update_model_dropdown()
        except Exception as e:
            status_label.configure(text=f"Error: {e}")

    threading.Thread(target=download, daemon=True).start()


def chat():
    model_name = model_var.get()
    user_input = chat_entry.get().strip()
    if not model_name or not user_input:
        messagebox.showerror("Error", "Please select a model and enter a message!")
        return

    chat_history.configure(state="normal")
    chat_history.insert("end", f"You: {user_input}\n")
    chat_history.configure(state="disabled")
    chat_entry.delete(0, "end")

    def get_response():
        chat_model = ChatOllama(model=model_name)
        response = chat_model.invoke(user_input)
        chat_history.configure(state="normal")
        chat_history.insert("end", f"Bot: {response}\n")
        chat_history.configure(state="disabled")

    threading.Thread(target=get_response, daemon=True).start()


def update_model_dropdown():
    models = get_available_models()
    model_dropdown.configure(values=models)
    if models:
        model_var.set(models[0])


# GUI setup
app = ctk.CTk()
app.title("Ollama Chat")
app.geometry("500x600")

ctk.CTkLabel(app, text="Enter Model Name:").pack(pady=5)
model_entry = ctk.CTkEntry(app, width=300)
model_entry.pack(pady=5)

ctk.CTkButton(app, text="Download Model", command=download_model).pack(pady=5)
status_label = ctk.CTkLabel(app, text="")
status_label.pack(pady=5)

ctk.CTkLabel(app, text="Select Model:").pack(pady=5)
model_var = ctk.StringVar()
model_dropdown = ctk.CTkComboBox(app, variable=model_var, values=get_available_models())
model_dropdown.pack(pady=5)

chat_history = ctk.CTkTextbox(app, width=400, height=300, state="disabled")
chat_history.pack(pady=5)

ctk.CTkLabel(app, text="Enter Message:").pack(pady=5)
chat_entry = ctk.CTkEntry(app, width=300)
chat_entry.pack(pady=5)

ctk.CTkButton(app, text="Send", command=chat).pack(pady=5)

update_model_dropdown()
app.mainloop()
