import quantum_fitter as qf
import numpy as np
import Labber
import matplotlib.pyplot as plt

# result_path = r"A:\Labber\20210512_Soprano_CharacterizationCooldown\2022\06\Data_0616\q2_Ramsey_freq_calibration_fine.hdf5"
# result_path = r"A:\Labber\20210512_Soprano_CharacterizationCooldown\2022\06\Data_0616\q2_Ramsey_freq_calibration_scandetuning_2.hdf5"
result_path = r"A:\Labber\20210512_Soprano_CharacterizationCooldown\2022\06\Data_0616\q2_Ramsey_freq_calibration_fine_3.hdf5"

fit_guess = {'T': 0.7, 'phi': np.pi/2}
omega, domega = qf.multi_entry(result_path, plot_i=True, mode='T2', return_freq=True, plot_mean=False, fit_guess=fit_guess)



freq_offset = np.array(omega)/(2*np.pi)*1e6
dfreq_offset = np.array(domega)
dfreq_offset[dfreq_offset==None] = 0
dfreq_offset = dfreq_offset/(2*np.pi)*1e6


out = Labber.LogFile(result_path)

frequencies = out.getStepChannels()[1]['values'][:len(omega)]

qubit_frequency_estimate_positive = frequencies + freq_offset
qubit_frequency_estimate_negative = frequencies - freq_offset

plt.figure()
plt.errorbar(frequencies*1e-9, qubit_frequency_estimate_positive*1e-9, dfreq_offset*1e-9, label='drive + oscillation')
plt.ylabel('Estimated qubit frequency [GHz]')
plt.xlabel('Drive frequency [GHz]')

plt.figure()
plt.errorbar(frequencies*1e-9, qubit_frequency_estimate_negative*1e-9, dfreq_offset*1e-9, label='drive - oscillation')
plt.ylabel('Estimated qubit frequency [GHz]')
plt.xlabel('Drive frequency [GHz]')
plt.grid()
plt.ylim(qubit_frequency_estimate_negative[-1]*np.array([1 - 0.7*1e-4, 1 + 0.7*1e-4])*1e-9)
plt.legend()
plt.show()

plt.figure()
plt.errorbar(frequencies*1e-6 - frequencies[0]*1e-6, qubit_frequency_estimate_negative*1e-9, dfreq_offset*1e-9)
plt.ylabel('Estimated qubit frequency [GHz]')
plt.xlabel(f'Detuning from {frequencies[0]*1e-9:.6} GHz [MHz]')
plt.grid()
plt.ylim(frequencies[0]*np.array([1 - 0.7*1e-4, 1 + 0.7*1e-4])*1e-9)
plt.legend()
plt.show()





plt.figure()
plt.errorbar(frequencies[:5]*1e-9, qubit_frequency_estimate_positive[:5]*1e-9, dfreq_offset[:5]*1e-9)
plt.ylabel('Estimated qubit frequency [GHz]')
plt.xlabel('Drive frequency [GHz]')

plt.errorbar(frequencies[6:]*1e-9, qubit_frequency_estimate_negative[6:]*1e-9, dfreq_offset[6:]*1e-9)
plt.ylabel('Estimated qubit frequency [GHz]')
plt.xlabel('Drive frequency [GHz]')
plt.grid()
plt.show()

