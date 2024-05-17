import json
import os
import pathlib
import socket
import threading
import time

from kivy.app import App
from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget  import Widget
from kivy.utils import platform

from network_.manager import NetworkManager

if platform == 'android':
    from androidstorage4kivy import SharedStorage
    from android import api_version
    from android import mActivity, autoclass
    

from kivy.config import Config
Config.set('graphics', 'resizable', True)

# with open('./config.json', 'r') as f:
#     cfg = json.load(f)
# IP   = cfg['IP'] 
# PORT = cfg['PORT']

IP = '146.168.100.42'
PORT = 16771
BUFF_SIZE = 4096

class SharingApp(App):
    def build(self):
        self.data_dir = self.user_data_dir
        root_widget = self.build_root_widget()
        self.start_service()
        return root_widget

    def start_service(self):
        if platform == "android":
            SERVICE_NAME = u"org.test.panzavantazhenko.ServiceMyservice" 
            service = autoclass(SERVICE_NAME)
            mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            service.start(mActivity, '')

    def build_root_widget(self):
        grid = GridLayout()
        grid.cols = 1
        # initialize widgets
        self.info_label     = Label(text=f'enter IP:PORT in the window below\ndata_dir = {self.data_dir}')
        self.ip_input       = TextInput(multiline=False, text=f'{IP}:{PORT}')
        self.request_input  = TextInput(multiline=False, text='Farewell to Erin - Mandolin and Bodhrán')
        
        self.toggles = GridLayout()
        self.toggles.cols = 2
        self.quality_toggle = ToggleButton(text="Toggle for higher quality", group='quality')
        self.video_toggle   = ToggleButton(text="Toggle to add video",       group='video')
        self.toggles.add_widget(self.quality_toggle)
        self.toggles.add_widget(self.video_toggle)
        button              = Button(text="Request")
        button2             = Button(text="Talk to service")
        # button bind
        button.bind( on_press=self.button_callback)
        button2.bind(on_press=self.button_callback2)
        # add widgets
        grid.add_widget(self.info_label)
        grid.add_widget(self.ip_input)
        grid.add_widget(self.request_input)
        grid.add_widget(self.toggles)
        grid.add_widget(button)
        grid.add_widget(button2)
        return grid 

    def button_callback(self, obj):
        self.send_request(obj)
        self.receive_file(obj)

    def button_callback2(self, obj):
        IP, PORT = self.ip_input.text.split(':')
        service_sock = socket.socket()
        service_sock.connect(("127.0.0.1", 3002))
        service_nm = NetworkManager(service_sock, BUFF_SIZE)
        service_nm.send({"query": self.request_input.text, 
                         "add_video": self.video_toggle.state == "down", 
                         "high_quality": self.quality_toggle.state == "down", 
                         "IP": IP,
                         "PORT": PORT,
                         "data_dir": self.data_dir})
        service_response = service_nm.recv()
        while service_response != "Done": 
            self.info_label.text = service_response
            service_response = service_nm.recv()
        service_nm.close()

    def send_request(self, obj):
        client = socket.socket()
        IP, PORT = self.ip_input.text.split(':')
        client.connect((str(IP), int(PORT)))
        self.nm = NetworkManager(client, BUFF_SIZE)
        self.nm.send({"query": self.request_input.text, 
                      "add_video": self.video_toggle.state == "down", 
                      "high_quality": self.quality_toggle.state == "down"})

    def receive_file(self, obj):
        file_meta = self.nm.recv()
        private_filename = f'{self.data_dir}/{file_meta["filename"]}'
        self.nm.file_receive(private_filename)
        self.nm.close()
        if platform == 'android':
            shared_path = SharedStorage().copy_to_shared(private_filename)
            self.info_label.text = 'Done'

if __name__ == "__main__":
    SharingApp().run()
