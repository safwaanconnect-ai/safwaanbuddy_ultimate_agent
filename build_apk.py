import os
import subprocess
import sys

KIVY_APP_CODE = """
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty
from jnius import autoclass, cast

class WebView(BoxLayout):
    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.render_webview()

    def render_webview(self):
        # This is Android specific logic using pyjnius
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        activity = PythonActivity.mActivity

        def create_webview():
            webview = WebView(activity)
            webview.getSettings().setJavaScriptEnabled(True)
            webview.setWebViewClient(WebViewClient())
            webview.loadUrl(self.url)
            activity.setContentView(webview)

        activity.runOnUiThread(create_webview)

class SafwanBuddyMobile(App):
    target_ip = StringProperty('192.168.1.100')
    target_port = StringProperty('5000')

    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.root.add_widget(Label(text='SafwanBuddy Mobile Lite Connect', font_size=24))
        
        self.ip_input = TextInput(text=self.target_ip, multiline=False, hint_text='PC IP Address')
        self.root.add_widget(self.ip_input)
        
        self.port_input = TextInput(text=self.target_port, multiline=False, hint_text='Port (Default 5000)')
        self.root.add_widget(self.port_input)
        
        connect_btn = Button(text='CONNECT TO ELITE PC', background_color=(0, 1, 0.8, 1))
        connect_btn.bind(on_press=self.start_webview)
        self.root.add_widget(connect_btn)
        
        return self.root

    def start_webview(self, instance):
        url = f"http://{self.ip_input.text}:{self.port_input.text}"
        # In a real APK build, this would switch to the WebView
        print(f"Connecting to {url}")
        # For the sake of the wrapper, we'd invoke the Android WebView here
"""

BUILDOZER_SPEC = """
[app]
title = SafwanBuddy Mobile
package.name = safwanbuddy
package.domain = com.safwan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,pyjnius

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 1
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
"""

def prepare_android_build():
    print("Preparing Android build environment...")
    if not os.path.exists('mobile_build'):
        os.makedirs('mobile_build')
    
    with open('mobile_build/main.py', 'w') as f:
        f.write(KIVY_APP_CODE)
        
    with open('mobile_build/buildozer.spec', 'w') as f:
        f.write(BUILDOZER_SPEC)
    
    print("Mobile build directory prepared at ./mobile_build")
    print("To build the APK, run: cd mobile_build && buildozer android debug")

if __name__ == "__main__":
    prepare_android_build()
