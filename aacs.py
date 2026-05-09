import customtkinter
from customtkinter import filedialog
from CTkMessagebox import CTkMessagebox
import configparser
import shutil
import os
import sys
import ctypes
import ctypes.wintypes
from pathlib import Path

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# GUID structure required by SHGetKnownFolderPath
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]

# FOLDERID_Documents GUID: {FDD39AD0-238F-46AF-ADB4-6C85480369C7}
FOLDERID_Documents = GUID(
    0xFDD39AD0,
    0x238F,
    0x46AF,
    (ctypes.c_ubyte * 8)(0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7)
)

def get_documents_folder() -> Path:
    # Get the user's Documents folder using the modern SHGetKnownFolderPath API.
    _SHGetKnownFolderPath = ctypes.windll.shell32.SHGetKnownFolderPath
    _SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID),   # rfid
        ctypes.wintypes.DWORD,  # dwFlags
        ctypes.wintypes.HANDLE, # hToken
        ctypes.POINTER(ctypes.c_wchar_p)  # ppszPath (out)
    ]
    _SHGetKnownFolderPath.restype = ctypes.HRESULT

    path_ptr = ctypes.c_wchar_p()
    hr = _SHGetKnownFolderPath(
        ctypes.byref(FOLDERID_Documents),
        0,      # dwFlags: default behaviour
        None,   # hToken: current user
        ctypes.byref(path_ptr)
    )

    if hr != 0:
        raise OSError(f"SHGetKnownFolderPath failed with HRESULT {hr:#010x}")

    path = Path(path_ptr.value)

    # Free the memory allocated by the Shell
    ctypes.windll.ole32.CoTaskMemFree(path_ptr)

    return path


def copy_file_via_dialog(profile_name):
    # Prompt the user to select a file and then copy the file to a new folder with the name of the profile in the current working directory
    documents_path = get_documents_folder()
    print(documents_path)
    source_path = filedialog.askopenfilename(initialdir=documents_path, title="Select a file to copy")
    if not source_path:
        print("No file selected.")
        return None

    cwd = os.getcwd()
    # cwd = os.path.join(os.getcwd(), "saved_configs")
    # Specify the directory name
    directory_name = os.path.join("saved_configs", profile_name)

    # Create the directory
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
        CTkMessagebox(
            title="Unable to create profile.", 
            message="Profile " + directory_name + " already exists.", 
            justify="center", 
            font= customtkinter.CTkFont(family="Arial", weight="bold"), 
            icon="cancel",
            sound=True
        )
        return None
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
        CTkMessagebox(
            title="Unable to create profile.", 
            message="Permission denied: Unable to create " + directory_name, 
            justify="center", 
            font= customtkinter.CTkFont(family="Arial", weight="bold"), 
            icon="cancel",
            sound=True
        )
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        CTkMessagebox(
            title="Unable to create profile.", 
            message="An error occurred.", 
            justify="center", 
            font= customtkinter.CTkFont(family="Arial", weight="bold"), 
            icon="cancel",
            sound=True
        )
        return None
    
    #combine current working directory, new directory, and existing filename to create the destination path
    destination_path = os.path.join(cwd, directory_name, os.path.basename(source_path))

    try:
        shutil.copy2(source_path, destination_path)
        print(f"Copied {source_path} to {destination_path}")
        CTkMessagebox(
            title="Success", 
            message="Successfully created new profile: " + profile_name, 
            justify="center", 
            font= customtkinter.CTkFont(family="Arial", weight="bold"), 
            icon="check",
            sound=True
        )
        return destination_path
    except Exception as e:
        print(f"Error copying file: {e}")
        return None

def verify_archeage_directory():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    archeage_directory = config['DEFAULT']['ArcheageDirectory']
    
    # check if directory exists and is not null or empty string
    if os.path.exists(archeage_directory) and not archeage_directory == 'null' and not archeage_directory == '':
        return True
    else:        
        return False
    
def get_archeage_directory():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    archeage_directory = config['DEFAULT']['ArcheageDirectory']

    return archeage_directory

class ProfileFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.checkboxes = []

        self.title = customtkinter.CTkLabel(
            self, 
            text=self.title,
            font= customtkinter.CTkFont(family="Arial", weight="bold"),
            text_color = "white", 
            fg_color="gray30", 
            corner_radius=6
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.optionmenu = customtkinter.CTkOptionMenu(
            master=self,
            font= customtkinter.CTkFont(family="Arial", weight="bold"),
            text_color = "white",  
            values=self.values, 
            command=self.optionmenu_callback
        )
        self.optionmenu.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.loadConfigButton = customtkinter.CTkButton(
            self, 
            text="Load Config", 
            font= customtkinter.CTkFont(family="Arial", weight="bold"),
            text_color = "white", 
            fg_color="#1d4ed8", 
            hover_color="#1e40af",
            command=self.loadConfigButton_event
        )
        self.loadConfigButton.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.deleteConfigButton = customtkinter.CTkButton(
            self, 
            text="Delete Config",
            font= customtkinter.CTkFont(family="Arial", weight="bold"),
            text_color = "white",
            fg_color="#b91c1c", 
            hover_color="#991b1b",
            command=self.deleteConfigButton_event
        )#tailwind red-700 and red-800
        self.deleteConfigButton.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="ew")

        self.disable_widgets() if len(self.values) == 0 else None

    def loadConfigButton_event(self):
        if verify_archeage_directory() == True:
            cwd = os.path.join(os.getcwd(), "saved_configs")
            # Specify the directory name
            directory_name = self.optionmenu.get()
            source_path = os.path.join(cwd, directory_name, "system.cfg")
            destination_path = os.path.join(get_archeage_directory(), "system.cfg")
            try:
                shutil.copy2(source_path, destination_path)
                print(f"Copied {source_path} to {destination_path}")
                CTkMessagebox(
                    title="Success", 
                    message="Successfully loaded config: " + directory_name, 
                    justify="center", 
                    font= customtkinter.CTkFont(family="Arial", weight="bold"), 
                    icon="check",
                    sound=True
                )
            except Exception as e:
                print(f"Error copying file: {e}")
        else:
            msg = CTkMessagebox(
                title="AA directory not found.", 
                message="Please set the path to your Archeage directory before loading a config.", 
                justify="center", 
                font= customtkinter.CTkFont(family="Arial", weight="bold"), 
                option_1="OK", 
                sound=True
            )
            return
            
    def deleteConfigButton_event(self):
        msg = CTkMessagebox(
            title="Delete?", 
            message="Are you sure you want to delete this config?",
            icon="question",
            option_1="No", 
            option_2="Yes", 
            sound=True
        )
        response = msg.get()
        
        if response=="Yes":
            option = self.optionmenu.get()
            print("Selected option:", option)
            os.remove(os.path.join(os.getcwd(), "saved_configs", option, "system.cfg"))
            os.rmdir(os.path.join("saved_configs", option))
            self.refresh_values()


    def optionmenu_callback(self, choice):
        print("optionmenu dropdown clicked:", choice)

    def refresh_values(self):
        # path = os.getcwd()
        path = os.path.join(os.getcwd(), "saved_configs")
        new_values = [entry.name for entry in os.scandir(path) if entry.is_dir()]
        self.optionmenu.configure(values= new_values)
        print("Refreshed option menu values:", new_values)
        self.disable_widgets() if len(self.optionmenu.cget("values")) == 0 else self.enable_widgets()
        

    # if dir_list is empty, disable options menu and load/delete buttons
    def disable_widgets(self):
        self.optionmenu.configure(state="disabled")
        self.loadConfigButton.configure(state="disabled")
        self.deleteConfigButton.configure(state="disabled")
        self.optionmenu.set("No configs found")

    def enable_widgets(self):
        self.optionmenu.configure(state="normal")
        self.loadConfigButton.configure(state="normal")
        self.deleteConfigButton.configure(state="normal")
        self.optionmenu.set(self.optionmenu.cget("values")[0])


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        archeage_directory = 'null'
        # check if settings.ini exists, if not create it with default values
        if not os.path.exists('settings.ini'):
            documents_path = os.path.join(get_documents_folder(), "AAClassic")
            config = configparser.ConfigParser()
            config['DEFAULT'] = {'ArcheageDirectory': documents_path}
            with open('settings.ini', 'w') as configfile:
                config.write(configfile)
            archeage_directory = config['DEFAULT']['ArcheageDirectory']
            CTkMessagebox(
                title="AA documents directory found.", 
                height=250,
                width=500,
                message="Archeage documents directory auto-detected at:\n\n" + archeage_directory + "\n\nYou can change this directory if it's incorrect.", 
                justify="center", 
                font= customtkinter.CTkFont(family="Arial", weight="bold"), 
                sound=True
            )
        else:
            config = configparser.ConfigParser()
            config.read('settings.ini')

        archeage_directory = config['DEFAULT']['ArcheageDirectory']
        print("Archeage Directory:", archeage_directory)

        # if archeage_directory is invalid then prompt the user to select the archeage directory and save it to settings.ini
        if not verify_archeage_directory():
            msg = CTkMessagebox(
                title="AA documents directory not found.", 
                message="Please enter the path to your Archeage documents directory.", 
                justify="center", 
                font= customtkinter.CTkFont(family="Arial", weight="bold"), 
                sound=True
            )
            response = msg.get()
    
            if response=="OK":
                self.selectGameDirectory_event()      
            else:
                App.destroy(self)
        
        # create saved_configs directory if it doesn't exist
        if not os.path.exists("saved_configs"):
            os.mkdir("saved_configs")

        self.title("AA Config Switcher")

        # Get resolution of primary monitor and position window in the center of the screen
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        window_width = 300
        window_height = 350
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Set scaling and layout of the window
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_widget_scaling(1.25)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=0)

        # Set the window icon
        iconpath = resource_path("aacs.ico")
        self.iconbitmap(iconpath)
        

        # List the folders of the saved configs in the current directory and populate the dropdown menu
        path = os.path.join(os.getcwd(), "saved_configs")
        dir_list = [entry.name for entry in os.scandir(path) if entry.is_dir()]
        print("Folders in '", path, "' :")
        print(dir_list)
        
        self.profile_frame = ProfileFrame(self, "Saved Configs", values= dir_list)
        self.profile_frame.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="nsew")

        self.newConfigButton = customtkinter.CTkButton(
            self, 
            text="Save New Config", 
            font= customtkinter.CTkFont(family="Arial", weight="bold"), 
            text_color = "white", 
            fg_color="#15803d", 
            hover_color="#166534", 
            command=self.newConfigButton_event
        )#tailwind green-700 and green-800
        self.newConfigButton.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        self.changeDirectoryButton = customtkinter.CTkButton(
            self, 
            text="Change AA Directory", 
            font= customtkinter.CTkFont(family="Arial", weight="bold"), 
            text_color = "white", 
            fg_color="transparent", 
            hover_color="#f59e0b",
            border_color="#f59e0b",
            border_width=2, 
            command=self.selectGameDirectory_event
        )#tailwind amber-500
        self.changeDirectoryButton.grid(row=2, column=0, padx=10, pady=10, sticky="n")

        
    
    def newConfigButton_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a name for this profile:", title="New Profile")
        iconpath = resource_path("aacs.ico")
        dialog.after(250, lambda: dialog.iconbitmap(iconpath))

        profile_name = dialog.get_input()  # waits for input 
        if profile_name is None or profile_name.strip() == "":
            print("No profile name entered.")
            return   
        copy_file_via_dialog(profile_name)
        ProfileFrame.refresh_values(self.profile_frame)


    def selectGameDirectory_event(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        archeage_directory = filedialog.askdirectory()
        if not archeage_directory:
            print("No directory selected.")
            return
        config['DEFAULT']['ArcheageDirectory'] = archeage_directory
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        print("Archeage Directory saved to settings.ini:", archeage_directory)
        # self.after(1000, self.deiconify)  # Show the main window again


app = App()
app.mainloop()