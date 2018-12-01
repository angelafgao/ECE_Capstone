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

def package_data(eyes, motion, hr):
    return str(hr) + "\n" + str(eyes) + "\n" + str(motion) + "\n"


if __name__ == '__main__':
    server = Server()
    while (1):
        ### expects data in this format
        ### "hr\neyes\n\motion\n"
        try:
            BlueSerial.main()
            eyes = faceDetectionUsingImage.main()
            motion = sleepwake_accelerometer.test()
            hr = heart_rate_detection.main()
            data = package_data(eyes, motion, hr)
            server.connect()
            server.send(bytes(data))
            server.disconnect()
            time.sleep(10)
        except KeyboardInterrupt:
            server.socket.close()
        except:
            server.socket.close()
    
     
