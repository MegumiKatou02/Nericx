import tkinter as tk
from ui.app import OsuManagerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = OsuManagerApp(root)
    
    try:
        root.iconbitmap("icon.ico")
    except:
        print("Không tìm thấy file icon.ico")
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()