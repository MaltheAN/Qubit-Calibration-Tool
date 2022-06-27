class Config:
    def __init__(self):
        self.set_instruments_names()
        self.set_sweep_parameters()
        self.set_save_path()
        self.set_controller()
        self.set_evaluator()
        self.set_method()

    def set_instruments_names(self, instruments_names=None):
        self.instruments_names = {
            "Tupa Name": "RS Pump",
            "Readout Name": "RS Readout",
            "Pulse Generator Name": "Pulse Generator",
        }

    def set_sweep_parameters(
        self, n_inital_points=10, n_replabs=3, n_passes=3, n_points=3, inital_scan=True
    ):
        self.n_inital_points = n_inital_points
        self.n_replabs = n_replabs
        self.n_passes = n_passes
        self.n_points = n_points

        self.inital_scan = inital_scan

    def set_save_path(self, path=None):
        import os

        self.save_path_basename = path or os.path.dirname(__file__)

    def set_controller(self, controller="Labber"):
        from Controllers import LabberController, DommyController

        if controller == "Labber":
            self.controller = LabberController

        elif controller == "Dommy":
            self.controller = DommyController

    def set_evaluator(self, evaluator="Fidelity"):
        from EvaluationFunctions import Eval, calculate_fidelity

        self.eval_method = evaluator

    def set_method(self, method="Fidelity"):
        self.method = method


if __name__ == "__main__":
    from Experiments import SingleShotCalibration

    filepath = "SampleData/q5_SS_drive_onoff_19_test.hdf5"
    ss = SingleShotCalibration(filepath)

