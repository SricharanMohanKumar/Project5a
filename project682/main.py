import network # type: ignore
import time
from ntp_client import sync_time, format_time_string, format_time_id
import usocket as socket # type: ignore
import ussl as ssl # type: ignore
import sys
import machine
import ujson
from lib.third_party import rsa
from ubinascii import b2a_base64
from lib.third_party import string
from aes import aes_decrypt
import Micropython_Test

#initializing variables
ssid = password = atSign = ''
aesEncryptPrivateKey = aesEncryptPublicKey = aesPkamPrivateKey = aesPkamPublicKey = selfEncryptionKey = ''
privateKey = []

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

def main():
    #initializing variables
    global ssid, password, atSign, privateKey, aesEncryptPrivateKey, aesEncryptPublicKey, aesPkamPrivateKey, aesPkamPublicKey, selfEncryptionKey
    #stores the data read from settings.json
    ssid, password, atSign, privateKey = read_settings()
    #stores the data read from keys file
    aesEncryptPrivateKey, aesEncryptPublicKey, aesPkamPrivateKey, aesPkamPublicKey, selfEncryptionKey = read_key(atSign)
    pkamPrivateKey = aes_decrypt(aesPkamPrivateKey, selfEncryptionKey)

    # connecting to Wi-Fi
    wlan = network.WLAN(network.STA_IF)  # type: ignore
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected() and wlan.status() >= 0:
        time.sleep(1)
        print("Wi-Fi .. Connecting")

    print ("Wi-Fi Connected")
    # syncs the time with an NTP server
    sync_time()
    
    # displays the main menu
    while True:
        print("Welcome! What would you like to do?\n\t1) REPL\n\t2) REPL (from:atSign challenge is completed automatically)\n\t3) Get privateKey for @" + atSign + "\n\t4) Temperature sensor menu\n\t5) Test\n\t6) Exit")
        opt= input("> ")
        
        if int(opt) == 1 or int(opt) == 2:
            print(atSign)
            secondary = find_secondary(atSign)
            ss = connect_to_secondary(secondary)

            print('Connected\n')
            command = '@'
            
            if int(opt) == 2:
                 # automatically completes the challenge from the secondary
                response, command = send_verb(ss, 'from:' + atSign)
                if 'data:_' in response:
                    print("Signing challenge... (This process can take up to 1 minute)")
                    private_key = rsa.PrivateKey(privateKey[0], privateKey[1], privateKey[2], privateKey[3], privateKey[4])
                    challenge = response.replace('@data:', '')
                    signature = b42_urlsafe_encode(rsa.sign(challenge, private_key, 'SHA-256'))
                    print("signature: "+signature)
                    response, command = send_verb(ss, 'pkam:' + signature)
                    print('reached : '+response)
                else:
                    ss.close()
                    sys.exit(1)
            
            while True:
                # waits for user input and sends it to the secondary
                verb = str(input(command))
                response, command = send_verbs(ss, verb)
                print("resp :"+response)
                if('error:AT' in response): 
                    ss.close()
                    sys.exit(1)
                    
        elif int(opt) == 3:
            # generates a new private key and saves it to settings.json
            from pem_service import get_pem_parameters, get_pem_key
            
            pemKey = get_pem_key(pkamPrivateKey)
            privateKey = get_pem_parameters(pemKey)
            with open('settings.json', 'w') as w:
                # ujson.dump({"ssid": ssid, "password" : password, "atSign" : atSign, "privateKey" : privateKey}, w)
                # w.write("{\n\t\"ssid\": " + ssid + ",\n\t\"password\": " + password + ",\n\t\"atSign\": "+ atSign + ",\n\t\"privateKey\": [" + text[0] + ",\n\t" + text[1] + ",\n\t" + text[2] + ",\n\t" + text[3] + ",\n\t" + text[4] + "\n\t]\n}")

                w.write("{\n\t\"ssid\": \"" + ssid + "\",\n\t\"password\": \"" + password + "\",\n\t\"atSign\": \"" + atSign +
                        "\",\n\t\"privateKey\": [\n\t\t\t\t\t" + str(privateKey[0]) + ",\n\t\t\t\t\t" + str(privateKey[1]) + ",\n\t\t\t\t\t" + str(privateKey[2]) +
                        ",\n\t\t\t\t\t" + str(privateKey[3]) + ",\n\t\t\t\t\t" + str(privateKey[4]) + "\n\t\t\t\t  ]\n}")
                
            print("Your privateKey has been generated. Re-launch REPL to continue")
            sys.exit()
            
            
        elif int(opt) == 4:
            while True:
                print("Temperature sensor menu\n\t1) See current temperature\n\t2) Record current temperature\n\t3) Exit")
                tmp = input("> ")
                if int(tmp) == 1:
                    print("--------------------\n")
                    print(format_time_string() + "\nTemperature: " + str(measure_temp()))
                    print("\n--------------------")
                elif int(tmp) == 2:
                    tm = str(measure_temp())
                    verb = "update:" + str(format_time_id()) + ".temperature@" + atSign + " " + tm
                    secondary = find_secondary(atSign)
                    ts = connect_to_secondary(secondary)
                    print('Connected\n')
                    response, command = send_verb(ts, 'from:' + atSign)
                    print(response)
                    pkam = str(input(command))
                    response, command = send_verb(ts, pkam)
                    print(response)
                    if('success' in response): 
                        send_verb(ts, verb)
                        print("Current temperature measurement has been recorded:\n" + verb.replace('update:', '') + '\n')
                    else:
                        print('Could not record temperature: Wrong pkam')
                    ts.close()
                elif int(tmp) == 3:
                    break
                else:
                    print('Invalid option. Please enter a number in the range [1-3]')
            
        elif int(opt) == 6:
            #terminates the program
            sys.exit(1)
        elif int(opt) == 5:
            #run the test cases on this file
            print('Running tests...')
            test_case = Micropython_Test.TestMicropythonCode()
            test_case.test_find_secondary()
            test_case.test_send_verbs()
            test_case.test_read_settings()
            test_case.test_read_key()
            sys.exit()
        else:
            print('Invalid option. Please enter a number in the range [1-4]')
