from controller import *

def reg_read(self, rapid):
    controller, aout = init_controller()
                    
    times = [1.0 for x in range(len(self.voltages))] if rapid else times

    counter = 1
    self.samplePressure = []
    self.sp = []
    self.tpr = []
    self.cr = []

    start_time = time.time()

    for i in range(len(self.voltages)):
        v = self.voltages[i]
        t = times[i]
        if(not self.running):
            return
        print(('Step %s' % counter))
        setVoltage(self, self.controller, self.aout, v)
        per_sec(self, self.controller, t, start_time, graph_times, 
                graph_pressure,
                self.gdl_tpr[i], graph_gdltpr, graph_tpr, graph_cr)

        reading = read(self.controller)
        v1 = reading[0]
        v2 = reading[1]
        v3 = reading[2]
        # Reading from AIN0, AIN1, AIN2
        # print(time.time())

        sp = v3
        tpr = v1-self.gdl_tpr[counter-1]
        cr = v2-(0.5*self.gdl_tpr[counter-1])
        self.sp.append(sp)
        self.tpr.append(tpr)
        self.cr.append(cr)
        counter += 1

        clamp(self.aout)
        # self.frames[Start_Page].save_to_file()