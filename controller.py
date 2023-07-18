import sys
import threading
import time

from copy import deepcopy
from datetime import datetime

try:
    import Queue
except ImportError:  # Python 3
    import queue as Queue

import u6

from LJTickDAC import *

# MAX_REQUESTS is the number of packets to be read.
MAX_REQUESTS = 20
# SCAN_FREQUENCY is the scan frequency of stream mode in Hz.
SCAN_FREQUENCY = 50000


class StreamDataReader(object):
    def __init__(self, device):
        self.device = device
        self.data = Queue.Queue()
        self.dataCount = 0
        self.missed = 0
        self.finished = False

    def readStreamData(self):
        self.finished = False

        print("Start stream.")
        start = datetime.now()
        try:
            self.device.streamStart()
            while not self.finished:
                # Calling with convert = False, because we are going to convert in
                # the main thread.
                returnDict = next(self.device.streamData(convert=False))
                #returnDict = self.device.streamData(convert=False).next()  # Python 2.5
                if returnDict is None:
                    print("No stream data")
                    continue

                self.data.put_nowait(deepcopy(returnDict))

                self.missed += returnDict["missed"]
                self.dataCount += 1
                if self.dataCount >= MAX_REQUESTS:
                    self.finished = True

            print("Stream stopped.\n")
            self.device.streamStop()
            stop = datetime.now()

            # Delay to help prevent print text overlapping in the two threads.
            time.sleep(0.200)

            sampleTotal = self.dataCount * self.device.packetsPerRequest * self.device.streamSamplesPerPacket
            scanTotal = sampleTotal / 1  # sampleTotal / NumChannels

            print("%s requests with %s packets per request with %s samples per packet = %s samples total." %
                  (self.dataCount, self.device.packetsPerRequest, self.device.streamSamplesPerPacket, sampleTotal))

            print("%s samples were lost due to errors." % self.missed)
            sampleTotal -= self.missed
            print("Adjusted number of samples = %s" % sampleTotal)

            runTime = (stop-start).seconds + float((stop-start).microseconds)/1000000
            print("The experiment took %s seconds." % runTime)
            print("Actual Scan Rate = %s Hz" % SCAN_FREQUENCY)
            print("Timed Scan Rate = %s scans / %s seconds = %s Hz" %
                  (scanTotal, runTime, float(scanTotal)/runTime))
            print("Timed Sample Rate = %s samples / %s seconds = %s Hz" %
                  (sampleTotal, runTime, float(sampleTotal)/runTime))
        except Exception:
            try:
                # Try to stop stream mode. Ignore exception if it fails.
                self.device.streamStop()
            except:
                pass
            self.finished = True
            e = sys.exc_info()[1]
            print("readStreamData exception: %s %s" % (type(e), e))


def init_controller():
    d = None

    # At high frequencies ( >5 kHz), the number of samples will be MAX_REQUESTS
    # times 48 (packets per request) times 25 (samples per packet)
    d = u6.U6()

    # For applying the proper calibration to readings.
    d.getCalibrationData()

    print("Configuring U6 stream")
    # d.streamConfig(NumChannels=1, ChannelNumbers=[2], ChannelOptions=[0], SettlingFactor=1, ResolutionIndex=1, ScanFrequency=SCAN_FREQUENCY)
    # d.streamConfig(NumChannels=2, ChannelNumbers=[0,1], ChannelOptions=[0,0], SettlingFactor=1, ResolutionIndex=1, ScanFrequency=SCAN_FREQUENCY)
    d.streamConfig(NumChannels=3, ChannelNumbers=[0,1,2], ChannelOptions=[0,0,0], SettlingFactor=1, ResolutionIndex=1, ScanFrequency=SCAN_FREQUENCY)

    # dac = LJTickDAC(d, 0)

    if d is None:
        print("""Configure a device first.
    Please open streamTest-threading.py in a text editor and uncomment the lines for your device.

    Exiting...""")
        sys.exit(0)

    tdac = LJTickDAC(d, 0)

    return d, tdac

def clamp(tdac):
    # print('clamping')
    tdac.update(5.0)

def setVoltage(tdac, v):
    # DAC0_VALUE = d.voltageToDACBits(v, dacNumber = 0, is16Bits = False)
    # d.getFeedback(u6.DAC0_8(DAC0_VALUE))
    dacA = v
    tdac.update(dacA)

def wait(app, t):
    counter = 0.0
    while(counter < float(t)):
        app.update()
        time.sleep(0.1)
        counter += 0.1
    # time.sleep(t)
    return

# Reads from AIN0, AIN1, AIN2 and returns as tuple
def read(d):
    return(d.getAIN(0), d.getAIN(1), d.getAIN(2))

def per_sec(app, d, t, start_time, times, sp_list,
            gdl_tpr, gdl_tpr_list, tprs, crs
            ):
    step_start = time.time()
    step_end = step_start + t
    print(t)
    while(time.time() < step_end):
        reading = read(d)
        times.append(time.time()-start_time)
        sp_list.append(reading[2]) # Voltage -> pressure calculation
        tprs.append(reading[0] - gdl_tpr)
        crs.append(reading[1] - 0.5*gdl_tpr)     
        gdl_tpr_list.append(gdl_tpr)   
        app.update()
    reading = read(d)
    return

# def script_measure(app, d, t, start_time, gdl_tpr):
#     step_start = time.time()
#     step_end = step_start + t
#     print(t)
#     while(time.time() < step_end):
#         reading = read(d)
#         app.update()
#     reading = read(d)
#     return


def read_stream(d):
    v_1 = []
    v_2 = []
    v_3 = []
    
    sdr = StreamDataReader(d)

    sdrThread = threading.Thread(target=sdr.readStreamData)

    # Start the stream and begin loading the result into a Queue
    sdrThread.start()

    errors = 0
    missed = 0
    # Read from Queue until there is no data. Adjust Queue.get timeout
    # for slow scan rates.
    while True:
        try:
            # Pull results out of the Queue in a blocking manner.
            result = sdr.data.get(True, 1)

            # If there were errors, print that.
            if result["errors"] != 0:
                errors += result["errors"]
                missed += result["missed"]
                print("+++++ Total Errors: %s, Total Missed: %s +++++" % (errors, missed))

            # Convert the raw bytes (result['result']) to voltage data.
            r = d.processStreamData(result['result'])

            # Do some processing on the data to show off.
            x = (len(r['AIN0']), sum(r['AIN0'])/len(r['AIN0']))
            y = (len(r['AIN1']), sum(r['AIN1'])/len(r['AIN1']))
            z = (len(r['AIN2']), sum(r['AIN2'])/len(r['AIN2']))
            print("Average of %s reading(s) x: %s" % x)
            print("Average of %s reading(s) y: %s" % y)
            print("Average of %s reading(s) z: %s" % z)
            

            v_1.append(x[1])
            v_2.append(y[1])
            v_3.append(z[1])

        except Queue.Empty:
            if sdr.finished:
                print("Done reading from the Queue.")
            else:
                print("Queue is empty. Stopping...")
                sdr.finished = True
            break
        except KeyboardInterrupt:
            sdr.finished = True
        except Exception:
            e = sys.exc_info()[1]
            print("main exception: %s %s" % (type(e), e))
            sdr.finished = True
            break


    # Wait for the stream thread to stop
    sdrThread.join()

    v_x = sum(v_1)/len(v_1) if len(v_1) != 0 else -1.0
    v_y = sum(v_2)/len(v_2) if len(v_2) != 0 else -1.0
    v_z = sum(v_3)/len(v_3) if len(v_3) != 0 else -1.0

    return (v_x, v_y, v_z)