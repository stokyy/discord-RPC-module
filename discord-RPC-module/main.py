# discord rpc module by stokyy
# 20.04.2025

import os
import time
import win32gui
import win32process
import psutil
import ctypes
import json
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from win11toast import toast
from pypresence import Presence

default_data = {
    'application_id': 'your_application_id_here',
    'debug_mode': False,
    'time': 20,
    'trey': True,
    'applications': {
        'process_name': {'text': 'main_text', 'image': 'big_img', 'small_image': 'small_img', 'tooltip': 'main_text', 'small_text': 'small_text'},
    }
}

file_name = 'config.json'
if not os.path.exists(file_name):
    with open(file_name, 'w') as file:
        json.dump(default_data, file, indent=4)
    print(f'{file_name} создан!')

with open(file_name, 'r', encoding='utf-8') as file:
    config = json.load(file)

application_id = config.get('application_id')
debug_mode = config.get('debug_mode')
applications = config.get('applications', {})
small_image = config.get('small_image')
small_text = config.get('small_text')
time_to_update = config.get('time')
trey_mode = config.get('trey')
custom_process_name = config.get('custom_name')

rpc = Presence(application_id)
rpc.connect()

default_data = {
    'application_id': 'your_application_id_here',
    'debug_mode': False,
    'time': 20,
    'trey': True,
    'applications': {'process_name': {'text': 'main_text', 'image': 'big_img', 'small_image': 'small_img', 'tooltip': 'main_text', 'small_text': 'small_text'}}
}

def get_active_window_name():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            process_name = process.name().lower().replace('.exe', '')
            return process_name, pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None, None

def update_activity():
    process_name, _ = get_active_window_name()
    if process_name:

        #параметры для process_name`ов, которых нет в cfg
        activity = applications.get(process_name, {
            'custom_name': process_name,
            'text': 'text',
            'image': 'default',
            'small_image': 'default_small',
            'tooltip': 'tooltip',
            'small_text': 'small_text'
        })
        
        rpc.update(
            details=f'возится в {activity['custom_name']}',
            state=activity['text'],
            large_image=activity['image'],
            large_text=activity['tooltip'],
            small_image=activity['small_image'],
            small_text=activity['small_text']
        )
        
        if debug_mode:
            print(f'[DEBUG] Активное приложение: {activity['custom_name']}, текст: {activity['text']}, изображение: {activity['image']}, текст к изображению: {activity['tooltip']}, маленькое изображение: {activity['small_image']}, текст к маленькому изображению: {activity['small_text']}')
    else:
        rpc.update(details='Нет активного окна', large_image='default', large_text='Ожидание...')
        if debug_mode:
            print('[DEBUG] Нет активного окна')

def hide_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)

def restore_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 5)

def exit_app(icon):
    toast('Discord RPC', 'discord RPC module выключен!')
    icon.stop()
    os._exit(0)

def draw_icon():
    size = (64, 64)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill='blue')
    return image

def create_tray_icon():
    menu = Menu(
        MenuItem('🔻 Скрыть консоль', lambda: hide_console()),
        MenuItem('🔺 Восстановить консоль', lambda: restore_console()),
        MenuItem('❌ Выход', lambda icon, item: exit_app(icon))
    )
    icon = Icon('SyncTray', draw_icon(), menu=menu)
    icon.run()

if __name__ == '__main__':
    if trey_mode:
        tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
        tray_thread.start()
        time.sleep(1)  
    
    try:
        print('discord RPC module работает!')
        toast('Discord RPC', 'discord RPC module работает!')
        while True:
            update_activity()
            time.sleep(time_to_update)
    except KeyboardInterrupt:
        print('\ndiscord RPC module выключен!')
        toast('Discord RPC', 'discord RPC module выключен!')