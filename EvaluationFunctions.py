import numpy as np

def calculate_fidelity(v0, v1):
    """Function to calculate fidelity. Returns the fidelity with a given error, given v0 and v1.

    Args:
        v0 (array): Voltage of the ground state data points.
        v1 (array): Voltage of the first existed state data points.

    Returns:
        Fidelity (array): Fidelitys of inputs
        Error (array): Errors of fidelity of inputs
    """

    # Esitmate 0/1 mean (number)
    mean0, sigma0 = np.mean(v0), np.std(v0) / np.sqrt(len(v0))
    mean1, sigma1 = np.mean(v1), np.std(v1) / np.sqrt(len(v1))

    # Esitmate rel distance
    dist0, dist1 = np.abs(v1 - mean0), np.abs(v1 - mean1)

    # Counts of 0/1 values
    n0 = len(np.nonzero(dist0 < dist1)[0])
    n1 = len(np.nonzero(dist0 >= dist1)[0])

    # Calulate outputs
    fidelity = 1 - n0 / float(n0 + n1)

    w = (dist1 / sigma1) / (dist0 / sigma0)
    error = np.std(w) / np.sqrt(n0)

    return fidelity, error


class Eval:
    def __init__(self, data, method="Fidelity", other=None):
        self.data = data

        if method == "Fidelity":
            self.eval = calculate_fidelity

        if other:
            other.scoring_type = method

    def result(self):
        v0, v1 = self.data
        result = np.array([self.eval(v0_i, v1_i) for v0_i, v1_i in zip(v0, v1)]).T
        values, errors = result[0, :], result[1, :]

        return values, errors


if __name__ == "__main__":
    None
