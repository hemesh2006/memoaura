import tkinter as tk
import time
import threading

def show_notification(msg, bg_color="#222", fg_color="white"):
    root = tk.Tk()
    root.overrideredirect(True)  # no title bar
    root.attributes("-topmost", True)
    root.configure(bg=bg_color)

    label = tk.Label(root, text=msg, fg=fg_color, bg=bg_color, font=("Arial", 12, "bold"), padx=20, pady=10)
    label.pack()

    # position bottom right
    root.update_idletasks()
    x = root.winfo_screenwidth() - root.winfo_width() - 20
    y = root.winfo_screenheight() - root.winfo_height() - 50
    root.geometry(f"+{x}+{y}")

    root.after(3000, root.destroy)  # auto close
    root.mainloop()

# Multiple styles
threading.Thread(target=show_notification, args=("🔔 Default Notification", "#333", "white")).start()
time.sleep(1)
threading.Thread(target=show_notification, args=("✅ Success Message", "green", "white")).start()
time.sleep(1)
threading.Thread(target=show_notification, args=("⚠️ Error Occurred", "red", "white")).start()
