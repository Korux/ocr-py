
from PIL import Image

import pytesseract
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import numpy as np
import cv2
from mss import mss

import pynput.keyboard as kb

from pynput.keyboard import Key
from pynput.keyboard import Listener as KListener
from pynput.mouse import Listener as MListener

from googletrans import Translator

class OCR:

    def __init__(self):
        self.mouse = MListener(on_click=self.onClick)
        self.keyboard = KListener(on_press=self.onPress)
        self.area = {}
        self.schedTranslation = 'none'

    def onClick(self,*args):
        if args[-1] and args[-2].name == "left":
            # Do something when the mouse key is pressed.
            # print('The "{}" mouse key has held down'.format(args[-2].name))
            self.area["top"] = args[1]
            self.area["left"] = args[0]

        elif not args[-1] and args[-2].name == "left":
            # Do something when the mouse key is released.
            # print('The "{}" mouse key is released'.format(args[-2].name))
            self.area["width"] = args[0] - self.area["left"]
            self.area["height"] = args[1] - self.area["top"]
            if(self.area["width"] < 0):
                self.area["width"] = abs(self.area["width"])
                self.area["left"] -= self.area["width"]
            if(self.area["height"] < 0):
                self.area["height"] = abs(self.area["height"])
                self.area["top"] -= self.area["height"]
            self.mouse.stop()
    
    def onPress(self,key):
        try:
            if key.char == 'z':
                if self.schedTranslation == 'none':
                    self.schedTranslation = 'google'
            elif key.char == 'x':
                if self.schedTranslation == 'none':
                    self.schedTranslation = 'deepl'
            else:
                print("unknown key")
        except:
            print("unknown key")
    def getArea(self):
        print("capturing area...")
        self.mouse.start()
        self.mouse.join()
        print("area is: {}".format(self.area))

    def beginCapture(self):
        sct = mss()
        self.keyboard.start()
        translator = Translator()
        print("begin capturing...")

        while 1:
            sct_img = np.array(sct.grab(self.area))
            if self.schedTranslation == 'google':
                sentence = pytesseract.image_to_string(Image.fromarray(sct_img), lang='jpn')
                translated = translator.translate(sentence)
                print(sentence)
                print('-----------------------------------')
                print(translated.text)
                print('-----------------------------------\n')
                self.schedTranslation = 'none'
            elif self.schedTranslation == 'deepl':
                sentence = pytesseract.image_to_string(Image.fromarray(sct_img), lang='jpn')
                #translated = self.translate(sentence)
                translated = self.translate(sentence)
                print(sentence)
                print('-----------------------------------')
                print(translated)
                print('-----------------------------------\n')
                self.schedTranslation = 'none'
            cv2.imshow('test', sct_img)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


    def translate(self,sentence):
        
        # Headless mode
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        # Start a Selenium driver
        driver_path='./chromedriver'
        driver = webdriver.Chrome(driver_path, chrome_options=options)

        # Reach the deepL website
        deepl_url = 'https://www.deepl.com/translator'
        driver.get(deepl_url)

        # # Get thie inupt_area 
        input_css = 'div.lmt__inner_textarea_container textarea'
        input_area = driver.find_element_by_css_selector(input_css)

        # # Send the text
        input_area.clear() 
        input_area.send_keys(sentence)

        # Init translated text
        translation = ""

        # Alt: get hidden text
        hidden_button = '.lmt__translations_as_text__text_btn'

        while translation == "":
            content = driver.find_element_by_css_selector(hidden_button)
            translation = content.get_attribute('innerHTML')

            # Wait for translation to appear on the web page
            time.sleep(0.1)

        # Quit selenium driver
        driver.quit()

        return translation

def main():

    ocr = OCR()
    ocr.getArea()
    ocr.beginCapture()

if __name__ == "__main__":
    main()