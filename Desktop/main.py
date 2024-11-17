# This is the code for the main app.
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivy.core.window import Window

from camera4kivy import Preview
from pyzbar.pyzbar import decode
from google_sheet_editor import *
from qr_codes import *
from qr_printing import *



# App build
Builder.load_file("app.kv")

id_read = None
data_drop = {}


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        Window.size = (850, 650)
        if authorize_credentials_old() == True:
            Snackbar(text="Logged in").open()
        else:
            Snackbar(text="Not logged in").open()

    def google_sign_in(self):
        if google_connect() is not None:
            Snackbar(text="Authorization successful").open()
        else:
            Snackbar(text="Authorization failed").open()
            
            
    def to_desktop(self):

        sm.current = "desktop"


    def generator(self):
        sm.current = "print"
        pass

    def scan_qr(self):
        sm.current = "camera"
        pass



# DesktopMain -takes name as input
class DesktopMainScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    pass

    def id_get(self):

        value = self.ids.find.text

        all_occ = search_for_string(value)

        for x in all_occ:
            if x is None:
                x = "None"
                Snackbar(text="No data found").open()
            else:
                pass

            button = MDRaisedButton(
                text=x.value,
                id=str(x.row),
                # We want to pass the current value of x, so when its called, it feeds the value of x when it was created
                on_press=lambda instance: self.clicked(instance),
            )

            self.ids.container.add_widget(button)

    def clicked(self, id_val):
        global id_read
        print(id_val.text)
        self.ids.container.clear_widgets()
        id_read = get_id_from_sheet(id_val.id)
        print("after", id_read)

        sm.current = "data"

    def go_back(self):
        self.ids.container.clear_widgets()
        self.ids.find.text = ""
        sm.current = "login"
        pass


# Camera screen - Displays the camera
class CameraScreen(Screen):

    # When app is started, this function is called
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # this is used to analyse the camera in real time
        self.ids.preview.connect_camera(enable_analyze_pixels=True)


    def scan_qr(self):
        global data_drop
        # self.ids.preview.disconnect_camera()
        data_drop = {}
        sm.current = "data"

    def go_back(self):
        sm.current = "login"
        pass


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
            missing_text = "L'application ne pouvait pas trouver: "
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
        global new_data, data_drop

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
                print(get)
                Snackbar(text=f"Error, data not sent: {get}").open()
                for x in get.keys():
                    del new_data[x]
                    del old_data[x]

        else:
            Snackbar(text="No data to send").open()

    def go_back(self):

        self.ids.container.clear_widgets()
        self.manager.current = "login"

    def go_print(self):
        self.ids.container.clear_widgets()
        self.manager.current = "print"


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
        global data_drop
        data_drop[drop_name] = instance.data  
        print(data_drop)

    def go_back(self):
        self.ids.container.clear_widgets()
        self.manager.current = "data"


class PrintScreen(Screen):
    global id_read

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        global printer
        printer = None
        for x in list_printers():
            print_choice = MDRaisedButton(
                text=f"{x}",
                id=str(x),
                # We want to pass the current value of x, so when its called, it feeds the value of x when it was created
                on_press=lambda instance: self.select_printer(instance),
            )

            self.ids.container_printer.add_widget(print_choice)

    def select_printer(self, instance):
        global printer
        printer = instance.id
        Snackbar(text=f"Printer selected: {printer}").open()

    def clear_id_text(self):
        with open("id.txt", "w"):
            pass

    def process_id_text(self):
        global printer

        try:
            os.mkdir("qrs")
        except:
            pass

        make_all()
        toast("Generated QR codes")

        if self.ids.print.active == True:
            if printer is None:
                Snackbar(text="No printer selected").open()
                return
            create_job(printer, os.listdir("qrs"))
            toast("Printed QR codes")

    def process_selected(self):
        global printer

        try:
            os.mkdir("qrs")
        except:
            pass

        list_id = self.ids.list_id.text
        list_id = list_id.split(" ")

        for x in list_id:
            if x + ".png" not in os.listdir("qrs"):
                make_card_indiv(x)

        list_id = [x + ".png" for x in list_id]

        toast("Generated QR codes")

        if self.ids.print.active == True:
            if printer is None:
                Snackbar(text="No printer selected").open()
                return
            create_job(printer, list_id)
            toast("Printed QR codes")

    def go_back(self):
        self.manager.current = "login"


# The actual app class
class TestApp(MDApp):

    # Called to build the actual app
    def build(self):
        global sm
        # Create the screen manager and sets a dark theme
        self.theme_cls.theme_style = "Dark"
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DesktopMainScreen(name="desktop"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(PreviewData(name="data"))
        sm.add_widget(ChangeDrop(name="drop"))
        sm.add_widget(PrintScreen(name="print"))

        return sm

    # Called when the app is closed - Makes sure the camera is disconnected.
    def on_stop(self):
        self.inner_instance = CameraScreen()
        self.inner_instance.ids.preview.disconnect_camera()


# Run the app
if __name__ == "__main__":
    TestApp().run()
