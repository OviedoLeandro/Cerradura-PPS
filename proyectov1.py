from machine import Pin, Timer
import urequests as requests
# Import time
import time
import utime
import machine
import network
# Import lcd_4bit_mode
#         import lcd_4bit_mode
# Initialize LCD pins
RS = machine.Pin(4,machine.Pin.OUT)
ENABLE = machine.Pin(5,machine.Pin.OUT)
BACK_LIGHT = machine.Pin(6,machine.Pin.OUT)
D4 = machine.Pin(18,machine.Pin.OUT)
D5 = machine.Pin(19,machine.Pin.OUT)
D6 = machine.Pin(20,machine.Pin.OUT)
D7 = machine.Pin(21,machine.Pin.OUT)                  
 
# CONSTANTS
KEY_UP   = const(0)
KEY_DOWN = const(1)
keys = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'], ['7', '8', '9', 'C'], ['*', '0', '#', 'D']]
# RPi Pico pin assignments
rows = [8,9,10,11]
cols = [12,13,15,16]
# Set pins for rows as outputs
row_pins = [Pin(pin_name, mode=Pin.OUT) for pin_name in rows]
# Set pins for columns as inputs
col_pins = [Pin(pin_name, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin_name in cols]
#Initialize the onboard LED as output
led = Pin("LED", Pin.OUT)
#Initialize timer_one. Used for toggling the LED
timer_one = Timer()
#Initialize timer_two. Used for polling keypad
timer_two = Timer()
#Initialize timer_three. Used for polling status (cloud input)
# timer_three = Timer()
#Initialize timer_four. Used for polling password change (cloud input)
timer_four = Timer()

#Variable de estados
key_status = [[KEY_UP, KEY_UP, KEY_UP, KEY_UP], [KEY_UP, KEY_UP, KEY_UP, KEY_UP], [KEY_UP, KEY_UP, KEY_UP, KEY_UP], [KEY_UP, KEY_UP, KEY_UP, KEY_UP]]

#Password valida
default_password = '1234'
valid_password = ''

#Password en pantalla
screen_password = '1234'

#estatus de la cerradura (abierta o cerrada) que se puede acceder desde internet
cloud_lock_status = False


def LocalBlinkLED(timer):
    led.toggle()
    
def InitKeypad():
    for row in range(0,4):
        for col in range(0,4):
            row_pins[row].low()
            
def LocalPollKeypad(timer):
    global screen_password
    global valid_password
    global cloud_lock_status 
    
#    key = None
#    for row in range(4):
#        for col in range(4):
#            # Set the current row to high
#            row_pins[row].high()
#            # Check for key pressed events
#            if col_pins[col].value() == KEY_DOWN:
#                key = KEY_DOWN
#            if col_pins[col].value() == KEY_UP:
#                key = KEY_UP
#                
#            row_pins[row].low()
#            if key == KEY_DOWN and key != key_status[row][col] and not((row == 0 and col == 3) or (row == 1 and col == 3) or (row == 2 and col == 3) or (row == 3 and col == 0) or (row == 3 and col == 2)):
#                if not (row == 3 and col == 3):    
#                    display.WriteLine("                ",2)
#                    last_key_press = keys[row][col]
#        
#                    screen_password += last_key_press 
#                    
#                    display.WriteLine(screen_password,2)
#                    
#                    print("Se toco: " + last_key_press)
#                    key_status[row][col] = key
#                
#                else:
                    #Chequeo de password
    is_valid_password = get_cloud_password(screen_password)
    if is_valid_password or cloud_lock_status:
        display.WriteLine('   BIENVENIDO ',1)
        display.WriteLine('   Password OK ',2)
        led.high()
        print("SOS UN CAPO")
        #screen_password = ''
        time.sleep(3)
        display.WriteLine('   Password:   ',1)
        display.WriteLine(' Ingrese aqui  ',2)
        cloud_lock_status = False
        
        
    else:
        display.WriteLine('',1)
        display.WriteLine('  Incorrecto!  ',2)
        #screen_password = ''
        time.sleep(3)
        display.WriteLine('   Password:   ',1)
        display.WriteLine(' Ingrese aqui  ',2)
                
#            if key == KEY_UP:
#                key_status[row][col] = key
                
                        
                        
                
class LCD16x2:
    
    def __init__(self, RS, ENABLE, BACK_LIGHT, D4, D5, D6, D7):
        self.RS = RS
        self.ENABLE = ENABLE
        self.BACK_LIGHT = BACK_LIGHT
        self.D4 = D4
        self.D5 = D5
        self.D6 = D6
        self.D7 = D7
        self.Reset()
    
    def Reset(self):
        self.RS.value(0)
        self.WriteCommand(0x03)
        self.WriteCommand(0x03)
        self.WriteCommand(0x03)
        
        #Initialize LCD into 4 bit mode
        self.WriteCommand(0x02)
        
        #Enable 5x7 character mode
        self.WriteCommand(0x28)
        
        #Cursor off
        self.WriteCommand(0x0C)
        
        #Increment cursor
        self.WriteCommand(0x06)
        
        #Clear screen
        self.WriteCommand(0x01)
        
        #Sleep for two mSeconds
        utime.sleep_ms(2)
     
    # Generate EnablePulse
    def EnablePulse(self):
        self.ENABLE.value(1)
        utime.sleep_us(40)
        self.ENABLE.value(0)
        utime.sleep_us(40)

    # Write a byte to LCD
    # Separate into 2 nibbles and then write to LCD
    def WriteByte(self, data):
       self.D4.value((data & 0b00010000) >>4)
       self.D5.value((data & 0b00100000) >>5)
       self.D6.value((data & 0b01000000) >>6)
       self.D7.value((data & 0b10000000) >>7)
       self.EnablePulse()
       
       self.D4.value((data & 0b00000001) >>0)
       self.D5.value((data & 0b00000010) >>1)
       self.D6.value((data & 0b00000100) >>2)
       self.D7.value((data & 0b00001000) >>3)
       self.EnablePulse()
       
    # Write a command to LCD
    def WriteCommand(self, data):
        # Disable Register Select
        self.RS.value(0)
        # Write Command Byte to LCD
        self.WriteByte(data)
        
    # Write a data to LCD
    def WriteData(self, data):
        # Enable Register Select
        self.RS.value(1)
        # Write Command Byte to LCD
        self.WriteByte(data)
        # Disable Register Select
        self.RS.value(0)
    
    # Writes a string into Line 1 or Line2
    def WriteLine(self, string, line_number):
        if(line_number == 1):
            self.WriteCommand(0x80)
            for x in string:
                self.WriteData(ord(x))
        if(line_number == 2):
            self.WriteCommand(0xC0)
            for x in string:
                self.WriteData(ord(x))    
    # Clear Screen
    def ClearScreenCursorHome(self):
        self.WriteCommand(0x01)
        self.WriteCommand(0x02)
        # Clear screen and put the cursor into Home needs longer time
        # Introduce two mSeconds delay
        utime.sleep_ms(2)
        
    # Back light On
    def BackLightOn(self):
        self.BACK_LIGHT.value(1)
        
    # Back light Off
    def BackLightOff(self):
        self.BACK_LIGHT.value(0)
        
    # Cursor On
    def CursorOn(self):
        self.WriteCommand(0x0E)

    # Cursor Blinking
    def CursorBlink(self):
        self.WriteCommand(0x0D)
        
    # Cursor Off
    def CursorOff(self):
        self.WriteCommand(0x0C)
                
    
#check if a new password is available in case cloud service is up
def get_cloud_password(local_pass):
    global valid_password
    global cloud_lock_status
    
    url_password = "https://pinpad-caece.herokuapp.com/api/check-password/"+local_pass
        
    try:
        r = requests.get(url_password)
        print(r.json()) 
        if r.json().get('unlock'):
            cloud_lock_status = True
            valid_password = local_pass
            return True
        return False
    except:
        print("CloudNewPassword - Servicio no disponible")
        
        #if connection is not available, compare against last valid password
        if valid_password and valid_password == local_pass:
            return True
            
        #if not connection and not valid pass set, use default
        if not valid_password and default_password == local_pass:
            return True
        
    return False
            
            
            
    
def CloudStatusLock(timer):
    global cloud_lock_status 
    
    url_lock_status = "https://pinpad-caece.herokuapp.com/api/status"
        
    try:
        r = requests.get(url_lock_status)
        cloud_lock_status = r.json().get('unlock')
        print(r.json())
        print(cloud_lock_status)
        if cloud_lock_status:
            led.high()
        else:
            led.low()
    except:
        print("CloudStatusLock - Servicio no disponible")


    
    
                
# Initialize and set all the rows to low
InitKeypad()
display = LCD16x2(RS,ENABLE,BACK_LIGHT,D4,D5,D6,D7)

# Turn on Back light
display.BackLightOn()

# Welcome string
display.WriteLine('   Password:   ',1)
display.WriteLine(' Ingrese aqui  ',2)
display.CursorOff()

# Wait for five seconds
led.off()
time.sleep(5)

def WifiConnection():
    ssid = 'Cerradura'
    password = 'Grupo 3 '

    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
      pass

    print('Connection successful')
    print(station.ifconfig())

    #led.on()

WifiConnection()

#local inputs
#timer_one.init(freq=5, mode=Timer.PERIODIC, callback=LocalBlinkLED)
timer_two.init(freq=1, mode=Timer.PERIODIC, callback=LocalPollKeypad)

#cloud inputs
timer_four.init(freq=1, mode=Timer.PERIODIC, callback=CloudStatusLock)

