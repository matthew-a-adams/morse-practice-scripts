from random import *
from qrz import QRZ

randomRST = {'599':100, '5NN':100, '589':50, '579':40, '569':5, '559':10, '549':5, '539':1, '529':1}

randomWeather = {'sunny':1, 'cloudy':1, 'rain':1, 'cold':1, 'hot':1, 'cldy':1, 'clear':1, 'oc':1}

randomRig = {'100W':100, 'KW':100, '1 KW':100, '5W':10, 'QRP':10}

randomAnt = {'EFHW':1, 'DIPOLE':1, '3 EL YAGI':1, 'YAGI':1, 'VERT':1, 'VERTICAL':1}

class Op:
    def __init__(self):
        qrz = QRZ('./settings.cfg')
        randomQRZOp  = qrz.randomOperator()

        self.call = randomQRZOp['call']
        self.RST = choices(randomRST.keys(), weights = list(randomRST.values()), k=1)
        self.call = randomQRZOp['addr2']
        self.call = randomQRZOp['fname']
        self.RST = choices(randomWeather.keys(), weights = list(randomWeather.values()), k=1)

        if randomQRZOp['country'] == 'United States':
            degrees = randint(-10, 110)
            if degrees < 0:
                self.temp = 'NEG ' + str(degrees * -1) + ' F'
            else:
                self.temp = str(degrees * -1) + ' F'
        else:
            degrees = randint(-40, 43)
            if degrees < 0:
                self.temp = 'NEG ' + str(degrees * -1) + ' C'
            else:
                self.temp = str(degrees * -1) + ' C'

        self.RST = choices(randomRig.keys(), weights = list(randomRig.values()), k=1)
        self.ant = choices(randomAnt.keys(), weights = list(randomAnt.values()), k=1)

    def callCQ(self):
        return 'CQ CQ CQ DE ' + self.call + ' ' + self.call + ' K'

    def answerCQ(self, receiver):
        return self.call + ' DE ' + receiver.call + ' K'