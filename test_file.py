from LabberController import LabberController as LC
from LabberController import Param, Data
from EvaluationFunctions import Fidelity
from SupportFunction import SupportFunction as SF
import Labber

filepath = "SampleData/q5_SS_drive_onoff_19_test.hdf5"
logfile = Labber.LogFile(filepath)
logfile.getData()

readoutVariable = "Pulse Generator - Single-shot, QB1"

for n in range(5):
    # get data for qubit 0/1
    v0 = logfile.getData(readoutVariable, n * 2)
    v1 = logfile.getData(readoutVariable, n * 2 + 1)


data = [
    [
        [1, 1, 0, 1, 0, 0, 1, 1, 2, 3, 45, 6, 7, 4, 0],
        [0, 0, 1, 2, 1, 1, 32, 5, 3, 3, 54, 7, 3],
    ]
]
Fidelity(data).result()

data
Data(data).data
Param("value", [1, 2, 4, 2, 5, 32, 5, 3, 6, 6])

