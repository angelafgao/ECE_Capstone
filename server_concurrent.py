import socket
import sys
#import faceDetectionUsingImage
import time
import sleepwake_accelerometer
import heart_rate_detection
import BlueSerial
import threading
motion = False
hr = 0
class Server:

    def __init__(self):
        self.host = "128.237.248.250"
        self.port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = None
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as err:
            print ("Bind Failed, Error Code: " + str(err[0]) + ", Message: " + err[1])
            sys.exit()
        print ("Server started successfully")

    def connect(self):
        print("aaah")
        self.socket.listen(1)
        self.client, addr = self.socket.accept()
        print ('Connected with ' + addr[0] + ':' + str(addr[1]))

    def send(self, data):
        self.client.sendall(data)
        print ("Sent data to client")
        
    def disconnect(self):
        self.client.close()
        print ("Server stopped successfully")

def package_data(awoken, hour, eyes, mot):
    s = ""
    s += "Awoken: " + str(awoken) + "\n"
    s += "Heart Rate: " + str(hour) + "\n"
    s += "Eyes Open: " + str(eyes) + "\n"
    s += "Motion: " + str(mot) + "\n"
    return s

def update_awake(prev_awake, next_awake, data):
    prev_awake = next_awake
    eyes, motion, hr = data
    if (eyes == "Open" and motion == True and hr > 140):
        next_awake = True
    awoken = False
    if (prev_awake == False and next_awake == True):
        awoken = True
    return prev_awake, next_awake, awoken

def updateSensorData(lock):
    global motion
    global hr
    print("we here")
    heartrateData,accData = BlueSerial.main()
    lock.acquire()
    motion = sleepwake_accelerometer.main(accData)
    hr = heart_rate_detection.main(heartrateData)
    #print("we here")
    lock.release()
    
    

server = Server()
prev_awake = True
next_awake = True
while (1):
    ### expects data in this format
    ### "alert\nhr\neyes\nmotion\n"
    try:
        print("hi")
        lock = threading.Lock()
        t1 = threading.Thread(target=updateSensorData, args=(lock,))
        t1.start()
        #heartrateData,accData = BlueSerial.main()
        print("done")
##            eyes = faceDetectionUsingImage.main()
##            motion = sleepwake_accelerometer.main(accData)
##            hr = heart_rate_detection.main(heartrateData)
        eyes = "Open"
        prev_awake, next_awake, awoken = update_awake(prev_awake, next_awake, [eyes, motion, hr])
        print(prev_awake, next_awake, awoken)
        #awoken = True
        data = package_data(awoken, hr, eyes, motion)
        server.connect()
        server.send(bytes(data))
        server.disconnect()
    except KeyboardInterrupt:
        print("socket closed")
        server.socket.close()
        sys.exit(0)
    except Exception as e:
        server.socket.close()
        raise e
        break

 

