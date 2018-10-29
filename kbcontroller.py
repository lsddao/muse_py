from pynput.keyboard import Controller, KeyCode

controller = Controller()

vk_nextTrack = 0xB0
vk_stop = 0xB2
vk_playPause = 0xB3

def pressKey(vk):
    controller.press(KeyCode.from_vk(vk))
    controller.release(KeyCode.from_vk(vk))

def nextTrack():
    pressKey(vk_nextTrack)

def playPause():
    pressKey(vk_playPause)

def stop():
    pressKey(vk_stop)