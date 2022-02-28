from PySimpleGUI import PySimpleGUI as sg

import uuid
import cv2

from os import listdir
from src.logger import logger, loggerMapClicked
from random import random, randint
from random import random

import numpy as np
import mss
import pyautogui
import time
import sys
import pygetwindow as pw

import yaml

def get_window(n):
    window = pw.getWindowsWithTitle('Bombcrypto')
    if pw.getActiveWindow() is not window[n]:
        try:
            window[n].activate()
            if window[n].isMaximized == False:
                window[n].maximize()
                print('Maximizada')
        except:
            window[n].minimize()
            window[n].maximize()
    else:
        pass

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images(dir_path='./imgs/'):
    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'imgs/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:,:,:3]

def position(target, threshold=0.85,img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    if len(rectangles) > 0:
        x,y, w,h = rectangles[0]
        return (x+(w/2),y+h/2)

    return positions

def add(img0, img1):
    return cv2.bitwise_and(img0, img1, mask = None)

if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)

    ct = c['threshold']
    ch = c['home']

    pause = c['time_intervals']['interval_between_moviments']
    pyautogui.PAUSE = pause

    pyautogui.FAILSAFE = False
    hero_clicks = 0
    login_attempts = 0
    last_log_is_progress = False

def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)

def load_imagesmain():
    file_names = listdir('./imgs/')
    targets = {}
    for file in file_names:
        path = 'imgs/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

images = load_imagesmain()

def loadHeroesToSendHome():
    file_names = listdir('./imgs/home-priority')
    heroes = []
    for file in file_names:
        path = './imgs/home-priority/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d heroes that should be sent home loaded' % len(heroes))
    return heroes

def show(rectangles, img = None):

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickBtn(img, timeout=3, threshold = ct['default']):
    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches)==0):
            has_timed_out = time.time()-start > timeout
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True

    return False
def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def scroll():

    commoms = positions(images['commom-text'], threshold = ct['commom'])
    if (len(commoms) == 0):
        return
    x,y,w,h = commoms[len(commoms)-1]
#
    moveToWithRandomness(x,y,1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')


def clickButtons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)

def isHome(hero, buttons):
    y = hero[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            # if send-home button exists, the hero is not home
            return False
    return True

def isWorking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickGreenBarButtons():
    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 130

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d buttons detected' % len(buttons))


    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d buttons with green bar detected' % len(not_working_green_bars))
        logger('👆 Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            logger('⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)

def clickFullBarButtons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)

def goToHeroes():
    if clickBtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0
    #TODO tirar o sleep quando colocar o pulling
    time.sleep(1)
    clickBtn(images['hero-icon'])
    time.sleep(1)

def goToGame():
    # in case of server overload popup
    clickBtn(images['x'])
    # time.sleep(3)
    clickBtn(images['x'])

    clickBtn(images['treasure-hunt-icon'])

def refreshHeroesPositions():

    logger('🔃 Refreshing Heroes Positions')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])

    # time.sleep(3)
    clickBtn(images['treasure-hunt-icon'])

def login():
    global login_attempts
    logger('😿 Checking if game has disconnected')

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    if clickBtn(images['connect-wallet'], timeout = 10):
        login_attempts = login_attempts + 1
        logger('🎉 Connect wallet button detected, logging in!')
        #TODO mto ele da erro e poco o botao n abre
        # time.sleep(10)

    if clickBtn(images['select-wallet-2'], timeout=10):
        # sometimes the sign popup appears imediately
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        if clickBtn(images['treasure-hunt-icon'], timeout = 15):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        return
        # click ok button

    if not clickBtn(images['select-wallet-1-no-hover']):
        if clickBtn(images['select-wallet-1-hover'],threshold  = ct['select_wallet_buttons'] ):
            pass
            # o ideal era que ele alternasse entre checar cada um dos 2 por um tempo 
            # print('sleep in case there is no metamask text removed')
            # time.sleep(20)
    else:
        pass
        # print('sleep in case there is no metamask text removed')
        # time.sleep(20)

    if clickBtn(images['select-wallet-2'], timeout = 20):
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        # time.sleep(25)
        if clickBtn(images['treasure-hunt-icon'], timeout=25):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        # time.sleep(15)

    if clickBtn(images['ok'], timeout=5):
        logger('Error message.')
        pass
        # time.sleep(15)
        # print('ok button clicked')


def sendHeroesHome(activehome):
    if not activehome:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len (hero_positions) == 0:
            #TODO maybe pick up match with most wheight instead of first
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return
    print(' %d heroes that should be sent home found' % n)
    # if send-home button exists, the hero is not home
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    # TODO pass it as an argument for both this and the other function that uses it
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not isHome(position,go_home_buttons):
            print(isWorking(position, go_work_buttons))
            if(not isWorking(position, go_work_buttons)):
                print ('hero not working, sending him home')
                moveToWithRandomness(go_home_buttons[0][0]+go_home_buttons[0][2]/2,position[1]+position[3]/2,1)
                pyautogui.click()
            else:
                print ('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')

def refreshHeroes(activehome, mode):
    logger('🏢 Search for heroes to work')

    goToHeroes()

    if mode == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif mode == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']

    while(empty_scrolls_attempts >0):
        if mode == 'full':
            buttonsClicked = clickFullBarButtons()
        elif mode == 'green':
            buttonsClicked = clickGreenBarButtons()
        else:
            buttonsClicked = clickButtons()

        sendHeroesHome(activehome)

        if buttonsClicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    logger('💪 {} heroes sent to work'.format(hero_clicks))
    goToGame()

