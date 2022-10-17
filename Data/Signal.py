import numpy as np
from pyqtgraph import colormap
from scipy.signal import find_peaks


class Signal:
    """Signal(signal: np.ndarray, speed: float, total_time: float, lambda_source: float,
              source_bandwith: float, delta_n: float, ADC_frequency: float, phase_modulation_frequency: float,
              name: str, pen)

        Класс "сигнал" представляет собой набор полей, соответствующих параметрам сигнала,
        и функций для их вычисления"""

    def __init__(self, interference: np.ndarray, speed: float, total_time: float, lambda_source: float,
                 source_bandwith: float, delta_n: float, ADC_frequency: float, phase_modulation_frequency: float,
                 name: str, pen):
        self.ADC_frequency = None  # Частота АЦП
        self.phase_modulation_frequency = None  # Частота фазовой модуляции
        self.depolarization_length = None  # Длина деполяризации
        self.beat_length = None  # Длина биений
        self.h_parameter = None  # h-параметр
        self.h_parameter_coordinates = None  # Координаты для графика h-параметра
        self.visibility_coordinates = None  # Координаты для графика видности
        self.visibility = None  # Видность
        self.periodicity_of_the_interference_pattern = None  # Период интерференционной картины
        self.denoised_interference_coordinates = None  # Координаты для графика интерференции без шума
        self.denoised_interference = None  # Интерференция без шума
        self.interference_coordinates = None  # Координаты для графика интерференции
        self.n_to_length = None  # Коэффициент перевода из единиц в длину
        self.pen = None  # Цвет сигнала
        self.name = None  # Название сигнала
        self.delta_n = None  # Разница показателей преломления
        self.source_bandwith = None  # Ширина полосы источника, м
        self.lambda_source = None  # Цетральная длина волны источника, м
        self.total_time = None  # Время движения подвижки, с
        self.speed = None  # Скорость движения подвижки, м/с
        self.interference = None  # Интерференционная картина
        # Создание объекта класса "сигнал"
        self.set_signal(interference, speed, total_time, lambda_source, source_bandwith, delta_n, name, pen)

    def set_signal(self, interference: np.ndarray, speed: float, total_time: float, lambda_source: float,
                   source_bandwith: float, delta_n: float, name: str, pen):
        n = np.size(interference)

        self.interference = interference
        self.speed = speed / 1000
        self.total_time = total_time
        self.lambda_source = lambda_source / 10 ** 9
        self.source_bandwith = source_bandwith / 10 ** 9
        self.delta_n = delta_n
        self.name = name
        self.pen = pen

        self.n_to_length = self.total_time * self.speed / n
        self.interference_coordinates = np.arange(0, n, 1, dtype=float) * self.n_to_length
        self.interference_coordinates = self.__set_0(
            self.interference_coordinates, self.interference
        )
        self.denoised_interference = self.__remove_noise(self.interference)
        self.denoised_interference_coordinates = self.__set_0(
            self.interference_coordinates, self.denoised_interference
        )
        self.periodicity_of_the_interference_pattern = \
            self.__calculate_interference_pattern_periodicity(self.denoised_interference)
        self.visibility_coordinates, self.visibility = self.__calculate_visibility(
            self.denoised_interference_coordinates, self.denoised_interference,
            self.periodicity_of_the_interference_pattern
        )
        self.visibility_coordinates = self.__set_0(
            self.visibility_coordinates, self.visibility
        )

        self.h_parameter_coordinates, self.h_parameter, self.beat_length, self.depolarization_length=  \
            self.__calculate_h_param(self.visibility_coordinates, self.visibility, self.lambda_source, self.delta_n,
                                     self.source_bandwith)



    @staticmethod
    def __set_0(x_axes: np.ndarray, y_axes: np.ndarray):
        i = np.where(y_axes == np.max(y_axes))
        x_axes = x_axes - x_axes[i[0][0]]
        return x_axes


    @staticmethod
    def __remove_noise(interference: np.ndarray):
        windowSize = np.size(interference) / 100000
        window = np.hanning(windowSize)
        window = window / window.sum()

        # filter the data using convolution
        denoised_interference = np.convolve(window, interference, mode='valid')

        return denoised_interference

    @staticmethod
    def __calculate_interference_pattern_periodicity(denoised_interference: np.ndarray):
        top_values = denoised_interference[denoised_interference > np.quantile(denoised_interference, 0.9999)]
        peaks, _ = find_peaks(top_values)
        return int(top_values.shape[0] / peaks.shape[0] * 10)

    @staticmethod
    def __calculate_visibility(x: np.ndarray, y: np.ndarray, span: float):
        splited_denoised_interference = np.array_split(y, y.shape[0] // span)
        maximum = (np.max(i) for i in splited_denoised_interference)
        minimum = (np.min(i) for i in splited_denoised_interference)
        visibility = np.fromiter(((ma - mi) / (ma + mi) for ma, mi in zip(maximum, minimum)), float)
        visibility_coordinates = np.linspace(np.min(x), np.max(x), num=visibility.shape[0])
        return visibility_coordinates, visibility

    def __calculate_h_param(self, visibility_coordinates: np.ndarray, visibility: np.ndarray, lambda_source: float,
                            delta_n: float, source_bandwith: float):
        y = np.divide(visibility, np.max(visibility))
        beat_length = lambda_source / delta_n
        depolarization_length = (lambda_source ** 2) / (source_bandwith * delta_n)
        h_parameter = 10 * np.log10(np.square(y) / depolarization_length)
        h_parameter_coordinates = visibility_coordinates * 0.002 / delta_n
        return h_parameter_coordinates, h_parameter, beat_length, depolarization_length