#send a verb to a socket and return the response
def send_verbs(skt, verb):
    # Print debug information
    print('skt: '+str(skt))
    print('verb: '+verb)
    # Send the verb to the socket and wait for a response
    skt.write((verb + "\r\n").encode())
    print('skt :' + str(skt))
    print('verb :'+ verb)
    time.sleep(1)
    response = b''
    data = skt.read()
    response += data
    # Split the response into separate parts
    parts = response.decode().split('\n')
    return parts[0], parts[1]
    
# sending a single verb to a socket and return the response
def send_verb(skt, verb):
    skt.write((verb + "\r\n").encode())
    time.sleep(1)
    response = b''
    data = skt.read()
    response += data
    parts = response.decode().split('\n')
    # If the verb is a llookup, decrypt the first part of the response
    if 'llookup:' in verb:
        content = parts[0].replace('data:', '')
        parts[0] = aes_decrypt(content, selfEncryptionKey)
        
    return parts[0], parts[1]
    
# Read the raw ADC value from the temperature sensor and convert it to a temperature value
def measure_temp():
    reading = sensor_temp.read_u16() * conversion_factor 
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature
# Open the settings file and load the JSON data
def read_settings():
    with open('settings.json') as f:
        info = ujson.loads(f.read())
        return info['ssid'], info['password'], info['atSign'].replace('@', ''), info['privateKey']
    
def read_key(atSign):
    # Build the path to the key file
    path = '/keys/@' + atSign + '_key.atKeys'
    # Open the key file and load the JSON data
    with open(path) as f:
        info = ujson.loads(f.read())
        # Return the encryption keys
        return info['aesEncryptPrivateKey'], info['aesEncryptPublicKey'], info['aesPkamPrivateKey'], info['aesPkamPublicKey'], info['selfEncryptionKey']

#function to connect to a secondary server
def connect_to_secondary(secondary):
    # Extract the address and port number from the secondary server information
    print('Connecting to secondary... ', end="")

    secondary = secondary.split(':')
    address = secondary[0]
    port = secondary[1]
    # Resolve the IP address of the secondary server
    a = socket.getaddrinfo(address, int(port))[0][-1]
    # Create a TCP socket and connect to the secondary server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    # try connecting to secondary
    try:
        s.connect(a)
    except OSError as e:
        if str(e) == '119': # For non-Blocking sockets 119 is EINPROGRESS
            print("In Progress")
        else:
            raise e
    # Set the socket to non-blocking and wrap it with SSL encryption.    
    s.setblocking(False)
    ss = ssl.wrap_socket(s, do_handshake = True)
    return ss
#function to find secondary server    
def find_secondary(atSign):
    print('Finding secondary for @' + atSign + '...')
    # Get the server address.
    a = socket.getaddrinfo('root.atsign.org', 64)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    # try connecting to secondary
    try:
        s.connect(a)
    except OSError as e:
        print("entered exception")
        if str(e) == '119': # For non-Blocking sockets 119 is EINPROGRESS
            print("In Progress")
        else:
            raise e
    # Set the socket to non-blocking and wrap it with SSL encryption.    
    s.setblocking(False)
    ss = ssl.wrap_socket(s, do_handshake = True)

    # Write the 'atSign' to the socket and wait for a response.
    ss.write((atSign + "\r\n").encode())
    time.sleep(1)

    # Extract the secondary address from the response and return it.
    response = b''
    data = ss.read()
    response += data
    secondary = response.decode().replace('@', '')
    secondary = secondary.replace('\r\n', '')
 
    # Close the socket and print the secondary address.
    ss.close()
    print('Address found: %s' % secondary)
    return secondary

def b42_urlsafe_encode(payload):
    return string.translate(b2a_base64(payload)[:-1].decode('utf-8'),{ ord('+'):'-', ord('/'):'_' })

if __name__ == '__main__':
    main()