def browserslist():
    window = pw.getWindowsWithTitle('Bombcrypto')
    lista = []
    for i in range(len(window)):
        lista.append(f"Bombcrypto {i+1}")
    if len(lista) == 0:
        return "Bombcrypto não encontrado."
    return lista

home_heroes = loadHeroesToSendHome()

def main(activehome, mode, multiaccount):

    time.sleep(1)
    t = c['time_intervals']

    last = {}
    for j in range(multiaccount):
        last["login_%s"%j] = 0
        last["heroes_%s"%j] = 0
        last["new_map_%s"%j] = 0
        last["check_for_captcha_%s"%j] = 0
        last["refresh_heroes_%s"%j] = 0

    d = {}
    
    while True:

        for i in range(multiaccount):
            get_window(i)
            
            d['time_%s'%str(i)] = time.time()
            if i >0:
                print("\n",d['time_%s'%(i-1)])
            print(d['time_%s'%(i)])
            
            #now = time.time()

            time.sleep(2)
            if d['time_%s'%i] - last["check_for_captcha_%s"%i] > addRandomness(t['check_for_captcha'] * 60):
                last["check_for_captcha_%s"%i] = d['time_%s'%i]

            if d['time_%s'%i] - last["heroes_%s"%i] > addRandomness(t['send_heroes_for_work'] * 60):
                last["heroes_%s"%i] = d['time_%s'%i]
                refreshHeroes(activehome,mode)

            if d['time_%s'%i] - last["login_%s"%i] > addRandomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last["login_%s"%i] = d['time_%s'%i]
                login()

            if d['time_%s'%i] - last["new_map_%s"%i] > t['check_for_new_map_button']:
                last["new_map_%s"%i] = d['time_%s'%i]

                if clickBtn(images['new-map']):
                    loggerMapClicked()


            if d['time_%s'%i] - last["refresh_heroes_%s"%i] > addRandomness( t['refresh_heroes_positions'] * 60):
                last["refresh_heroes_%s"%i] = d['time_%s'%i]
                refreshHeroesPositions()

            #clickBtn(teasureHunt)
            logger(None, progress_indicator=True)

            sys.stdout.flush()

            time.sleep(1)


def janela_bot():
    sg.theme('LightGrey')
    values = 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    layout = [
        [sg.Titlebar('BomberBot')],
        [sg.Text('Esteja com o jogo ABERTO!')],
        [sg.Text("MultiAccount:")],
        [sg.InputCombo((values),key="multiaccount",default_value=1,readonly=True),sg.Button('Detect Browser')],
        [sg.Text("Modo House:")],
        [sg.Checkbox('Home',key='Home')],
        [sg.Text('Selecionar Hero:')],
        [sg.Radio('Full Stamina', 'Radio01', default=True,key='FullS'), sg.Radio('Green Stamina','Radio01', default=False,key='GreenS')],
        [sg.Text('Discord: L4wless#5627',text_color='Blue')],
        [sg.Button('Play'),sg.Button('UUID')],
    ]
    return sg.Window('BomberBot', layout=layout,finalize=True)

def janela_check():
    sg.theme('LightGrey')
    layout = [
        [sg.Titlebar('UUID Checker')],
        [sg.Button('Check'),sg.Button('Voltar')],
    ]
    return sg.Window('UUID Checker', layout=layout,finalize=True)


#Main
window1, window2 = janela_bot(), None

while True:
    window,event,values = sg.read_all_windows()
    if window == window1 and event == sg.WINDOW_CLOSED:
        break
    if window == window1 and event == 'UUID':
        window2 = janela_check()
        window1.hide()
    if window == window2 and event == sg.WINDOW_CLOSED:
        break
    if window == window2 and event == 'Voltar':
        window2.hide()
        window1.un_hide()
    if window == window2 and event == 'Check':
        sg.popup(f'Seu Código UUID: {uuid.getnode()}')
    if window == window1 and event == 'Detect Browser':
        sg.popup_scrolled(browserslist(),title="Detected")

    if window == window1 and event == 'Play':
        nav = values
        if uuid.getnode() == uuid.getnode(): #Setar UUID de quem comprou.
            if nav['Home'] == True and nav['GreenS'] == True:
                if len(browserslist()) < nav['multiaccount'] or browserslist()=="Bombcrypto não encontrado.":
                    sg.Popup("MultiAccount Error: \nValor é maior que a quantidade de games encontrados!")
                else:
                    main(True,'green',nav['multiaccount'])
            
            elif nav['Home'] == True and nav['FullS'] == True:
                if len(browserslist()) < nav['multiaccount'] or browserslist()=="Bombcrypto não encontrado.":
                    sg.Popup("MultiAccount Error: \nValor é maior que a quantidade de games encontrados!")
                else:
                    main(True,'full',nav['multiaccount'])
            
            elif nav['Home'] == False and nav['FullS'] == True:
                if len(browserslist()) < nav['multiaccount'] or browserslist()=="Bombcrypto não encontrado.":
                    sg.Popup("MultiAccount Error: \nValor é maior que a quantidade de games encontrados!")
                else:
                    main(False,'full',nav['multiaccount'])

            elif nav['Home'] == False and nav['GreenS'] == True:
                if len(browserslist()) < nav['multiaccount'] or browserslist()=="Bombcrypto não encontrado.":
                    sg.Popup("MultiAccount Error: \nValor é maior que a quantidade de games encontrados!") 
                else:
                    main(False,'green',nav['multiaccount'])
            
            else:
                sg.popup("Error!")
        else:
            sg.popup("UUID desconhecido.")
            SystemExit
            break