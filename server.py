import socket
import sys
import faceDetectionUsingImage
import time
import sleepwake_accelerometer
import heart_rate_detection
import BlueSerial

class Server:

    def __init__(self):
        self.host = "128.237.248.250"
        self.port = 8888
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = None
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as err:
            print ("Bind Failed, Error Code: " + str(err[0]) + ", Message: " + err[1])
            sys.exit()
        print ("Server started successfully")

    def connect(self):
        self.socket.listen(1)
        self.client, addr = self.socket.accept()
        print ('Connected with ' + addr[0] + ':' + str(addr[1]))

    def send(self, data):
        self.client.sendall(data)
        print ("Sent data to client")
        
    def disconnect(self):
        self.client.close()
        print ("Server stopped successfully")

def package_data(awoken, eyes, motion, hr):
    s = ""
    s += "Awoken: " + str(awoken) + "\n"
    s += "Heart Rate: " + str(hr) + "\n"
    s += "Eyes Open: " + str(eyes) + "\n"
    s += "Motion: " + str(motion) + "\n"
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


if __name__ == '__main__':
    server = Server()
    prev_awake = True
    next_awake = True
    while (1):
        ### expects data in this format
        ### "alert\nhr\neyes\nmotion\n"
        try:
            print("hi")
##            heartrateData,accData = BlueSerial.main()
            print("done")
##            eyes = faceDetectionUsingImage.main()
##            motion = sleepwake_accelerometer.main(accData)
##            hr = heart_rate_detection.main(heartrateData)
            eyes = "Open"
            hr = 170
            motion = True
            prev_awake, next_awake, awoken = update_awake(prev_awake, next_awake, [eyes, motion, hr])
            print(prev_awake, next_awake, awoken)
            data = package_data(awoken, hr, eyes, motion)
            server.connect()
            server.send(bytes(data))
            server.disconnect()
        except KeyboardInterrupt:
            server.socket.close()
        except Exception as e:
            server.socket.close()
            raise e
            break
    
     
