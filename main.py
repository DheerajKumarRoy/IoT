from machine import Pin, reset, PWM, Timer
import ubluetooth
from ir_rx import NEC_16
import time



#pins
IR_pin=18
TimerLED_pin=32
Buzzer_Pin=19
ButLED_pin=25
Relay1_pin=14
Relay2_pin=27
Relay3_pin=26
Relay4_pin=15

#Indicators
#power-LED
TimerLED= Pin(TimerLED_pin, Pin.OUT)#red
#timer_pwm= PWM(TimerLED, freq=50)
#timer_pwm.duty(5)
#Buzzer
Buzzer= Pin(Buzzer_Pin, Pin.OUT)#buzzer
#but-press-led
ButLED= Pin(ButLED_pin, Pin.OUT)#Green

#Devices
Relay1= Pin(Relay1_pin, Pin.OUT)
Relay2= Pin(Relay2_pin, Pin.OUT)
Relay3= Pin(Relay3_pin, Pin.OUT)
Relay4= Pin(Relay4_pin, Pin.OUT)

#buttons={code:(button, pin, dev_name)}
#keys={'code':'action'}
    
#buttons={code:(button, pin, dev_name)}
btkeys = {
        'socket':Relay1,
        'bulb':Relay2,
        'fan':Relay3,
        'switch4':Relay4
       }
for value in btkeys.values():
    value.value(1)
    
#timer schedules
schedules = {}

def callback(data, addr, ctrl):
        if data > 0:  # NEC protocol sends repeat codes.
            code ='{:02x}'.format(data)
            print(code)
            
            
ble_msg = ""

class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):        
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global ble_msg
        
        if event == 1: #_IRQ_CENTRAL_CONNECT:
                       # A central has connected to this peripheral
            self.connected()

        elif event == 2: #_IRQ_CENTRAL_DISCONNECT:
                         # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()
        
        elif event == 3: #_IRQ_GATTS_WRITE:
                         # A client has written to this characteristic or descriptor.          
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()
            
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + 'n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray(b'\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("BT on!")
                # adv_data
                # raw: 0x02010209094553503332424C45
                # b'x02x01x02ttESP32BLE'
                #
                # 0x02 - General discoverable mode
                # 0x01 - AD Type = 0x01
                # 0x02 - value = 0x02
                
                # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
                # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics

ble = ESP32_BLE("D's_Switches")
#timer_time = int()
action = ''
timer = False
timer_led = False
def check_ble_msg(m):
    try:
        if m.isdigit():
            return True
        else:
            float(m)
            return True
    except ValueError:
        return False
def blink():
    ButLED.on()
    time.sleep_ms(50)
    ButLED.off()
    
while True:
    ir = NEC_16(Pin(IR_pin, Pin.IN), callback)
    if ble_msg:  # NEC protocol sends repeat codes.
            try:
                #print(ble_msg,end=' \r')
                if timer:
                    if ble_msg in btkeys.keys():
                        action = ble_msg
                        ble.send(f'\n<set time(mins) to schedule {action}>')      
                    elif check_ble_msg(ble_msg):
                        if action:
                            timer_time = time.mktime(time.localtime())+round(float(ble_msg)*60)
                            ble.send(f'\n<{action} will turn on in {ble_msg}mins>') if btkeys[action].value()==1 else ble.send(f'\n<{action} will turn off in {ble_msg}mins>')
                            schedules[action]=timer_time
                            timer_pwm= PWM(TimerLED, freq=50)
                            timer_pwm.duty(5)
                            timer_led = True
                            action = ''
                            timer = not timer
                        else:
                            ble.send(f'\n<shchedule an event first!>')
                    elif ble_msg=='timer':
                        ble.send('\n<nothing new scheduled!>\n')
                        timer = not timer
                    else:
                        ble.send('\n<enter a valid time/event!>\n')
                else:
                    if ble_msg in btkeys.keys():
                        btkeys[ble_msg].value(not btkeys[ble_msg].value())
                        ble.send(f'\n<{ble_msg} is turned off!>') if btkeys[ble_msg].value()==1 else ble.send(f'\n<{ble_msg} is turned on>')
                        if ble_msg in schedules.keys():
                            del schedules[ble_msg]
                    elif ble_msg=='timer':
                        ble.send(f'\n<set an event to schedule!>')
                        timer = not timer
                    elif ble_msg=='timer-off':
                        if schedules:
                            schedules = {}
                            ble.send('\n<timer off!>')
                        else:
                            ble.send('\n<nothing scheduled!>\n')
                    elif ble_msg=='power':
                        for value in btkeys.values():
                            value.value(1)
                        schedules = {}
                        ble.send('\n<power off!>')
                    elif ble_msg=='schedules':
                        if schedules:
                            ble.send('\n[scheduled events]')
                            for key, value in schedules.items():
                                time_left = str((value - time.mktime(time.localtime()))/60).split('.')
                                ble.send(f'\n<{key} turn off in {time_left[0]}mins, {int(float('0.'+time_left[1])*60)}secs!>') if btkeys[key].value()==0 else ble.send(f'\n<{key} turn on in {time_left[0]}mins, {int(float('0.'+time_left[1])*60)}secs!>')
                        else:
                            ble.send('\n<nothing scheduled!>\n')
                    else:
                        ble.send('\n<invalid command!>')
                ble_msg=''
                blink()
            except Exception as e:
                print(str(e))
    else:
        if schedules:
            for key, value in schedules.items():
                if value <=time.mktime(time.localtime()):
                    btkeys[key].value(not btkeys[key].value())
                    ble.send('\n[scheduled events]')
                    ble.send(f'\n<{key} turned off!>') if btkeys[key].value()==1 else ble.send(f'\n<{key} turned on!>')
                    del schedules[key]
                    blink()
                else:
                    continue
        elif timer_led:
            timer_pwm= PWM(TimerLED, freq=50)
            timer_pwm.deinit()
            timer_led = not timer_led
                
        
        
    
