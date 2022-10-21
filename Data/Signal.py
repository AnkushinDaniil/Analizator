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
        self.beat_length = None  # Длина биений
        self.delta_n = None  # Разница показателей преломления
        self.denoised_interference = None  # Интерференция без шума
        self.denoised_interference_coordinates = None  # Координаты для графика интерференции без шума
        self.depolarization_length = None  # Длина деполяризации
        self.h_parameter = None  # h-параметр
        self.h_parameter_coordinates = None  # Координаты для графика h-параметра
        self.interference = None  # Интерференционная картина
        self.interference_coordinates = None  # Координаты для графика интерференции
        self.lambda_source = None  # Цетральная длина волны источника, м
        self.n_to_length = None  # Коэффициент перевода из единиц в длину
        self.name = None  # Название сигнала
        self.pen = None  # Цвет сигнала
        self.periodicity_of_the_interference_pattern = None  # Период интерференционной картины
        self.phase_modulation_frequency = None  # Частота фазовой модуляции
        self.source_bandwith = None  # Ширина полосы источника, м
        self.speed = None  # Скорость движения подвижки, м/с
        self.total_time = None  # Время движения подвижки, с
        self.visibility = None  # Видность
        self.visibility_coordinates = None  # Координаты для графика видности
        # Создание объекта класса "сигнал"
        self.set_signal(interference, speed, total_time, lambda_source, source_bandwith, delta_n, name, pen)

    def set_signal(self, interference: np.ndarray, speed: float, total_time: float, lambda_source: float,
                   source_bandwith: float, delta_n: float, name: str, pen):
        n = np.size(interference)
        print()
        print(name)
        self.interference = interference
        self.speed = speed / 1000
        print(f'Скорость движения подвижки = {self.speed} м/с')
        self.total_time = total_time
        print(f'Время движения подвижки = {self.total_time} с')
        self.lambda_source = lambda_source / 10 ** 9
        print(f'Цетральная длина волны источника = {self.lambda_source} м')
        self.source_bandwith = source_bandwith / 10 ** 9
        print(f'Ширина полосы источника = {self.source_bandwith} м')
        self.delta_n = delta_n
        print(f'Разница показателей преломления = {self.delta_n}')
        self.name = name
        self.pen = pen
        print(f'Цвет = {self.pen}')

        self.n_to_length = self.total_time * self.speed / n
        print(f'Коэффициент перевода из единиц в длину = {self.n_to_length}')
        self.interference_coordinates = np.arange(0, n, 1, dtype=float) * self.n_to_length
        self.interference_coordinates = self.__set_0(
            self.interference_coordinates, self.interference
        )
        self.denoised_interference_coordinates, self.denoised_interference = \
            self.__remove_noise(self.interference, self.interference_coordinates)
        self.denoised_interference_coordinates = self.__set_0(
            self.denoised_interference_coordinates, self.denoised_interference
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

        self.h_parameter_coordinates, self.h_parameter, self.beat_length, self.depolarization_length =  \
            self.__calculate_h_param(self.visibility_coordinates, self.visibility, self.lambda_source, self.delta_n,
                                     self.source_bandwith)
        print(f'Длина биений = {self.beat_length} м')
        print(f'Длина деполяризации = {self.depolarization_length} м')
        self.visibility_after_BD_compensation = self.__BD_compensation(self.visibility)




    @staticmethod
    def __set_0(x_axes: np.ndarray, y_axes: np.ndarray):
        i = np.where(y_axes == np.max(y_axes))
        x_axes = x_axes - x_axes[i[0][0]]
        return x_axes


    @staticmethod
    def __remove_noise(interference: np.ndarray, interference_coordinates: np.ndarray):
        windowSize = np.size(interference) / 100000
        window = np.hanning(windowSize)
        window = window / window.sum()

        # filter the data using convolution
        denoised_interference = np.convolve(window, interference, mode='valid')
        denoised_interference_coordinates = interference_coordinates[:denoised_interference.shape[0]]

        return denoised_interference_coordinates, denoised_interference

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

    @staticmethod
    def __calculate_h_param(visibility_coordinates: np.ndarray, visibility: np.ndarray, lambda_source: float,
                            delta_n: float, source_bandwith: float):
        y = np.divide(visibility, np.max(visibility))
        beat_length = lambda_source / delta_n
        depolarization_length = (lambda_source ** 2) / (source_bandwith * delta_n)
        h_parameter = 10 * np.log10(np.square(y) / depolarization_length)
        h_parameter_coordinates = visibility_coordinates * 0.002 / delta_n
        return h_parameter_coordinates, h_parameter, beat_length, depolarization_length

    @staticmethod
    def __BD_compensation(visibility: np.ndarray):
        pass
        # peaks, properties = find_peaks(visibility, prominence=1, width=20)
        # properties["prominences"], properties["widths"]
        # # (array([1.495, 2.3]), array([36.93773946, 39.32723577]))
        # plt.plot(x)
        # plt.plot(peaks, x[peaks], "x")
        # plt.vlines(x=peaks, ymin=x[peaks] - properties["prominences"],
        #            ymax=x[peaks], color="C1")
        # plt.hlines(y=properties["width_heights"], xmin=properties["left_ips"],
        #            xmax=properties["right_ips"], color="C1")
        # plt.show()