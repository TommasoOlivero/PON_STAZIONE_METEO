# Program for reading data on the davis Pro Vantage 2 station console
# PON 2021/2022 project
__author__ = "PyTrimons"

# import of the following libraries
import cv2
import numpy as np
from flask import Flask, render_template
import datetime
import time

app = Flask(__name__)

# camera settings
camera_port = 0
ramp_frames = 30

cam_l = cv2.VideoCapture(1)

brightness = 70
cam_l.set(cv2.CAP_PROP_BRIGHTNESS, brightness)

contrast = 90
cam_l.set(cv2.CAP_PROP_CONTRAST, contrast)

saturation = 0
cam_l.set(cv2.CAP_PROP_SATURATION, saturation)

exposure = 0
cam_l.set(cv2.CAP_PROP_EXPOSURE, exposure)


@app.route('/')
def index():

    ret, frame = cam_l.read()

    cv2.imwrite("./data/prova_luce.png", frame)
    
    print("foto salvata")
    #####################      global variables for various measurements       ###############
    pressione, temp_int, temp_est, umi_int, umi_est, rain, vento = {}, {}, {}, {}, {}, {}, {}

    #####################               training part                #########################
    samples = np.loadtxt('./data/generalsamples.data', np.float32)
    responses = np.loadtxt('./data/generalresponses.data', np.float32)
    responses = responses.reshape((responses.size, 1))

    model = cv2.ml.KNearest_create()
    model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    #####################    machine learning display by 'yan9yu'    #########################

    im = cv2.imread('./data/prova_luce.png')
    out = np.zeros(im.shape, np.uint8)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 27), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        if cv2.contourArea(cnt) > 50:
            [x, y, w, h] = cv2.boundingRect(cnt)
            if h > 28:
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
                roi = thresh[y:y + h, x:x + w]
                roismall = cv2.resize(roi, (10, 10))
                roismall = roismall.reshape((1, 100))
                roismall = np.float32(roismall)
                retval, results, neigh_resp, dists = model.findNearest(
                    roismall, k=1)
                string = str(int((results[0][0])))
                cv2.putText(out, string, (x, y + h), 0, 1, (0, 255, 0))

    ############################# Data processing part based on the position on the display #################################

                if(y > 155 and y < 185):
                    if(x > 460 and x < 600):            # PRESSURE #
                        pressione[x] = results[0][0]

                    elif(x > 320 and x < 350):          # EXTERNAL TEMPERATURE #
                        temp_est[x] = results[0][0]

                    elif(x > 350 and x < 450):          # EXTERNAL HUMIDITY #
                        umi_est[x] = results[0][0]

                elif(y > 150 and y < 190):
                    if(x > 150 and x < 180):            # WIND SPEED #
                        vento[x] = results[0][0]

                elif(y > 220 and y < 260):
                    if(x > 350 and x < 460):            # INTERNAL HUMIDITY #
                        umi_int[x] = results[0][0]

                    elif(x > 290 and x < 350):          # INTERNAL TEMPERATURE #
                        temp_int[x] = results[0][0]

                elif(y > 310 and y < 345):              # DAYLI RAIN #
                    rain[x] = results[0][0]


    if pressione == {}:
        pressione_valore = "Valore non rilevato"
    else:
        pressione_valore = ordinamento(pressione)
        
    if vento == {}:
        vento_valore = "0"
    else:
        vento_valore = ordinamento(vento)

    if umi_est == {}:
        umi_est_valore = "Valore non rilevato"
    else:
        umi_est_valore = ordinamento(umi_est)
        
    if umi_int == {}:
        umi_int_valore = "Valore non rilevato"
    else:
        umi_int_valore = ordinamento(umi_int)

    if temp_est == {}:
        temp_est_valore = "Valore non rilevato"
    else:
        temp_est_valore= ordinamento(temp_est)

    if temp_int == {}:
        temp_int_valore = "Valore non rilevato"
    else:
        temp_int_valore = ordinamento(temp_int)

    if rain == {}:
        rain_valore = "Valore non rilevato"
    else:
        rain_valore = ordinamento(rain)
    

    data = datetime.date.today()
    ora = datetime.datetime.now().strftime("%H:%M:%S")

    # sending data on the website
    return render_template('dati.html', data=data, ora=ora, pressione_valore = pressione_valore,
                                        temp_est_valore = temp_est_valore, temp_int_valore=temp_int_valore,
                                        umi_est_valore=umi_est_valore,umi_int_valore=umi_int_valore,
                                        vento_valore=vento_valore, rain_valore = rain_valore)


    
# function for sorting the data according to the position on the abscissa
def ordinamento(dizionario):          

    lista = [elem for elem in dizionario]
    lista.sort()

    dizionario_ordinato = {}
    for cor in lista:
        for valore in dizionario:
            if(cor == valore):
                dizionario_ordinato[valore] = dizionario[valore]

    dizionario_ordinato = doppio_zero(dizionario_ordinato)
    return dizionario_ordinato

# function for checking the presence of double zero and possible removal of one
def doppio_zero(dizionario):
    cont, lista_zeri = 0, []

    for k in dizionario:
        if(dizionario[k] == 0):
            cont += 1
            valChiave = k
            if(cont == 2):
                if(dizionario[valChiave] == 0):
                    lista_zeri.append(valChiave)
                    valChiave = 0
    for i in lista_zeri:
        del dizionario[i]
    dizionario = dizionario_numero(dizionario)
    return dizionario

# function for creating real value
def dizionario_numero(dizionario):  
    numero_stringa = ""
    for ind, chiave in enumerate(dizionario):
        if(ind == 3):
            numero_stringa += "."
        numero_stringa += str(int(dizionario[chiave]))

    return numero_stringa

def main():
    app.run(debug=True, host='127.0.0.1', port=5000) # run flask application
    
if __name__ == "__main__":
    main()