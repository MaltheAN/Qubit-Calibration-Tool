import Labber
import numpy as np
import quantum_fitter as qf
import matplotlib.pyplot as plt


def outputFileName(fPath, i):     
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

offset_list = np.linspace(-100, 100, 201)*1e6
qubit_frequency = np.zeros(len(offset_list))
dfreq = np.zeros(len(offset_list))
for i, offset in enumerate(offset_list):
    fPath = "A:\\Labber\\20210512_Soprano_CharacterizationCooldown\\2022\\06\\Data_0615\\q2_Ramsey_freq_calibration.hdf5"

    logIn = Labber.LogFile(fPath)
    qubit_frequency_estimate = logIn.getChannelValue('RS Drive 1 - Frequency')

    measurement = Labber.ScriptTools.MeasurementObject(fPath, outputFileName(fPath, i))
    measurement.updateValue('RS Drive 1 - Frequency', qubit_frequency_estimate + offset)

    result_path = measurement.performMeasurement(return_data=False)

    result = Labber.LogFile(result_path)

    signal = result.getEntry()['Pulse Generator - Voltage, QB1']
    signal = abs(signal)
    time = result.getEntry()['Pulse Generator - Sequence duration']

    qf_fit = qf.multi_entry(result_path, plot_i=True, mode='T2', return_object=True)

    freq = 1e6*qf_fit.fit_params('omega')
    dfreq[i] = 1e6*qf_fit.err_params('omega')

    qubit_frequency[i] = qubit_frequency_estimate + offset - np.sign(offset)*freq

    print(f"Frequency is {qubit_frequency[i]*1e-9} GHz, error is {dfreq[i]*1e-6} MHz")

plt.figure()
plt.errorbar(offset_list*1e-6, qubit_frequency*1e-9, dfreq*1e-9)
plt.xlabel('Frequency offset [MHz]')
plt.ylabel('Estimated qubit frequency [GHz]')
plt.show()


result_path = r"A:\Labber\20210512_Soprano_CharacterizationCooldown\2022\06\Data_0616\q2_Ramsey_freq_calibration_scandetuning.hdf5"
omega, domega = qf.multi_entry(result_path, plot_i=True, mode='T2', return_freq=True, plot_mean=False)

out = Labber.LogFile(result_path)

omega = np.array(omega)/(2*np.pi)*1e6
domega = np.array(domega)/(2*np.pi)*1e6

frequencies = out.getStepChannels()[1]['values'][:len(omega)]

qubit_frequency_estimate = frequencies + omega

plt.errorbar(frequencies*1e-9, qubit_frequency_estimate*1e-9, domega*1e-9)
