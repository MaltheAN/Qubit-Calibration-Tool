import Labber
import contextlib
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

    class FidelitySS:
        def __init__(
            self,
            fPath=None,
            plot=False,
            stepChannelName=None,
            readoutVariable="Pulse Generator - Single-shot, QB1",
            oldData=None,
        ):

            if oldData:
                self.oldData = oldData
            else:
                self.oldData = {"value":[], "scoring":[]}
            if fPath != None:
                self.loopOverEntries(fPath, readoutVariable, stepChannelName)

                if plot == True:
                    self.plotScoring()

        def calculateFidelity(self, v0, v1):
            self.scoringName = "Fidelity"

            # Esitmate 0/1 mean (number)
            mean0, sigma0 = np.mean(v0), np.std(v0) / np.sqrt(len(v0))
            mean1, sigma1 = np.mean(v1), np.std(v1) / np.sqrt(len(v1))

            # Esitmate rel distance
            #dist00, dist01 = np.abs(v0 - mean0), np.abs(v0 - mean1)
            dist0, dist1 = np.abs(v1 - mean0), np.abs(v1 - mean1)

            # Counts of 0/1 values
            n0 = len(np.nonzero(dist0 < dist1)[0])
            n1 = len(np.nonzero(dist0 >= dist1)[0])

            # Calulate outputs
            fidelity = 1 - n0 / float(n0 + n1)
         
            w = (dist1 / sigma1) / (dist0 / sigma0)
            error = np.std(w) / np.sqrt(n0)

            return fidelity, error 

        def loopOverEntries(
            self,
            fPath,
            readoutVariable="Pulse Generator - Single-shot, QB1",
            stepChannelName=None,
        ):
            self.fileName = self._get_file_name_from_path(fPath)

            logIn = Labber.LogFile(fPath)
            stepChannels = logIn.getStepChannels()

            try:
                stepChannel = stepChannels[
                    [
                        i
                        for i, val in enumerate(stepChannels)
                        if val["name"] == stepChannelName
                    ][0]
                ]
            except Exception:
                stepChannel = stepChannels[1]

            # Set values
            self.paramScaling = 1
            self.paramName = stepChannel["name"]
            self.paramUnit = stepChannel["unit"]
            self.paramValues = stepChannel["values"]
            self.paramStepsize = self.paramValues[1] - self.paramValues[0]

            # Make fidelity list
            self.scoring = {
                i: np.zeros(len(self.paramValues)) for i in ["value", "error"]
            }

            self.scoring["paramValue"] = self.paramValues

            # loop over values
            for n, val in enumerate(self.paramValues):
                # get data for qubit 0/1
                v0 = logIn.getData(readoutVariable, n * 2)
                v1 = logIn.getData(readoutVariable, n * 2 + 1)

                (
                    self.scoring["value"][n],
                    self.scoring["error"][n],
                ) = self.calculateFidelity(v0, v1)

        def plotScoring(self):
            plt.figure()

            for i, value in enumerate(self.oldData["value"]):
                plt.errorbar(
                    self.oldData["paramValue"][i] / self.paramScaling,
                    value,
                    self.oldData["error"][i],
                    fmt="",
                )
            plt.errorbar(
                self.paramValues / self.paramScaling,
                self.scoring["value"],
                self.scoring["error"],
                fmt="",
            )

            from scipy.signal import savgol_filter
            fittedArray = savgol_filter(self.scoring["value"], 5, 3)
            plt.plot(self.paramValues / self.paramScaling, fittedArray)



            plt.title(
                "{}\n {} vs {}".format(self.fileName, self.scoringName, self.paramName)
            )
            plt.xlabel(f"{self.paramName} [{self.paramUnit}]")
            plt.ylabel(self.scoringName)
            plt.show()

        def value(self):
            max_arg = np.argmax(self.scoring["value"])
            return self.paramValues[max_arg], self.paramStepsize, self.scoring

        def _get_file_name_from_path(self, part="tail"):
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
                head, tail = os.path.split(self)

                return head if part == "head" else tail.replace(".hdf5", "")
            except Exception:
                # print('No filepath fund. Please make a title manually.')
                return ""

        def round_on_error(self, value, error):
            import math

            significant_digits = 10 ** math.floor(math.log(error, 10))
            return value // significant_digits * significant_digits

    def setParams(self, param=None):
        if self.fPath is None:
            print("set file path (fPath)")
            self.params = None
        else:
            self.Lfile = Labber.LogFile(self.fPath)

            self.params = {
                "RS Pump - Power": [],
                "RS Pump - Frequency": [],
                "RS Readout - Frequency": [],
                "RS Readout - Power": [],
                "Pulse Generator - Demodulation - Length": [],

            }

            self._updateDirLabber()

            if param:
                for key, value in param.items():
                    if value is None:
                        del self.spans[key]
                        del self.params[key]

                    else:
                        self.params[key] = value
                        if key not in self.spans.keys():
                            self.spans[key] = []
                            print(
                                f"Please set intial span for paramter {key}, by calling 'self.spans[{key}] = inital value'"
                            )

            self._checkDirLabber()

    def setSpans(self, span=None):
        if self.fPath is None:
            print("set file path (fPath)")
            self.spans = None
        else:
            self.Lfile = Labber.LogFile(self.fPath)

            self.spans = {
                "RS Readout - Frequency": 9e6,
                "RS Readout - Power": 20,
                "RS Pump - Power": 2,
                "Pulse Generator - Demodulation - Length": 1e-6,
                "RS Drive 1 - Frequency": 10e7,
                "Pulse Generator - Amplitude #1": 0.5,
            }

            self._checkDirLabber()

            if span:
                for key, value in span.items():
                    if value is None:
                        del self.spans[key]
                        del self.params[key]

                    else:
                        self.spans[key] = value
                        if key not in self.params.keys():
                            self.params[key] = []
                            print(
                                f"Please set intial value for paramter {key}, by calling 'self.param[{key}] = inital value'"
                            )

            self._checkDirLabber()

    def _checkDirLabber(self):
        for key in self.params.copy() or self.spans.copy():
            if key in [d["name"] for d in self.Lfile.getStepChannels()] == False:
                print("Removed: {} \nAdd it to Step Channels in Labber.\n".format(key))
                del self.params[key]
                del self.spans[key]

    def _updateDirLabber(self):
        for key in self.params.copy():
            try:
                if key in [d["name"] for d in self.Lfile.getStepChannels()]:
                    self.params[key] = self.Lfile.getChannelValue(key)
                else:
                    print(
                        "Removed: {} \nAdd it to Step Channels in Labber.\n".format(key)
                    )
                    del self.params[key]
            except Exception:
                print(
                        "Removed: {} \nAdd it to Step Channels in Labber.\n".format(key)
                    )
                del self.params[key]

    def setScanParams(
        self,
        numberOfInitalPoints=16,
        numberOfReplabs=2,
        numberOfPasses=3,
        numberOfPoints=5,
        intialScan=True,
    ):
        # First scan params
        self.numberOfInitalPoints = numberOfInitalPoints

        # Second scan params
        self.numberOfReplabs = numberOfReplabs
        self.numberOfPasses = numberOfPasses
        self.numberOfPoints = numberOfPoints

        # Adds inital scan
        self.intialScan = intialScan

    def run(self):
        if self.params is None:
            self.setParams()

        if self.spans is None:
            self.spans()

        msin = 1

        # Optimize values
        for replab in range(self.numberOfReplabs):

            # Get data
            msmt_data = Labber.ScriptTools.MeasurementObject(
                self.fPath_temp, self.outputFileName(self.fPath, msin)
            )

            print(f"Replab number {replab}")

            for param in self.params:
                print("\n", param)

                # First scan
                if self.intialScan == True:
                    print("inital scan: ", self.params[param], "+/-", self.spans[param])
                    msmt_data.updateValue(param, self.params[param], itemType="CENTER")
                    msmt_data.updateValue(param, self.spans[param], itemType="SPAN")
                    msmt_data.updateValue(
                        param, self.numberOfInitalPoints, itemType="N_PTS"
                    )

                # Second scan (fin scan)
                self.scorings = {"value":[], "error":[], "paramValue":[]}

                for _ in range(self.numberOfPasses):
                    Lfilename = msmt_data.performMeasurement(return_data=False)

                    paramPeak, paramStepsize, scorings_i = self.FidelitySS(
                        Lfilename,
                        plot=self.plot,
                        stepChannelName=param,
                        oldData=self.scorings,
                    ).value()
                    
                    for key in self.scorings:
                        self.scorings[key].append(scorings_i[key])

                    print(param, paramPeak, paramStepsize)
                    span = 2 * (paramStepsize / (self.numberOfPoints + 2)) * self.numberOfPoints

                    msmt_data.updateValue(param, span, itemType="SPAN")
                    msmt_data.updateValue(param, paramPeak, itemType="CENTER")
                    msmt_data.updateValue(param, self.numberOfPoints, itemType="N_PTS")

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
        print(statement, "\n")
        print(all_done)

    def outputFileName(self, fPath, i):
        def _get_file_name_from_path(path, part="tail"):
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

                return head if part == "head" else tail.replace(".hdf5", "")
            except Exception:
                # print('No filepath fund. Please make a title manually.')
                return ""

        fName = _get_file_name_from_path(fPath, part="tail")
        fHead = _get_file_name_from_path(fPath, part="head")

        return fHead + f"\\{fName}_gen_data\\" + fName + f"_{i}_test.hdf5"

    def runOutput(self, ampRange=None, n_pts=101):
        if ampRange is None:
            ampRange = [0, 2]
        msmt_final = Labber.ScriptTools.MeasurementObject(
            self.fPath_temp, self.outputFileName(self.fPath, "final")
        )
        msmt_final.updateValue("RS Drive 1 - Output", 1)

        msmt_final.updateValue(
            "Pulse Generator - Amplitude #1", ampRange[0], itemType="START"
        )
        msmt_final.updateValue(
            "Pulse Generator - Amplitude #1", ampRange[1], itemType="STOP"
        )
        msmt_final.updateValue(
            "Pulse Generator - Amplitude #1", n_pts, itemType="N_PTS"
        )

        msmt_final.performMeasurement(return_data=False)

"""
fPath = "C:\\Users\\T5_2\Desktop\\Q2 Calibration\\q2_SS_temp_optimized_newdemod.hdf5"
fPath = "C:\\Users\\T5_2\\Desktop\\Qubit calibration data\\Q5\\q5_SS_drive_onoff.hdf5"

Three = ThreeSixtynNoScopeAutoAim_readout_optimizer(fPath, run=False, plot=True)
Three.setScanParams(numberOfInitalPoints=10, numberOfPoints=8, numberOfReplabs=10)
Three.setSpans({"RS Readout - Power": 10})

Three.run()
Three.runOutput()
"""

Olddata = r"C:\Users\T5_2\Desktop\Qubit calibration data\Q5\q5_SS_drive_onoff_gen_data\q5_SS_drive_onoff_19_test.hdf5"

Three = ThreeSixtynNoScopeAutoAim_readout_optimizer()
Three.FidelitySS(Olddata, plot=True)