from Controllers import LabberController as LC
from Controllers import Param, Data
from EvaluationFunctions import Eval
from SupportFunction import SupportFunction as SF
import Labber

filepath = "SampleData/q5_SS_drive_onoff_19_test.hdf5"
logfile = Labber.LogFile(filepath)
Labber.LogFile(filepath).getData()

data = logfile.getData()
data_ = data[::2], data[1::2]

stepChannels = logIn.getStepChannels()
value, error = Eval(data_).result()
Data(data=value, error=error)

