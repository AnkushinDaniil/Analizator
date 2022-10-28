import numpy as np
from pyqtgraph import colormap
from scipy.signal import find_peaks, freqs, cheby2, sosfilt, cheb2ord, freqz
from scipy.fft import fft, ifft, rfft, irfft


class Signal:
    """Signal(signal: np.ndarray, speed: float, total_time: float, lambda_source: float,
              source_bandwith: float, delta_n: float, ADC_frequency: float, phase_modulation_frequency: float,
              name: str, pen)

        Класс "сигнал" представляет собой набор полей, соответствующих параметрам сигнала,
        и функций для их вычисления"""

    def __init__(self):
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
        self.split_num = None  # Период интерференционной картины
        self.phase_modulation_frequency = None  # Частота фазовой модуляции
        self.source_bandwith = None  # Ширина полосы источника, м
        self.speed = None  # Скорость движения подвижки, м/с
        self.total_time = None  # Время движения подвижки, с
        self.visibility = None  # Видность
        self.visibility_coordinates = None  # Координаты для графика видности

    def set_signal(self, interference: np.ndarray, speed: float, total_time: float, lambda_source: float,
                   source_bandwith: float, delta_n: float, ADC_frequency: float, phase_modulation_frequency: float,
                   name: str, pen):
        n = np.size(interference)
        print()
        print(name)
        self.ADC_frequency = ADC_frequency
        print(f'Частота АЦП = {self.ADC_frequency} Гц')
        self.phase_modulation_frequency = phase_modulation_frequency
        print(f'Частота фазовой модуляции = {self.phase_modulation_frequency} Гц')
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
        self.cheb2_x, self.cheb2_y, self.denoised_interference = self.__remove_noise(self.interference, self.ADC_frequency)
        self.denoised_interference_coordinates = self.__set_0(
            self.interference_coordinates, self.denoised_interference
        )
        self.split_num = self.__get_split_num(self.total_time, self.speed)
        self.visibility_coordinates, self.visibility = self.__calculate_visibility(
            self.denoised_interference_coordinates, self.denoised_interference, self.split_num
        )
        self.visibility_coordinates = self.__set_0(
            self.visibility_coordinates, self.visibility
        )

        self.h_parameter_coordinates, self.h_parameter, self.beat_length, self.depolarization_length = \
            self.__calculate_h_param(self.visibility_coordinates, self.visibility, self.lambda_source, self.delta_n,
                                     self.source_bandwith)
        print(f'Длина биений = {self.beat_length} м')
        print(f'Длина деполяризации = {self.depolarization_length} м')
        self.visibility_after_BD_compensation = self.__BD_compensation(self.visibility)

    def read_signal(self, signal_dict: dict):
        for key in self.__dict__.keys():
            setattr(self, key, signal_dict.get(key, None))


    @staticmethod
    def __set_0(x_axes: np.ndarray, y_axes: np.ndarray):
        i = np.where(y_axes == np.max(y_axes))
        x_axes: np.ndarray = x_axes - x_axes[i[0][0]]
        return x_axes


    @staticmethod
    def __remove_noise(interference: np.ndarray, ADC_frequency: float):
        x = np.arange(interference.shape[0])
        coef = np.polyfit(x, interference, 1)
        poly1d = np.poly1d(coef)
        linear = poly1d(x)
        interference_0: np.ndarray = interference - linear
        fs = ADC_frequency  # Частота дискретизации в Гц
        wp = 2600  # Частота полосы пропускания в Гц
        ws = 6000  # Частота полосы заграждения в Гц
        gpass = 1  # Неравномерность полосы пропускания в дБ
        gstop = 100  # Затухание в полосе задерживания в дБ

        analog = False
        N, Wn = cheb2ord(wp=wp, ws=ws, gpass=gpass, gstop=gstop, analog=analog, fs=fs)
        b, a = cheby2(N=N, rs=gpass, Wn=Wn, btype='lowpass', analog=analog, fs=fs)
        w, h = freqz(b, a)
        sos = cheby2(N=N, rs=gpass, Wn=Wn, btype='lowpass', analog=analog, fs=fs, output='sos')
        denoised_interference: np.ndarray = sosfilt(sos, interference_0) + linear

        return w/np.pi*ADC_frequency/2, 10 * np.log10(abs(h)), denoised_interference

    @staticmethod
    def __get_split_num(total_time: float, speed: float):
        split_num = total_time * speed / 0.000001
        print(split_num)
        return split_num

    @staticmethod
    def __calculate_visibility(x: np.ndarray, y: np.ndarray, split_num: float):
        splited_denoised_interference: np.ndarray = np.array_split(y, split_num)
        # print(splited_denoised_interference)
        maximum = (i.max() for i in splited_denoised_interference)
        # print(maximum)
        minimum = (i.min() for i in splited_denoised_interference)
        # print(minimum)
        visibility: np.ndarray = np.fromiter(((ma - mi) / (ma + mi) for ma, mi in zip(maximum, minimum)), float)
        # print(visibility)
        visibility_coordinates: np.ndarray = np.linspace(x.min(), x.max(), num=visibility.shape[0])
        return visibility_coordinates, visibility

    @staticmethod
    def __calculate_h_param(visibility_coordinates: np.ndarray, visibility: np.ndarray, lambda_source: float,
                            delta_n: float, source_bandwith: float):
        y = np.divide(visibility, visibility.max())
        beat_length = lambda_source / delta_n
        depolarization_length = (lambda_source ** 2) / (source_bandwith * delta_n)
        h_parameter: np.ndarray = 10 * np.log10(np.square(y) / depolarization_length)
        h_parameter_coordinates: np.ndarray = visibility_coordinates / delta_n
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
