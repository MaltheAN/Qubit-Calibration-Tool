class LabberController:
    def __init__(self, file_path, method="Fidelity"):
        self.file_path = file_path
        self.file_path_copy = file_path
        self.method = method

        self._set_labber_object()
        self._set_inital_paramaters()
        self._check_paramaterrs(update_values=True)
        self.set_sweep_parameters()

    def _set_labber_object(self):
        # Initialize Labber object
        self.log_file = Labber.LogFile(self.file_path)

        # Initialize step channel object
        self.step_channels = self.log_file.getStepChannels()
        self.step_channels_names = [d["name"] for d in self.step_channels]

    def _set_inital_paramaters(self):
        self.parameters = [
            Param(f"{TupaName} - Power", span=2),
            Param(f"{TupaName} - Frequency", span=9e6),
            Param(f"{ReadoutName} - Frequency", span=9e6),
            Param(f"{ReadoutName} - Power", span=20),
            Param(f"{PulseGeneratorName} - Demodulation - Length", span=1e-6),
        ]

    def _check_paramaterrs(self, update_values=False):
        for i, param in enumerate(self.parameters):
            if param.name in self.step_channels_names:
                index = self.step_channels_names.index(param.name)

                # Update parameters
                if update_values:
                    param.value = self.step_channels[index]["values"]
                    param.unit = self.step_channels[index]["unit"]

            else:
                print(
                    f"Parameter '{param.name}' is not in StepChannels. \nThe parameter is removed.\n\n"
                )
                self.parameters.pop(i)

    def set_parameters(self, new_params):
        if self.parameters == False:
            self._set_inital_paramaters()

        for new_param in new_params:
            if new_param.name in [p.name for p in self.parameters]:
                index = [p.name for p in self.parameters].index(new_param.name)

                if new_param.value:
                    self.parameters[index].value = new_param.value

                if new_param.span:
                    self.parameters[index].span = new_param.span

            else:
                self.parameters.append(new_param)

            if new_param.remove:
                print(f"Parameter '{new_param.name}' has been removed.\n\n")
                self.parameters.pop(index)

            self._check_paramaterrs(update_values=False)

    def set_sweep_parameters(
        self, n_inital_points=10, n_replabs=3, n_passes=3, n_points=3, inital_scan=True
    ):
        self.n_inital_points = n_inital_points
        self.n_replabs = n_replabs
        self.n_passes = n_passes
        self.n_points = n_points

        self.inital_scan = inital_scan

    def run(self):
        # TODO: This function is not done!
        def _make_labber_object(self, param, name):
            return Labber.ScriptTools.MeasurementObject(self.file_path_copy, name)

        def _inital_run(self, meas_obj):
            if self.inital_scan:
                print(
                    f"Inital scan of {param.name}:\n{param.value} \u00B1 {param.span}"
                )
                meas_obj.updateValue(param.name, param.value, itemType="CENTER")
                meas_obj.updateValue(param.name, param.span, itemType="SPAN")
                meas_obj.updateValue(param.name, self.n_inital_points, itemType="N_PTS")

        def _get_data_from_file(self, filepath):
            data = Labber.LogFile(filepath).getData()
            return data[::2], data[1::2]

        data_list = []
        for _ in range(self.n_replabs):
            for param in self.parameters:

                # Cunstruct measurement object
                meas_name = SF.save_labber_file(self.file_path, parameter=param.name)
                meas_obj = _make_labber_object(self, param, meas_name)

                # First scan (if True)
                _inital_run(self, meas_obj)

                for _ in range(self.n_passes):
                    # Perform Measurement
                    filepath = meas_obj.performMeasurement(return_data=False)
                    v0, v1 = _get_data_from_file(filepath)

                    # Evaluate Result
                    values, errors = Eval(
                        [v0, v1], method=self.method, other=self
                    ).result()
                    Data(
                        data=values,
                        errors=errors,
                        name=meas_name,
                        parameter_name=param.name,
                        parameter_values=param.values,
                    )

                    # Old function:
                    """
                    for key in self.scorings:
                        self.scorings[key].append(scorings_i[key])

                    print(param, paramPeak, paramStepsize)
                    span = (
                        2
                        * (paramStepsize / (self.numberOfPoints + 2))
                        * self.numberOfPoints
                    )

                    msmt_data.updateValue(param, span, itemType="SPAN")
                    msmt_data.updateValue(param, paramPeak, itemType="CENTER")
                    msmt_data.updateValue(param, self.numberOfPoints, itemType="N_PTS")
                    """

    def run_output_experiment(self):
        # TODO: this function is not done!

        # Old function:
        """ def runOutput(self, ampRange=None, n_pts=101):
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

        msmt_final.performMeasurement(return_data=False)"""
        pass
