from SupportFunction import SupportFunction as sf
from EvaluationFunctions import Eval
from Controllers import Param, Data
from main import Config
import numpy as np


class SingleShotCalibration:
    # Atom:
    # Check_data_scan + Analyis
    # Calibatrion_data + Analyis
    # Tolorance
    # Periode of belive (0 = inf)
    # Dit with params (when (time), state = (good, bad), methods, qubit number

    # Node:
    # check_state
    # qubit number

    # Qubit number

    def __init__(self, file_path, config=None):
        self.file_path = file_path
        self.file_path_temp = file_path

        self.config = config or Config()

        self._set_inital_paramaters()
        self.set_sweep_parameters()

    def _initialize_controller(self):
        self.controller = self.config.controller(
            file_path=self.file_path,
            parameters=self.parameters,
            method=self.config.method,
            config=self.config,
        )

    def set_parameters(self, **kwargs):
        self.controller.set_parameters(**kwargs)

    def get_parameters(self, **kwargs):
        self.controller.get_parameters(**kwargs)

    def _set_inital_paramaters(self):
        self.parameters = [
            Param(f"{self.config.instruments_names['Tupa Name']} - Power", span=2),
            Param(
                f"{self.config.instruments_names['Tupa Name']} - Frequency", span=9e6
            ),
            Param(
                f"{self.config.instruments_names['Readout Name']} - Frequency", span=9e6
            ),
            Param(
                f"{self.config.instruments_names['Pulse Generator Name']} - Power",
                span=20,
            ),
            Param(
                f"{self.config.instruments_names['Pulse Generator Name']} - Demodulation - Length",
                span=1e-6,
            ),
        ]

    def set_sweep_parameters(
        self, n_inital_points=10, n_replabs=3, n_passes=3, n_points=3, inital_scan=True
    ):
        self.n_inital_points = n_inital_points
        self.n_replabs = n_replabs
        self.n_passes = n_passes
        self.n_points = n_points

        self.inital_scan = inital_scan

    def run(self):
        def _new_span(self, step_size):
            return 2 * (step_size / (self.n_points + 2)) * self.n_points

        self.data_list = []
        for _ in range(self.n_replabs):
            for param in self.parameters:

                # Make measurement object
                meas_name = sf.save_labber_file(self.file_path, parameter=param.name)
                meas_obj = self.controller.initialize(self.file_path_temp, meas_name)

                # If inital scan true
                if self.inital_scan:
                    self.controller.set_parameters(param, meas_obj)

                for _ in range(self.n_passes):
                    # Perform measurement
                    v0, v1 = self.controller.run(meas_obj)

                    # Evaluate result
                    values, errors = Eval([v0, v1], method=self.config.method).result()
                    param.value = np.max(values)  # TODO: Make this function
                    param.span = _new_span((param.value[0] - param.value[1]))

                    self.data_list.append(
                        Data(
                            data=values,
                            errors=errors,
                            name=meas_name,
                            parameter_name=param.name,
                            parameter_values=param.values,
                        )
                    )

                    self.controller.set_parameters(param, meas_obj)

                # Update value and params
                self.controller.set_parameters(param, meas_obj, single_point=True)

            # Udate filepath (bug in Labber)
            self.file_path_temp = self.controller.run(meas_obj)

    def run_output_experiment(self):
        # TODO: this function is not done!
        pass
