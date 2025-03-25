from tkinter import ttk

class NericxTheme:
    PRIMARY = "#7289DA"  # Discord Blue
    SECONDARY = "#424549"  # Discord Dark
    ACCENT = "#5b6dae"  # Dark Blue
    BACKGROUND = "#36393F"  # Discord Dark Background
    LIGHT_BACKGROUND = "#40444B"  # Discord Channel Background
    TEXT_LIGHT = "#FFFFFF"  # White
    TEXT_DARK = "#99AAB5"  # Discord Grey Text
    SUCCESS = "#43B581"  # Discord Green
    ERROR = "#F04747"  # Discord Red
    WARNING = "#FAA61A"  # Discord Orange


class NericxStyle:
    @staticmethod
    def apply_theme(root):
        style = ttk.Style()
        style.theme_use('clam') 
        
        style.configure('TFrame', background=NericxTheme.BACKGROUND)
        style.configure('TLabel', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        style.configure('TLabelframe', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        style.configure('TLabelframe.Label', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        
        style.configure('TNotebook', background=NericxTheme.BACKGROUND, borderwidth=0)
        style.configure('TNotebook.Tab', background=NericxTheme.SECONDARY, foreground=NericxTheme.TEXT_LIGHT,
                        padding=[10, 5], font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', NericxTheme.PRIMARY)],
                  foreground=[('selected', NericxTheme.TEXT_LIGHT)])
        
        style.configure('TButton', background=NericxTheme.PRIMARY, foreground=NericxTheme.TEXT_LIGHT,
                      font=('Segoe UI', 9, 'bold'), borderwidth=0, padding=5)
        style.map('TButton', background=[('active', NericxTheme.ACCENT)],
                foreground=[('active', NericxTheme.TEXT_LIGHT)])
        
        style.configure('Faded.TButton', background=NericxTheme.SECONDARY, foreground=NericxTheme.TEXT_DARK)
        style.map('Faded.TButton', background=[('active', NericxTheme.SECONDARY)],
                foreground=[('active', NericxTheme.TEXT_LIGHT)])
        
        style.configure('Success.TButton', background=NericxTheme.SUCCESS, foreground=NericxTheme.TEXT_LIGHT)
        style.map('Success.TButton', background=[('active', NericxTheme.SUCCESS)],
                foreground=[('active', NericxTheme.TEXT_LIGHT)])
        
        style.configure('TEntry', foreground=NericxTheme.TEXT_LIGHT, fieldbackground=NericxTheme.LIGHT_BACKGROUND,
                      borderwidth=0, padding=5)
        
        style.configure('TCheckbutton', background=NericxTheme.BACKGROUND, foreground=NericxTheme.TEXT_LIGHT)
        style.map('TCheckbutton', background=[('active', NericxTheme.BACKGROUND)])
        
        style.configure('TProgressbar', background=NericxTheme.ACCENT, troughcolor=NericxTheme.LIGHT_BACKGROUND, 
                      borderwidth=0, thickness=10)
        
        style.configure('TScrollbar', background=NericxTheme.LIGHT_BACKGROUND, borderwidth=0, arrowsize=12)
        style.map('TScrollbar', background=[('active', NericxTheme.PRIMARY)])
        
        style.configure('Treeview', background=NericxTheme.LIGHT_BACKGROUND, fieldbackground=NericxTheme.LIGHT_BACKGROUND,
                      foreground=NericxTheme.TEXT_LIGHT, borderwidth=0, padding=5)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10)) 
        style.configure("TCheckbutton", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))

        root.configure(background=NericxTheme.BACKGROUND)
        root.option_add("*Font", ("Segoe UI", 10))