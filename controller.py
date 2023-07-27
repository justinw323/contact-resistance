import sys
import threading
import time
import traceback

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
SCAN_FREQUENCY = 5000


def init_controller():
    d = None

    # At high frequencies ( >5 kHz), the number of samples will be MAX_REQUESTS
    # times 48 (packets per request) times 25 (samples per packet)
    d = u6.U6()

    # For applying the proper calibration to readings.
    d.getCalibrationData()

    # print("Configuring U6 stream")
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
    tdac.update(3.0)

def unclamp(tdac):
    # print('clamping')
    tdac.update(0.0)

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

def print_read(d):
    print(d.getAIN(0), d.getAIN(1), d.getAIN(2))

# Reads from AIN0, AIN1, AIN2 and returns as tuple
def read(d):
    return(d.getAIN(0), d.getAIN(1), d.getAIN(2))

def per_sec(app, d, t, start_time, times, sp_list,
            gdl_tpr, gdl_tpr_list, tprs, crs, area
            ):
    tpr_stream = []
    cr_stream = []
    sp_stream = []
    i = 0
    step_start = time.time()
    step_end = step_start + t
    
    try:
        # print("Start stream")
        d.streamStart()
        # start = datetime.now()
        # print("Start time is %s" % start)

        missed = 0
        dataCount = 0
        packetCount = 0

        for r in d.streamData():
            if r is not None:
                # Our stop condition
                if time.time() > step_end:
                    break

                v1 = sum(r["AIN0"])/len(r["AIN0"])
                v2 = sum(r["AIN1"])/len(r["AIN1"])
                v3 = sum(r["AIN2"])/len(r["AIN2"])
                # print(1000*(v1-0.4), 1000*(v2-0.4), 1000*(v3-0.4))
                # Comment out these prints and do something with r
                # print("Average of %s AIN0, %s AIN1 readings: %s, %s" %
                #     (len(r["AIN0"]), len(r["AIN1"]), sum(r["AIN0"])/len(r["AIN0"]), sum(r["AIN1"])/len(r["AIN1"])))

                times.append(time.time()-start_time)
                sp_list.append(v3*5.0*area)
                sp_stream.append(v3*5.0*area)
                tprs.append((v1-0.4)*1000 - gdl_tpr)    # All tprs
                tpr_stream.append((v1-0.4)*1000 - gdl_tpr)  # Tprs from this step
                crs.append((v2-0.4)*1000 - 0.5*gdl_tpr) # All crs
                cr_stream.append((v2-0.4)*1000 - 0.5*gdl_tpr)  # Crs from this step
                gdl_tpr_list.append(gdl_tpr)   
                app.update()

                dataCount += 1
                packetCount += r['numPackets']
            else:
                # Got no data back from our read.
                # This only happens if your stream isn't faster than the USB read
                # timeout, ~1 sec.
                # print("No data ; %s" % datetime.now())
                continue
    except:
        # print("".join(i for i in traceback.format_exc()))
        pass
    finally:
        # print('Stream stopped')
        d.streamStop()
    return tpr_stream, cr_stream, sp_stream