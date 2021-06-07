##############################################################################
# GUI Main
#
# Jendrik Richter (UMG)
##############################################################################
# Standard library imports
import configparser
import os.path
# Third Party Imports
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
# Local application imports
from Scripts import configHandler
from Scripts import handleOPT as opt
from Scripts import buildComp as bob

confFile_path = 'config.ini'
if os.path.isfile(confFile_path):
    config = configHandler.readConf()
else:
    print("error konfig erstellen/eingeben")

class Source(Screen):
    # Objects from GUI(SourcSelector)
    getPreview_Button = ObjectProperty(None)
    selectDataInput_Radio = ObjectProperty(None)
    ehrRepoAdress_Input = ObjectProperty(None)
    test_input = ObjectProperty(None)
    uploadbutton = ObjectProperty(None)

    def press(self):
        test_input = self.test_input.text
        ## Print it to the Screen -> to the screen of the app is more complicated
        #self.add_widget(Label(text=f'Hi {test_input}'))
        print(f'Hi {test_input}')

        ## Clear Input
        self.test_input.text = ''

    def uploadbutton(self):
        # Upload OPT
        opt.handleOPT(
            config['targetRepo']['workdir'], 
            config['targetRepo']['templateName'], 
            config['targetRepo']['inputCSV'], 
            config['targetRepo']['targetRepoAdress'],
            config['targetRepo']['targetRepoUser'],
            config['targetRepo']['targetRepoPw'],
            config['targetRepo']['targetflatAPIadress'],
            config['targetRepo']['targetopenEHRAPIadress']
            )

class Mapper(Screen):
    pass

class Uploader(Screen):
    buildbutton = ObjectProperty(None)

    def buildbutton(self):
        # Build Resources
        bob.buildComp(
            config['targetRepo']['workdir'], 
            config['targetRepo']['templateName'],
            config['targetRepo']['inputCSV']
            )

class WindowManager(ScreenManager):
    pass

class FLATLoader_GUI(App):
    def build(self):
        kv_path = os.path.join('UI', 'flatloader_window.kv')
        return Builder.load_file(kv_path)

if __name__ == "__main__":
    FLATLoader_GUI().run()


# UrlRequest  -> https://kivy.org/doc/stable/api-kivy.network.urlrequest.html#kivy.network.urlrequest.UrlRequest
# Animation   -> https://kivy.org/doc/stable/api-kivy.animation.html#kivy.animation.Animation
# Clock, before, after -> https://kivy.org/doc/stable/gettingstarted/framework.html

############################# Important Notes ###############################
# Installation of Kivy
# Installation of KivyMD -> https://github.com/kivymd/KivyMD   |   https://www.youtube.com/watch?v=ycoKlFV3-iU&list=PLCC34OHNcOtpz7PJQ7Tv7hqFBP_xDDjqg&index=41
#   KivyMD needs Pillow

# Standalone Python EXE: https://www.youtube.com/watch?v=NEko7jWYKiE
# Radio-Button: https://www.youtube.com/watch?v=X-9l-Sll_gE&list=PLCC34OHNcOtpz7PJQ7Tv7hqFBP_xDDjqg&index=30
# Navbar with KivyMD: https://www.youtube.com/watch?v=YynbD-netKg

# Widget with Data List Property
# grid = GridLayout(cols=len(self.data))
# self.bind(data=grid.setter('cols'))
#
# GridLayout:
#    cols: len(root.data)