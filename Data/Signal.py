import numpy as np
from scipy.fft import rfft, irfft
from scipy.signal import correlate, choose_conv_method, medfilt


class Signal:
    """Signal(signal: np.ndarray, speed: float, total_time: float, lambda_source: float,
              source_bandwith: float, delta_n: float, ADC_fr: float, pm_fr: float,
              name: str, pen)

        Класс "сигнал" представляет собой набор полей, соответствующих параметрам сигнала,
        и функций для их вычисления"""

    def __init__(self):
        self.per = None
        self.per_x = None
        self.visibility_clear_x = None
        self.visibility_after_BD_compensation = None
        self.visibility_clear = None
        self.filter_v_y = None
        self.filter_v_x = None
        self.filter_i_y = None
        self.filter_i_x = None
        self.ADC_fr = None  # Частота АЦП
        self.beat_length = None  # Длина биений
        self.delta_n = None  # Разница показателей преломления
        self.interference_clear = None  # Интерференция без шума
        self.interference_clear_x = None  # Координаты для графика интерференции без шума
        self.depol_len = None  # Длина деполяризации
        self.h_par = None  # h-параметр
        self.h_par_x = None  # Координаты для графика h-параметра
        self.interference = None  # Интерференционная картина
        self.interference_x = None  # Координаты для графика интерференции
        self.lambda_source = None  # Цетральная длина волны источника, м
        self.n_to_length = None  # Коэффициент перевода из единиц в длину
        self.name = None  # Название сигнала
        self.pen = None  # Цвет сигнала
        self.split_num = None  # Период интерференционной картины
        self.pm_fr = None  # Частота фазовой модуляции
        self.source_bandwith = None  # Ширина полосы источника, м
        self.speed = None  # Скорость движения подвижки, м/с
        self.total_time = None  # Время движения подвижки, с
        self.visibility = None  # Видность
        self.visibility_x = None  # Координаты для графика видности

    def set_signal(self, interference: np.ndarray, speed: float, total_time: float, lambda_source: float,
                   source_bandwith: float, delta_n: float, adc_fr: float, pm_fr: float,
                   name: str, pen):
        n = np.size(interference)
        print()
        print(name)
        self.ADC_fr = adc_fr
        print(f'Частота АЦП = {self.ADC_fr} Гц')
        self.pm_fr = pm_fr
        print(f'Частота фазовой модуляции = {self.pm_fr} Гц')
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
        self.interference_x = np.arange(0, n, 1, dtype=float) * self.n_to_length
        self.interference_x = self.__set_0(x_axes=self.interference_x, y_axes=self.interference)
        self.filter_i_x, self.filter_i_y, self.interference_clear_x, self.interference_clear = \
            self.__remove_noise(x=self.interference_x, y=self.interference, lambda_source=self.lambda_source, adc_fr=self.ADC_fr)
        self.interference_clear_x = self.__set_0(x_axes=self.interference_clear_x, y_axes=self.interference_clear)
        self.split_num = self.__get_split_num(total_time=self.total_time, speed=self.speed,
                                              lambda_source=self.lambda_source)
        self.visibility_x, self.visibility = self.__calculate_visibility(
            x=self.interference_clear_x, y=self.interference_clear, split_num=self.split_num
        )
        self.visibility_x = self.__set_0(x_axes=self.visibility_x, y_axes=self.visibility)
        # self.filter_v_x, self.filter_v_y, self.visibility_clear_x, self.visibility_clear = \
        #     self.__remove_noise(x=self.visibility_x, y=self.visibility,
        #     ADC_fr=self.ADC_fr, lambda_source=self.lambda_source)
        self.visibility_clear_x, self.visibility_clear = self.visibility_x, self.visibility
        # self.visibility_clear = self.visibility_clear / self.visibility_clear.max() * self.visibility.max()
        self.visibility_clear_x = self.__set_0(x_axes=self.visibility_clear_x, y_axes=self.visibility_clear)
        self.h_par_x, self.h_par, self.beat_length, self.depol_len = \
            self.__calculate_h_param(visibility_x=self.visibility_clear_x, visibility=self.visibility_clear,
                                     lambda_source=self.lambda_source, delta_n=self.delta_n,
                                     source_bandwith=self.source_bandwith)
        self.per_x, self.per = self.h_par_x, self.__calculate_per(visibility=self.visibility_clear)
        print(f'Длина биений = {self.beat_length} м')
        print(f'Длина деполяризации = {self.depol_len} м')
        self.visibility_after_BD_compensation = self.__bd_compensation(self.visibility_clear)

    def read_signal(self, signal_dict: dict):
        for key in self.__dict__.keys():
            setattr(self, key, signal_dict.get(key, None))

    @staticmethod
    def __set_0(x_axes: np.ndarray, y_axes: np.ndarray):
        i = np.where(y_axes == y_axes.max())
        x_axes: np.ndarray = x_axes - x_axes[i[0][0]]
        return x_axes

    @staticmethod
    def __remove_noise(x: np.ndarray, y: np.ndarray, lambda_source: float, adc_fr: float):
        # N = 20
        # Fc1 = 2600
        # Fc2 = 6000
        # nyq = adc_fr/2
        # h = firwin2(numtaps=N, freq=[0, Fc1, Fc2, nyq], gain=[1.0, 1.0, 0.0, 0.0], nyq=nyq)
        # freq, response = freqz(h)
        # y_clear: np.ndarray = abs(lfilter(h, 1.0, y)[30:])
        # x_clear: np.ndarray = np.linspace(start=x.min(), stop=x.max(), num=y_clear.shape[0])
        # return nyq * freq / np.pi, np.abs(response), x_clear, y_clear

        n_iter = 1
        n_per = 5

        i_max = np.where(y == y.max())[0][0]
        len2i = x.shape[0] // (x.max() - x.min())
        win_half_size: int = round(lambda_source * len2i / 4 * n_per)
        window: np.ndarray = y[i_max - win_half_size: i_max + win_half_size]
        # for _ in range(10):
        #     y = medfilt(y)
        y_rfft = rfft(y)
        fr_filt = np.where(y_rfft > np.quantile(y_rfft, 0.9999))[0].max()
        print(fr_filt)
        y_rfft[fr_filt:] = 0
        y = irfft(y_rfft)
        # window = np.sin(np.linspace(0, 2 * np.pi * n_per, win_half_size * 2)) + 1
        # win_size = len(window)
        # g: np.ndarray = gaussian(win_size, std=win_size / 51 * 7)
        # window = window * g

        window_x = x[i_max - win_half_size: i_max + win_half_size]
        # method = choose_conv_method(y, window, mode='valid')
        # for _ in range(n_iter):
        #     y = correlate(y, window, mode='valid', method=method)
        x_clear: np.ndarray = np.linspace(start=x.min(), stop=x.max(), num=y.shape[0])

        return window_x, window, x_clear, y

    @staticmethod
    def __get_split_num(total_time: float, speed: float, lambda_source: float):
        split_num = total_time * speed / lambda_source / 3
        return split_num

    @staticmethod
    def __calculate_visibility(x: np.ndarray, y: np.ndarray, split_num: float):
        splited_interference_clear: np.ndarray = np.array_split(y, split_num)
        maximum = (i.max() for i in splited_interference_clear)
        minimum = (i.min() for i in splited_interference_clear)
        visibility: np.ndarray = np.fromiter(((ma - mi) / (ma + mi) for ma, mi in zip(maximum, minimum)), float)
        visibility_x: np.ndarray = np.linspace(x.min(), x.max(), num=visibility.shape[0])
        return visibility_x, visibility

    @staticmethod
    def __calculate_h_param(visibility_x: np.ndarray, visibility: np.ndarray, lambda_source: float,
                            delta_n: float, source_bandwith: float):
        y = np.divide(visibility, visibility.max())
        beat_length = lambda_source / delta_n
        depol_len = (lambda_source ** 2) / (source_bandwith * delta_n)
        h_par: np.ndarray = np.square(y) / depol_len
        h_par_x: np.ndarray = visibility_x * 2 / delta_n
        return h_par_x, h_par / 10, beat_length, depol_len

    @staticmethod
    def __calculate_per(visibility: np.ndarray):
        y = np.divide(visibility, visibility.max())
        per: np.ndarray = np.log10(np.square(y)) * 10
        return per

    @staticmethod
    def __bd_compensation(visibility: np.ndarray):
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
