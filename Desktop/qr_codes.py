import qrcode
import os
import sys
from PIL import Image, ImageFont, ImageDraw
import gspread
from oauth2client.service_account import ServiceAccountCredentials


import qrcode
from PIL import Image, ImageDraw, ImageFont
def create_card(text_info, qr_data):
    # Set up the card dimensions and font
    card_width, card_height = 400, 200
    font = ImageFont.truetype("arial.ttf", 14)

    # Create a new blank image
    card = Image.new('RGB', (card_width, card_height), color='white')
    draw = ImageDraw.Draw(card)

    # Define text information
    text_x, text_y = 10, 10 # Text position
    text_spacing = 30

    # Add text information to the images
    for key, value in text_info.items():
        if len(value) > 12:
            try:
                value = value.replace(" - ", "- ")
                value = value.replace(" ", "\n")
                if "\n" in value:
                    count = value.count("\n")
                    
                    text_spacing += 15*count
                
            except:
                pass
            
        text = f"{key}: {value}"
        draw.text((text_x, text_y), text, fill='black', font=font)
        text_y += text_spacing

    # Create a QR code and resize to fit the available space
    qr = qrcode.make(qr_data)
    qr.thumbnail((180, 180))  # Resize the QR code to fit within a specific area
    qr_x, qr_y = 210, 10
    card.paste(qr, (qr_x, qr_y))

    # Save the card image
    card.save(f"qrs/{qr_data}.png")

def authorize_api():
    # Specify where to get the google sheets
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]

    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # Authorize the app through the client_key.json
    file_name = os.path.join(base_dir, 'client_key.json')
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
    client = gspread.authorize(creds)
    return client

def get_id(name):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    #Name of the sheets to read
    sheet_name = 'copyBOM'

    #Open a specific worksheet
    sheet_BOM = client.open(sheet_name).get_worksheet(0)

    #Get all the column values from the BOM sheet
    
    search_list = sheet_BOM.findall(name)
    id_list = []
    for elem in search_list:
        id = sheet_BOM.cell(sheet_BOM.find(elem.value, in_column=0).row, sheet_BOM.find("").col).value
        id_list.append(id)
    print(f"Search: {id_list} {type(id_list)} {type(id_list[0])}")
    return id_list
 
def get_info(id):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    #Name of the sheets to read
    sheet_name = 'copyBOM'

    #Open a specific worksheet
    sheet_BOM = client.open(sheet_name).get_worksheet(0)

    #Get all the column values from the BOM sheet
    name = sheet_BOM.cell(sheet_BOM.find(id, in_column=1).row, sheet_BOM.find("Nom", in_row=1).col).value
    material = sheet_BOM.cell(sheet_BOM.find(id, in_column=1).row, sheet_BOM.find("Matériaux", in_row=1).col).value
    return name, material

def extra_info(id):
    try:
        client = authorize_api()
    except Exception as e:
        print(e)

    #Name of the sheets to read
    sheet_name = 'copyBOM'

    #Open a specific worksheet
    sheet_BOM = client.open(sheet_name).get_worksheet(0)

    #Get all the column values from the BOM sheet
    manufacturier = sheet_BOM.cell(sheet_BOM.find(id, in_column=1).row, sheet_BOM.find("Manufacturier", in_row=1).col).value
    type = sheet_BOM.cell(sheet_BOM.find(id, in_column=1).row, sheet_BOM.find("TYPE", in_row=1).col).value
    return manufacturier, type

def make_card_indiv(valeur):
    try:    
        retourinfo = get_info(valeur)
        name, material = retourinfo
        data = {
            'ID': f'{valeur}',
            'Name': f'{name}',
            'Material': f'{material}'
        }
        create_card(data, valeur)
    except:
        print("N'existe pas")
        pass
    print(f"Done {valeur}")

def make_all():
    error = []
    existing_qrs = os.listdir("qrs")
    with open("id.txt", "r") as f:
        #Code to generate the qr codes
        try:
            os.mkdir("qrs")
        except: pass
        line = None
        while True:
            try: line = f.readline().split()[0]
            
            except:
                if len(line) == 0:
                    break

                error.append(line)
                break

            if line+".png" in existing_qrs:
                print(f"QR code already exists for {line}")
                continue
            make_card_indiv(line)

    error.remove(line)
    if len(error) > 0:
        print(f"Error with: {error}")
    print(f"Last id processed: {line}") 
    pass

def id_text_logic(): #this has the logic to manipulate id.txt file

    status =True   
    while status == True:
        choice = input("Quelle action voulez-vous faire? (Écrivez le chiffre): \n \t1. Imprimer manuellement \n \t2. Imprimer id.txt \n \t3. Vérification de ID \n \t4. Sortir ")
        match choice:
            case "1":
                valeur = input("Donner le ID: ")
                try:
                    retourinfo = get_info(valeur)
                    name, material = retourinfo
                    data = {
                        'ID': f'{valeur}',
                        'Name': f'{name}',
                        'Material': f'{material}'
                    }

                    print(data)

                    create_card(data, valeur)

                except:
                    print("N'existe pas")
                    pass

            case "2":
                choice_append = input("Souhaiteriez-vous imprimer automatiquement id.txt (Y/N) ").lower()
                match choice_append:
                    case "y":
                        #mode overwrite
                        try:
                            os.mkdir("qrs")
                        except: pass
                        line = None
                        with open("id.txt", "r") as f:
                            #Code to generate the qr codes

                            while True:
                                try: line = f.readline().split()[0]
                                except:
                                    print(f"This value caused an error: {line}")
                                    break
                                if len(line) == 0:
                                    break

                                # img = qrcode.make(line)
                                # type(img)
                                # img.save(f"qrs/{line}.png")

                                try:
                                    retourinfo = get_info(line)
                                except:
                                    print("N'existe pas")

                                name, material = retourinfo

                                data = {
                                            'ID': f'{line}',
                                            'Name': f'{name}',
                                            'Material': f'{material}'
                                        }

                                print(data)

                                create_card(data, line)
                                    
                                
                        print(f"Last id processed: {line}")                
                    case"_":
                        print("Retour au menu")
                pass
            case "3":
                valeur = input("Donner le ID: ")
                try:
                    retourinfo = get_info(valeur)
                    name, material = retourinfo

                    retour_extra = extra_info(valeur)
                    manufacturier, id_type = retour_extra
                    data = {
                        'ID': f'{valeur}',
                        'Name': f'{name}',
                        'Material': f'{material}',
                        'Manufacturier': f'{manufacturier}',
                        'TYPE': f'{id_type}'
                    }

                    print(data)
                    print_txt = input("Souhaiteriez-vous ajouter cet ID au fichier id.txt? (Y/N)").lower()
                    match print_txt:
                        case "y":
                            # mode append
                            with open("id.txt", "a") as file:
                                print("open")
                                retourinfo = get_info(valeur)
                                file.write(f"{valeur}\n")
                                pass
                            pass

                        case _:
                            print("Retour au menu")
                    pass
                except:
                    print("N'existe pas")
                    break

            case _:
                status = False
                print("Merci et au revoir!")
                exit()
