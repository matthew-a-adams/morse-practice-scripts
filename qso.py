import time, warnings

from random import *
from qrz import QRZ

randomRST = {'599':100, '5NN':100, '589':50, '579':40, '569':5, '559':10, '549':5, '539':1, '529':1}

randomWeather = {'SUNNY':1, 'CLOUDY':1, 'RAIN':1, 'COLD':1, 'HOT':1, 'CLDY':1, 'CLEAR':1, 'OC':1}

randomRig = {'100W':100, 'KW':100, '1 KW':100, '5W':10, 'QRP':10}

randomAnt = {'EFHW':1, 'DIPOLE':1, '3 EL YAGI':1, 'YAGI':1, 'VERT':1, 'VERTICAL':1}

warnings.filterwarnings("ignore")

class Op:
    def __init__(self):
        qrz = QRZ('./settings.cfg')
        randomQRZOp  = qrz.randomOperator()

        self.call = randomQRZOp['call']

        self.RST = choices(list(randomRST.keys()), weights = list(randomRST.values()), k=1)[0]

        self.QTH = randomQRZOp['addr2']
        if randomQRZOp['country'] == 'United States':
            self.QTH += ' ' + randomQRZOp['state']
        self.QTH = self.QTH.upper()

        self.name = randomQRZOp['fname'].split()[0].upper()

        self.weather = choices(list(randomWeather.keys()), weights = list(randomWeather.values()), k=1)[0]

        if randomQRZOp['country'] == 'United States':
            degrees = randint(-10, 110)
            if degrees < 0:
                self.temp = 'NEG ' + str(degrees * -1) + ' F'
            else:
                self.temp = str(degrees) + ' F'
        else:
            degrees = randint(-40, 43)
            if degrees < 0:
                self.temp = 'NEG ' + str(degrees * -1) + ' C'
            else:
                self.temp = str(degrees) + ' C'

        self.rig = choices(list(randomRig.keys()), weights = list(randomRig.values()), k=1)[0]

        self.ant = choices(list(randomAnt.keys()), weights = list(randomAnt.values()), k=1)[0]

    def call_cq(self):
        return 'CQ CQ CQ DE ' + self.call + ' ' + self.call + ' K'

    def answer_cq(self, receiver):
        return receiver.call + ' DE ' + self.call + ' ' + self.call + ' K'

    def send_report(self, receiver, response = False):
        message = receiver.call + ' DE ' + self.call
        if response:
            message += ' FB ' + receiver.name
        else:
            message += ' THX FER CALL'
        message += ' UR RST IS ' + receiver.RST
        message += ' QTH IS ' + self.QTH + ' ' + self.QTH
        message += ' NAME IS ' + self.name + ' ' + self.name
        message += " HW CPY? "
        message += receiver.call + ' DE ' + self.call

        return message

    def send_secondary_report(self, receiver):
        message = receiver.call + ' DE ' + self.call
        message += ' SLD CPY ' + receiver.name
        message += ' WX HR IS ' + self.weather + ' TEMP IS ' + self.temp
        message += ' RIG RUNS ' + self.rig +  ' INTO ' + self.ant
        message += " HW CPY? "
        message += receiver.call + ' DE ' + self.call

        return message

    def send_signoff(self, receiver):
        message = receiver.call + ' DE ' + self.call
        message += ' SLD CPY ' + receiver.name
        message += ' THX FER QSO ' + receiver.name + ' ES 73 SK '
        message += receiver.call + ' DE ' + self.call

        return message

if __name__ == '__main__':

    caller = Op()
    callee = Op()

    print(caller.call_cq())

    time.sleep(3)

    print(callee.answer_cq(caller))

    time.sleep(3)

    print(caller.send_report(callee))

    time.sleep(3)

    print(callee.send_report(caller, True))

    time.sleep(3)

    print(caller.send_secondary_report(callee))

    time.sleep(3)

    print(callee.send_secondary_report(caller))

    time.sleep(3)

    print(caller.send_signoff(callee))

    time.sleep(3)

    print(callee.send_signoff(caller))