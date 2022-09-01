import numpy as np

class Signal:

    def __init__(self, signal, speed, total_time, lambda_source, source_bandwith, delta_n, name=''):
        self.set_signal(signal, speed, total_time, lambda_source, source_bandwith, delta_n, name)

    def set_signal(self, signal, speed, total_time, lambda_source, source_bandwith, delta_n, name):
        if self.__check_signal(signal, speed, total_time, lambda_source, source_bandwith, delta_n, name):
            n = np.size(signal)
            speed = speed / 1000
            self.n_to_length = total_time * speed / n
            coordinates = np.arange(0, n, 1, dtype=float) * self.n_to_length
            self.__interference = (coordinates, signal, name)
            self.__interference = self.__set_0(self.__interference)

    @staticmethod
    def __check_signal(signal, speed, total_time, lambda_source, source_bandwidth, delta_n, name):
        return all((isinstance(signal, np.ndarray), isinstance(speed, float),
                    isinstance(total_time, float), isinstance(lambda_source, float),
                    isinstance(source_bandwidth, float), isinstance(delta_n, float),
                    isinstance(name, str)))

    @staticmethod
    def __set_0(signal):
        from scipy.signal import find_peaks

        x, y, name = signal
        peaks, _ = find_peaks(y)
        i = np.where(y == np.sort(y[peaks])[~0])

        x = x - x[i]

        return x, y, name

    def get_interference(self):
        return self.__interference

    def get_visibility(self):
        self.__denoised_signal = self.__remove_noise(self.__interference)
        self.__periodicity_of_the_interference_pattern = \
            self.__calculate_interference_pattern_periodicity(self.__denoised_signal[1])
        self.__visibility = self.__calculate_visibility(self.__denoised_signal,
                                                        self.__periodicity_of_the_interference_pattern)
        self.__visibility = self.__set_0(self.__visibility)
        return self.__visibility

    @staticmethod
    def __remove_noise(signal):
        from scipy.signal import find_peaks
        x, y, name = signal
        span = int(x.shape[0] / len(find_peaks(y)[0]))
        denoised_signal = np.convolve(y, np.ones(span * 2 + 1) / (span * 2 + 1), mode="same")[span:~span]
        new_coordinates = x[span:~span]
        return new_coordinates, denoised_signal, name

    @staticmethod
    def __calculate_interference_pattern_periodicity(denoised_signal):
        from scipy.signal import find_peaks
        top_values = denoised_signal[denoised_signal > np.quantile(denoised_signal, 0.9999)]
        peaks, _ = find_peaks(top_values)
        return int(top_values.shape[0] / peaks.shape[0] * 10)

    def __calculate_visibility(self, denoised_signal, span):
        x, y, name = denoised_signal
        splited_denoised_signal = np.array_split(y, y.shape[0] // span)
        maximum = (np.max(i) for i in splited_denoised_signal)
        minimum = (np.min(i) for i in splited_denoised_signal)
        visibility = np.fromiter(((ma - mi) / (ma + mi) for ma, mi in zip(maximum, minimum)), float)
        visibility_coordinate = np.linspace(np.min(x), np.max(x),
                                            num=visibility.shape[0])
        return visibility_coordinate, visibility, name