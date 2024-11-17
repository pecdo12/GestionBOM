import win32api
import win32print
import time
import os
import win32con
import pyautogui


def list_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    return printers


def create_job(printer, filenames):
    file_list = []
    for i in filenames:
        file_list.append(os.path.abspath(f"qrs/{i}"))

    PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}

    pHandle = win32print.OpenPrinter(printer, PRINTER_DEFAULTS)
    properties = win32print.GetPrinter(pHandle, 2)
    properties["pDevMode"].Color = 2
    properties["pDevMode"].Copies = 1
    properties["pDevMode"].Orientation = win32con.DMORIENT_LANDSCAPE
    properties["pDevMode"].DisplayFixedOutput = win32con.DMDFO_CENTER

    win32print.SetPrinter(pHandle, 2, properties, 0)
    win32print.SetDefaultPrinter(printer)

    counter = 0

    try:
        for file in file_list:
            print(file)
            if counter == 0:
                win32api.ShellExecute(0, "print", file, None, ".", 0)
                time.sleep(2)
                # pyautogui.hotkey("win", "tab")
                # pyautogui.hotkey("left")
                # pyautogui.hotkey("enter")
                counter += 1

            else:
                win32api.ShellExecute(0, "print", file, None, ".", 0)

            time.sleep(1)
            pyautogui.press("tab", presses=7)
            pyautogui.press("space")
            # pyautogui.press("enter")
            time.sleep(1)

    except Exception as e:
        print("Error printing file")
        print(e)

    win32print.ClosePrinter(pHandle)
