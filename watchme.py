import subprocess

import PySimpleGUIQt as sg

TRICKS_FILE = '/Users/liamcryan/PycharmProjects/watchlog/tricks.yaml'

menu_def = ['BLANK', ['Restart', '---', 'Exit']]
tray = sg.SystemTray(menu=menu_def,
                     filename=r'icon.png',
                     )


def watch_process() -> subprocess.Popen:
    return subprocess.Popen(['watchmedo', 'tricks-from', 'tricks.yaml'], shell=False)


process = watch_process()

while True:
    menu_item = tray.read()

    if menu_item == 'Exit':
        process.kill()
        process.wait()
        break
    if menu_item == 'Restart':
        process.kill()
        process.wait()
        process = watch_process()
