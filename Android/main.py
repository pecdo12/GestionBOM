# pylint: disable=import-error
# This is the code for the main app.
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.app import MDApp

from PIL import Image
from camera4kivy import Preview
from pyzbar.pyzbar import decode

from google_sheet_editor import *

# Check if platform is android, if not, act as computer app
if platform == "android":
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    from android import mActivity

    # gets permissions from android
    request_permissions(
        [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.CAMERA,
            Permission.INTERNET,
        ]
    )
    View = autoclass("android.view.View")
else:
    from kivy.config import Config

    Config.set("input", "mouse", "mouse, disable_multitouch")


# App build
Builder.load_file("app.kv")

id_read = None
opened = False


class Login(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        if authorize_credentials_old():
            Snackbar(text="Logged in successfully").open()

        else:
            Snackbar(text="Error, not logged in").open()

    def bypass(self):
        self.manager.current = "camera"

    def get_code(self):
        url_web = open_google_connect()
        self.ids.url.text = url_web

    def login_google(self):
        if exchange_code(self.ids.code.text):
            Snackbar(text="Logged in successfully").open()
            sm.current = "camera"
        else:
            Snackbar(text="Error, not logged in").open()


# Camera screen - Displays the camera
class CameraScreen(Screen):

    # When app is started, this function is called
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def on_enter(self, *args):
        global opened
        if not opened:
            try:
                self.ids.preview.connect_camera(enable_analyze_pixels=True)
                opened = True
            except Exception as e:
                print(f"Error connecting to camera: {e}")
        
        try:
            if opened == True:
                pass
            else:
                self.ids.preview.connect_camera(enable_analyze_pixels=True)
                opened = True
        except:
            pass


    def scan_qr(self):
        global data_drop
        data_drop = {}
        sm.current = "data"

    def go_back(self):
        self.manager.current = "login"


# The camera class which is nested in the camera-screen.
class ScanAnalyze(Preview):

    # When enable_analyze_pixels = True, this function is automatically called on repeat.
    # Basically a thread is started that continuously check the camera and feeds the image in the argument pixels
    def analyze_pixels_callback(self, pixels, image_size, image_pos, scale, mirror):
        global id_read, id

        # Converts the pixels(bytes) into an actual image
        pimage = Image.frombytes(mode="RGBA", size=image_size, data=pixels)
        # This function is continuously being called, so checks if there are any qr codes inside the image
        if decode(pimage) != []:
            # A qr code has been found and switches the screen to PreviewData
            qr = str(decode(pimage)[0].data)
            id_read = qr[2:-1]
            print(f"Read id: {id_read}")
        else:
            pass


# The screen where we display what we want to do with the qr code we just scanned.
# We need to display the name of the item scanned, what the previous status was and a confirm button
class PreviewData(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_list(self):
        global titles

        self.ids.container.clear_widgets()

        try:
            titles = get_titles(id_read)
            textfield, dropdowns = titles
            print("Titles: ", titles)
        except Exception as e:
            text = MDLabel(
                text=f"Incorrect Barcode; The text extracted was: {id_read} \n and the error generated was: {e}",
                halign="center",
            )

            self.ids.container.add_widget(text)
            return

        for x, y in textfield.items():
            if y is None:
                y = "None"
            else:
                pass

            text = MDTextField(
                hint_text=y, helper_text=x, helper_text_mode="persistent"
            )

            self.ids.container.add_widget(text)

        for x, y in dropdowns.items():
            if y is None:
                y = "None"
            else:
                pass

            drop_buttons = MDRaisedButton(
                text=f"The selected value of {x} is {y}",
                id=str(x),
                # We want to pass the current value of x, so when its called, it feeds the value of x when it was created
                on_press=lambda instance: self.drop(instance),
            )

            self.ids.container.add_widget(drop_buttons)

        # Checks if any columns were not found in the sheet
        missing = []
        for x in [
            "Nom",
            "QuCAD",
            "QuCOM",
            "Manufacturier",
            "Matériaux",
            "Longueur/aire en pouce",
        ]:
            if x in textfield:
                pass
            else:
                missing.append(x)

        for x in ["Order status", "Fab Status", "DXF / CAM", "TYPE"]:
            if x in dropdowns:
                pass
            else:
                missing.append(x)

        if missing:
            missing_text = (
                f"Pour le id  {id_read}, l'application ne pouvait pas trouver: "
            )
            for x in missing:
                missing_text += f"{x}, "
            print(missing_text[:-2])
            missing_text = (
                missing_text[:-2]
                + ". Assurez vous que les colonnes dans le sheets sont écrites de la même façon."
            )
            text = MDLabel(text=missing_text, halign="center")
            self.ids.box_text.add_widget(text)

    def drop(self, button_instance):
        global drop_name
        drop_name = button_instance.id
        print(drop_name)
        sm.current = "drop"

    def send_data(self):
        global new_data
        new_data = {}

        try:  # This is to merge the dictionnaries for the drop buttons with the textfield buttons
            new_data.update(data_drop)
        except:
            print("No drop data")

        for (
            child
        ) in self.ids.container.children:  # This is to get the data from the textfields
            if isinstance(child, MDTextField):
                if child.text == "":
                    pass
                else:
                    new_data[child.helper_text] = child.text

        if new_data:  # This is to check if there is any data to send
            old_data = {}
            titles_dict = {}
            for d in titles:  # Get searchable dictionnary
                titles_dict.update(d)

            # Get old data that was modified
            for x in titles_dict:
                if x in list(new_data.keys()):
                    old_data[x] = titles_dict[x]
                else:
                    pass

            # Send data and retrieve failed items
            get = modify_sheet(id_read, new_data)
            if get is None:
                Snackbar(text="Data sent successfully").open()

            else:  # Removes failed items fromlog list
                Snackbar(text=f"Error, data not sent: {get}").open()
                for x in get.keys():
                    del new_data[x]
                    del old_data[x]

        else:
            Snackbar(text="No data to send").open()

    def go_back(self):
        self.ids.container.clear_widgets()
        self.manager.current = "camera"


class ChangeDrop(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        options = get_drop(drop_name)
        if options == []:
            Snackbar(text="No options found").open()
            self.manager.current = "data"
            return

        else:
            for x in options:
                button = MDRaisedButton(text=x, on_press=self.save_data)
                button.data = x
                self.ids.container.add_widget(button)

    def save_data(self, instance):
        data_drop[drop_name] = instance.data
        print(data_drop)

    def go_back(self):
        self.ids.container.clear_widgets()
        self.manager.current = "data"



# The actual app class
class TestApp(MDApp):

    # Called to build the actual app
    def build(self):
        global sm
        # Create the screen manager and sets a dark theme
        self.theme_cls.theme_style = "Dark"
        sm = ScreenManager()
        sm.add_widget(Login(name="login"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(PreviewData(name="data"))
        sm.add_widget(ChangeDrop(name="drop"))

        return sm

    # Called when the app is closed - Makes sure the camera is disconnected.
    def on_stop(self):
        self.inner_instance = CameraScreen()
        self.inner_instance.ids.preview.disconnect_camera()


# Run the app
if __name__ == "__main__":
    TestApp().run()
