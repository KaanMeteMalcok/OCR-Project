import string
import cv2 
import numpy as np
from sqlite3 import Cursor
import pypyodbc
import pymysql.cursors
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

db = pymysql.connect(host = 'localhost',user = 'root', password = 'Kaan441998.', db = 'deneme', charset = 'utf8mb4', cursorclass = pymysql.cursors.DictCursor)
con_1 = db.cursor()

kaynak = ""
Start_1 = """
(1) Resim ile bilgi gir
(2) Çıkış
"""
Start_2 = """
Bilgileri yüklemek için 1'e basın 
El ile bilgi girmek için 2'ye basın
Çıkmak için 3'ye basın
"""
Start_3 = """
Firma adı ile devam etmek için 1'e basın
Firma adı olmadan devam etmek için 2'ye basın
Çıkmak için 3' e basın
"""
Start_3_Company = """
Firmanın adı doğruysa 1'e basın
Firmanın adı yanlışsa 2'ye basın
"""
Boşluk_1 = """
"""
key_num = 1
key_num_1 = 1
key_num_2 = 1
key_num_3 = 1


def İmgRead(img_path): # Resimi okuyup düzenlemek için
    image = cv2.imread(img_path)

    image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    image = cv2.medianBlur(image, ksize= 5)       # bu işe yarıyor gibi
    #image = cv2.blur(image,(10,10))
    #image = cv2.GaussianBlur(image,(9,9),5)
    #image = cv2.equalizeHist(image)

    kernel = np.ones((1,1),np.uint8)
    image = cv2.erode(image,kernel,iterations=2)
    #image = cv2.dilate(image,kernel,iterations=1)

    #kullanma #image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,31,2)
    cv2.imwrite(kaynak+'temizlenmisResim.jpeg',image)

    result = pytesseract.image_to_string(Image.open(kaynak+'temizlenmisResim.jpeg'),lang='tur')

    return result

# Uygulamanın ana döngüsü
while key_num == 1: 
    print(Start_1)
    question = input("Yapmak istediğiniz işlemin numarasını giriniz : ")
    if question == '2':
        print("Çıkılıyor")
        key_num = 0  
    elif question == '1':
        img_name = input("Resmin tüm adını giriniz : ")
        print(' ')
        img_name = img_name+'.jpeg'
        key_num_1 = 1
        key_num_2 = 1
        key_num_3 = 1
        txt = İmgRead(img_name)
        txt = txt.lower()
        print(txt)

        # Firma ismini girmek için
        while key_num_2 == 1:
            print(Start_3)
            company_question = input("Yapmak istediğiniz işlemi seçiniz : ")
            print(' ')
            if company_question == '3':
                print("Çıkılıyor")
                key_num_2 = 0
            elif company_question == '1':
                company_name = txt[0:14]
                print(company_name)
                company_name_control = input(Start_3_Company)
                while key_num_3 == 1:  
                    if company_name_control == '1':
                        key_num_2 = 0
                        key_num_3 = 0
                    elif company_name_control == '2':
                        company_name = input("Firmanın adını el ile giriniz : ")
                        print(' ')
                        print(company_name)
                        key_num_2 = 0
                        key_num_3 = 0
                    else:
                        print("YANLIŞ GİRİŞ")
                        break
            elif company_question == '2':
                company_name = ['Firmanın Adı yok']
                key_num_2 = 0
            else :
                print("YANLIŞ GİRİŞ")

        # Toplam vergiyi bulmak için
        tax_index = txt.find("kdv")
        tax_string = txt[tax_index:tax_index+12]
        tax_number = tax_string[3:11]
        if tax_number[1] != '1' and tax_number[1] != '2' and tax_number[1] != '3' and tax_number[1] != '4' and tax_number[1] != '5' and tax_number[1] != '6' and tax_number[1] != '7' and tax_number[1] != '8' and tax_number[1] != '9':
            tax_char_1 = tax_number[1]
            tax_number = tax_number.replace(tax_char_1,' ')
        else:
            tax_number = tax_number    
        if tax_number[-1] == 't':
            tax_char = tax_number[-1]
            tax_number = tax_number.replace(tax_char,' ')
        elif tax_number[-1] == 'o':
            tax_number = tax_number.replace('to',' ')
        else:
            tax_number = tax_number    
        print(tax_number)

        # Toplam değeri bulmak için
        total_index = txt.find("toplam")
        if total_index == -1:
            total_index_1 = txt.find("top")
            total_string = txt[total_index_1:total_index_1+15]
            total_number = total_string[5:12]
            if total_number[1] != '1' and total_number[1] != '2' and total_number[1] != '3' and total_number[1] != '4' and total_number[1] != '5'and total_number[1] != '6' and total_number[1] != '7' and total_number[1] != '8' and total_number[1] != '9':
                total_char_1 = total_number[1]
                total_number = total_number.replace(total_char_1,' ')
            else:
                total_number = total_number    
        else:
            total_string = txt[total_index:total_index+15]
            total_number = total_string[8:15]
            if total_number[1] != '1' and total_number[1] != '2' and total_number[1] != '3' and total_number[1] != '4' and total_number[1] != '5'and total_number[1] != '6' and total_number[1] != '7' and total_number[1] != '8' and total_number[1] != '9':
                total_char_1 = total_number[1]
                total_number = total_number.replace(total_char_1,' ')
            else:
                total_number = total_number 
        print(total_number)
        # Bilgileri Mysql Servere yüklemek için gerekli kod
        while key_num_1 == 1:
            print(Start_2)
            upload_1 = input("Yapmak istediğiniz işlemi seçiniz : ")
            print(' ')
            if upload_1 == '3':
                print("Çıkılıyor")
                key_num_1 = 0
            elif upload_1 == '1':
                print("Yükleniyor")
                print(company_name)
                print(tax_number)
                print(total_number)
                tax_number = tax_number.replace(',','.')
                tax_number = tax_number.replace(Boşluk_1,'')
                tax_number = tax_number.replace(' ','')
                tax_number = float(tax_number)
                total_number = total_number.replace(',','.')
                total_number = total_number.replace(Boşluk_1,'')
                total_number = total_number.replace(' ','')
                total_number = float(total_number)
                con_1.execute('INSERT INTO giderler VALUES(%s,%s,%s,%s)',(None,company_name,tax_number,total_number))
                db.commit()
                key_num_1 = 0
            elif upload_1 == '2':
                tax_number = input("Vergi değerini giriniz : ")
                print(' ')
                total_number = input("Toplam değeri giriniz : ")
                print(' ')
                print(company_name)
                print(tax_number)
                print(total_number)
                tax_number = tax_number.replace(',','.')
                tax_number = tax_number.replace(Boşluk_1,'')
                tax_number = tax_number.replace(' ','')
                tax_number = float(tax_number)
                total_number = total_number.replace(',','.')
                total_number = total_number.replace(Boşluk_1,'')
                total_number = total_number.replace(' ','')
                total_number = float(total_number)
                con_1.execute('INSERT INTO giderler VALUES(%s,%s,%s,%s)',(None,company_name,tax_number,total_number))
                db.commit()
                key_num_1 = 0
            else:
                print("yanlış giriş")
    else:
        print("Yanlış Giriş")
        print("Aşağıdaki seçeneklerden birini giriniz : ",Start_1)

