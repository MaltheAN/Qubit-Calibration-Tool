import Labber
import numpy as np
import matplotlib.pyplot as plt


class ThreeSixtynNoScopeAutoAim_readout_optimizer:
    def __init__(self, fPath=None, plot=False, run=False, runOutput=False):
        self.fPath = self.fPath_temp = fPath
        self.plot = plot

        self.setParams()
        self.setSpans()
        self.setScanParams()

        if run == True:
            self.run()
        
        if runOutput == True:
            self.runOutput()
        pass
   
    class FidelitySS:
        def __init__(self, fPath=None, plot=False, stepChannelName=None, readoutVariable="Pulse Generator - Single-shot, QB1", 
                    oldData=None):
            if fPath != None:
                self.loopOverEntries(fPath, readoutVariable, stepChannelName)

                if plot == True:
                    self.plotScoring(oldData)

        def calculateFidelity(self, v0, v1):
            self.scoringName = 'Fidelity'
            
            # Esitmate 0/1 mean (number)
            mean0, sigma0 = np.mean(v0), np.std(v0)
            mean1, sigma1 = np.mean(v1), np.std(v1)
        
            # Esitmate rel distance
            dist00, dist01 = np.abs(v0 - mean0), np.abs(v0 - mean1) 
            dist0, dist1 = np.abs(v1 - mean0), np.abs(v1 - mean1) 
        
            # Counts of 0/1 values
            n0 = len(np.nonzero(dist0 < dist1)[0])
            n1 = len(np.nonzero(dist0 >= dist1)[0])

            # Calulate outputs
            fidelity = 1-n0/float(n0+n1)
            error = 1 / np.sqrt(n0)
            
            return fidelity, error

        def loopOverEntries(self, fPath, readoutVariable='Pulse Generator - Single-shot, QB1', stepChannelName=None):
            self.fileName = self._get_file_name_from_path(fPath)
            
            logIn = Labber.LogFile(fPath)
            stepChannels = logIn.getStepChannels()
        
            try:
                stepChannel = stepChannels[[i for i, val in enumerate(stepChannels) if val['name'] == stepChannelName][0]]
            except:
                stepChannel = stepChannels[1]
            
            # Set values
            self.paramScaling = 1
            self.paramName = stepChannel['name']
            self.paramUnit = stepChannel['unit']
            self.paramValues = stepChannel['values']
            self.paramStepsize = self.paramValues[1] - self.paramValues[0]
            
            # Make fidelity list
            self.scoring = {i:np.zeros(len(self.paramValues)) for i in ['value', 'error']}
                
            # loop over values
            for n, val in enumerate(self.paramValues):
                # get data for qubit 0/1
                v0 = logIn.getData(readoutVariable, n*2)
                v1 = logIn.getData(readoutVariable, n*2+1)
                
                self.scoring['value'][n], self.scoring['error'][n] = self.calculateFidelity(v0, v1)

        def plotScoring(self, oldData=None):
            plt.figure()

            try:
                for oldDatai in oldData:
                    plt.errorbar(self.paramValues/self.paramScaling, oldDatai['value'], oldDatai['error'],
                    fmt='')
            except:
                pass

            plt.errorbar(self.paramValues/self.paramScaling, self.scoring['value'], self.scoring['error'],
                fmt='')
            plt.title('{}\n {} vs {}'.format(self.fileName, self.scoringName, self.paramName))
            plt.xlabel('{} [{}]'.format(self.paramName, self.paramUnit))
            plt.ylabel(self.scoringName)
            plt.show()
            
        def value(self):
            max_arg = np.argmax(self.scoring['value'])
            return self.paramValues[max_arg], self.paramStepsize, self.scoring

        def _get_file_name_from_path(path, part='tail'):
                    """Small function for getting the hit and sale of path.

                    Args:
                        path (string): Datafile path
                        part (str, optional): If head, the main part is returned. If tail, the filename is retruned. Defaults to 'tail'.

                    Returns:
                        head (string): main part of path.
                        tail (string): filename 
                    """
                    import os
                    try:
                        head, tail = os.path.split(path)
                        
                        if part == 'head':
                            return head
                        else:
                            return tail.replace('.hdf5', '')
                    except:
                        #print('No filepath fund. Please make a title manually.')
                        return ''

        def round_on_error(self, value, error):
            import math
            significant_digits = 10**math.floor(math.log(error, 10))
            return value // significant_digits * significant_digits

    def setParams(self, param=None):
        if self.fPath == None:
            print('set file path (fPath)')
            self.params = None
        else:
            Lfile = Labber.LogFile(self.fPath)
                
            self.params = {
                        'RS Readout - Frequency': [],
                        'RS Readout - Power': [],
                        'RS Pump - Power':[],
                        'Pulse Generator - Demodulation - Length': [],
                        'RS Drive 1 - Frequency': [],
                        'Pulse Generator - Amplitude #1': []             
            }

            for key in self.params.copy():
                try:
                    if key in [d['name'] for d in Lfile.getStepChannels()]:
                        self.params[key] = Lfile.getChannelValue(key)
                    else:
                        print('Removed: {} \nAdd it to Step Channels in Labber.\n'.format(key))
                        del self.params[key]
                except:
                    del self.params[key]


            for key, value in param.items():
                if value == None:
                    del self.spans[key]
                    del self.params[key]
                
                else:
                    self.params[key] = value
                    if key not in self.spans.keys():
                        self.spans[key] = []
                        print("Please set intial span for paramter {}, by calling 'self.spans[{}] = inital value'".format(key, key))
        
    def setSpans(self, span=None):
        if self.fPath == None:
            print('set file path (fPath)')
            self.spans = None
        else:
            Lfile = Labber.LogFile(self.fPath)
                
            self.spans = {
                        'RS Readout - Frequency': 9E6,
                        'RS Readout - Power': 20,
                        'RS Pump - Power':2,
                        'Pulse Generator - Demodulation - Length': 1E-6,
                        'RS Drive 1 - Frequency': 10E7,
                        'Pulse Generator - Amplitude #1': 0.5            
            }
            
            for key, value in span.items():
                if value == None:
                    del self.spans[key]
                    del self.params[key]

                else:
                    self.spans[key] = value
                    if key not in self.params.keys():
                        self.params[key] = []
                        print("Please set intial value for paramter {}, by calling 'self.param[{}] = inital value'".format(key, key))

            for key in self.spans.copy():
                if key in [d['name'] for d in Lfile.getStepChannels()] == False:
                    print('Removed: {} \nAdd it to Step Channels in Labber.\n'.format(key))
                    del self.spans[key]
         
    def setScanParams(self, numberOfInitalPoints=16, numberOfReplabs=2,
                        numberOfPasses=3, numberOfPoints=5, intialScan=True):
        # First scan params
        self.numberOfInitalPoints = numberOfInitalPoints

        # Second scan params
        self.numberOfReplabs = numberOfReplabs
        self.numberOfPasses = numberOfPasses
        self.numberOfPoints = numberOfPoints

        # Adds inital scan
        self.intialScan = intialScan

    def run(self):  
        if self.params == None:
            self.setParams()
        
        if self.spans == None:
            self.spans()

        msin=1


        # Optimize values
        for replab in range(self.numberOfReplabs):

            # Get data
            msmt_data = Labber.ScriptTools.MeasurementObject(self.fPath_temp, self.outputFileName(self.fPath, msin))

            print(f'Replab number {replab}')

            for param in self.params:
                print('\n', param)

                # First scan
                if self.intialScan == True:
                    print('inital scan: ', self.params[param], '+/-', self.spans[param])
                    msmt_data.updateValue(param, self.params[param], itemType='CENTER')
                    msmt_data.updateValue(param, self.spans[param], itemType='SPAN')
                    msmt_data.updateValue(param, self.numberOfInitalPoints, itemType='N_PTS')

                # Second scan (fin scan)
                for ii in range(self.numberOfPasses):
                    self.oldData = []
                    Lfilename = msmt_data.performMeasurement(return_data=False)

                    paramPeak, paramStepsize, oldDatai = self.FidelitySS(Lfilename, plot=self.plot, 
                                                                    stepChannelName=param, oldData=self.oldData).value()
                    self.oldData.append(oldDatai)
                    print(param, paramPeak, paramStepsize)
                
                    msmt_data.updateValue(param, paramPeak, itemType='CENTER')
                    msmt_data.updateValue(param, 2*paramStepsize, itemType='SPAN')
                    msmt_data.updateValue(param, self.numberOfPoints, itemType='N_PTS')

                # update value and params      
                msmt_data.updateValue(param, paramPeak)
                self.params[param] = paramPeak
                msin += 1
            

            # Update filepath (bug in labber)
            Lfilename = msmt_data.performMeasurement(return_data=False)
            self.fPath_temp = Lfilename
            
    def printAllDone(self, statement):
        all_done = '"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""\n                          ALL DONE!\n"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""\n'
        print(all_done)
        print(statement, '\n')
        print(all_done)
    
    def outputFileName(self, fPath, i):     
        def _get_file_name_from_path(path, part='tail'):
                """Small function for getting the hit and sale of path.

                Args:
                    path (string): Datafile path
                    part (str, optional): If head, the main part is returned. If tail, the filename is retruned. Defaults to 'tail'.

                Returns:
                    head (string): main part of path.
                    tail (string): filename 
                """
                import os
                try:
                    head, tail = os.path.split(path)
                    
                    if part == 'head':
                        return head
                    else:
                        return tail.replace('.hdf5', '')
                except:
                    #print('No filepath fund. Please make a title manually.')
                    return ''  

        fName = _get_file_name_from_path(fPath, part='tail')
        fHead = _get_file_name_from_path(fPath, part='head')

        return fHead + f'\\{fName}_gen_data\\' + fName + f'_{i}_test.hdf5'

    def runOutput(self, ampRange = [0,2], n_pts=101):      
        msmt_final = Labber.ScriptTools.MeasurementObject(self.fPath_temp, self.outputFileName(self.fPath, 'final'))
        msmt_final.updateValue('RS Drive 1 - Output', 1)

        msmt_final.updateValue('Pulse Generator - Amplitude #1', ampRange[0], itemType='START')
        msmt_final.updateValue('Pulse Generator - Amplitude #1', ampRange[1], itemType='STOP')
        msmt_final.updateValue('Pulse Generator - Amplitude #1', n_pts, itemType='N_PTS')

        msmt_final.performMeasurement(return_data=False)


fPath = "C:\\Users\\T5_2\Desktop\\Q2 Calibration\\q2_SS_temp_optimized_newdemod.hdf5"
ThreeSixtynNoScopeAutoAim_readout_optimizer(fPath, run=True, plot=True)