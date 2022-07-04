import Labber
import numpy as np
from dataclasses import dataclass


@dataclass
class Param:
    name: str
    value: float = None
    span: float = None
    scaling: float = None
    unit: str = None
    remove: bool = False

    def __repr__(self):
        if len(str(self.value)) > 25:
            value_str = f"{str(self.value)[:25]}..."
        else:
            value_str = str(self.value)
        return f"{self.name}: {value_str} \u00B1 {self.span}"


@dataclass
class Data:
    data: float
    error: float = None
    name: str = None
    parameter_name: str = None
    parameter_values: float = None

    def __repr__(self):
        if len(str(self.data)) > 25:
            data_str = f"{str(self.data)[:25]}..."
        else:
            data_str = str(self.data)

        if len(str(self.error)) > 25:
            error_str = f"{str(self.error)[:25]}..."
        else:
            error_str = str(self.error)

        return f"name: {self.name} \ndata: {data_str} \nerror: {error_str}"


class DommyController:
    def __init__(self, file_path, method="Fidelity"):
        """Dommy function for structur of controllers"""
        pass

    def get_parameters(self):
        "Pulls parameters from controller/experiments. Returns parameters."
        pass

    def set_parameters(self, parameters):
        "Pushes/updates parameters to controller/Experiments"
        pass

    def run(self):
        "reutrn: x,y data"
        pass


class LabberController:
    def __init__(self, file_path, parameters, config, method="Fidelity"):
        self.file_path = file_path
        self.file_path_copy = file_path
        self.method = method
        self.parameters = parameters
        self.config = config

        self._set_labber_object()
        self.get_parameters(update_values=True)

    def _set_labber_object(self):
        # Initialize Labber object
        self.log_file = Labber.LogFile(self.file_path)

        # Initialize step channel object
        self.step_channels = self.log_file.getStepChannels()
        self.step_channels_names = [d["name"] for d in self.step_channels]

    def get_parameters(self, update_values=False):
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

    def set_parameters(self, new_params, meas_obj=None, single_point=False):
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

            self.get_parameters(update_values=False)

            if meas_obj:
                if single_point:
                    meas_obj.updateValue(new_param.name, new_param.value)
                else:
                    print(
                        f"Scan of {new_param.name}:\n{new_param.value} \u00B1 {new_param.span}"
                    )
                    meas_obj.updateValue(
                        new_param.name, new_param.value, itemType="CENTER"
                    )
                    meas_obj.updateValue(
                        new_param.name, new_param.span, itemType="SPAN"
                    )
                    meas_obj.updateValue(
                        new_param.name, self.config.n_inital_points, itemType="N_PTS"
                    )

    def initialize(self, input_file_path, output_file_path):
        return Labber.ScriptTools.MeasurementObject(input_file_path, output_file_path)

    def run(self, meas_obj):
        filepath = meas_obj.performMeasurement(return_data=False)
        data = Labber.LogFile(filepath).getData()
        return data[::2], data[1::2]  # v0, v1


if __name__ == "__main__":
    None
