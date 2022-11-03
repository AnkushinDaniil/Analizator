import numpy as np
from scipy.signal import cheby2, sosfilt, cheb2ord, freqz, remez, lfilter


class Signal:
    """Signal(signal: np.ndarray, speed: float, total_time: float, lambda_source: float,
              source_bandwith: float, delta_n: float, ADC_fr: float, pm_fr: float,
              name: str, pen)

        Класс "сигнал" представляет собой набор полей, соответствующих параметрам сигнала,
        и функций для их вычисления"""

    def __init__(self):
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
                   source_bandwith: float, delta_n: float, ADC_fr: float, pm_fr: float,
                   name: str, pen):
        n = np.size(interference)
        print()
        print(name)
        self.ADC_fr = ADC_fr
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
        self.interference_x = self.__set_0(
            self.interference_x, self.interference
        )
        self.filter_i_x, self.filter_i_y, self.interference_clear = self.__remove_noise_i(self.interference, self.ADC_fr)
        self.interference_clear_x = self.__set_0(
            self.interference_x, self.interference_clear
        )
        self.split_num = self.__get_split_num(self.total_time, self.speed)
        self.visibility_x, self.visibility = self.__calculate_visibility(
            self.interference_clear_x, self.interference_clear, self.split_num
        )
        self.visibility_x = self.__set_0(self.visibility_x, self.visibility)
        self.filter_v_x, self.filter_v_y, self.visibility_clear = self.__remove_noise_v(self.visibility)
        self.visibility_clear_x = self.__set_0(self.visibility_x, self.visibility_clear)
        self.h_par_x, self.h_par, self.beat_length, self.depol_len = \
            self.__calculate_h_param(self.visibility_clear_x, self.visibility_clear, self.lambda_source, self.delta_n,
                                     self.source_bandwith)
        print(f'Длина биений = {self.beat_length} м')
        print(f'Длина деполяризации = {self.depol_len} м')
        self.visibility_after_BD_compensation = self.__BD_compensation(self.visibility_clear)

    def read_signal(self, signal_dict: dict):
        for key in self.__dict__.keys():
            setattr(self, key, signal_dict.get(key, None))


    @staticmethod
    def __set_0(x_axes: np.ndarray, y_axes: np.ndarray):
        i = np.where(y_axes == np.max(y_axes))
        x_axes: np.ndarray = x_axes - x_axes[i[0][0]]
        return x_axes


    @staticmethod
    def __remove_noise_i(interference: np.ndarray, ADC_fr: float):
        x = np.arange(interference.shape[0])
        coef = np.polyfit(x, interference, 1)
        poly1d = np.poly1d(coef)
        linear = poly1d(x)
        interference_0: np.ndarray = interference - linear
        fs = ADC_fr  # Частота дискретизации в Гц
        wp = 2600  # Частота полосы пропускания в Гц
        ws = 6000  # Частота полосы заграждения в Гц
        gpass = 1  # Неравномерность полосы пропускания в дБ
        gstop = 100  # Затухание в полосе задерживания в дБ

        analog = False
        N, Wn = cheb2ord(wp=wp, ws=ws, gpass=gpass, gstop=gstop, analog=analog, fs=fs)
        b, a = cheby2(N=N, rs=gpass, Wn=Wn, btype='lowpass', analog=analog, fs=fs)
        w, h = freqz(b, a)
        sos = cheby2(N=N, rs=gpass, Wn=Wn, btype='lowpass', analog=analog, fs=fs, output='sos')
        interference_clear: np.ndarray = sosfilt(sos, interference_0) + linear
        # elif filt == 'Фильтр Паркса-МакКлеллана':
        #     fs = 1000  # Sample rate, Hz
        #     cutoff = 100  # Desired cutoff frequency, Hz
        #     trans_width = 80  # Width of transition from pass band to stop band, Hz
        #     numtaps = 20  # Size of the FIR filter.
        #     gpass = 0.0057563991496  # Passband Ripple
        #     gstop = 0.0001  # Stopband Attenuation
        #     b = remez(numtaps=numtaps, bands=[0, cutoff, cutoff + trans_width, 0.5 * fs], desired=[gpass, gstop], Hz=fs)
        #     w, h = freqz(b)
        #     y = lfilter(b, [1.0], x)
        #     interference_clear: np.ndarray = y + linear

        return w/np.pi*ADC_fr/2, 10 * np.log10(abs(h)), interference_clear

    @staticmethod
    def __remove_noise_v(visibility: np.ndarray):
        fs = 1000  # Sample rate, Hz
        cutoff = 100  # Desired cutoff frequency, Hz
        trans_width = 80  # Width of transition from pass band to stop band, Hz
        numtaps = 20  # Size of the FIR filter.
        gpass = 0.0057563991496  # Passband Ripple
        gstop = 0.0001  # Stopband Attenuation
        b = remez(numtaps=numtaps, bands=[0, cutoff, cutoff + trans_width, 0.5 * fs], desired=[gpass, gstop], Hz=fs)
        w, h = freqz(b)
        y = lfilter(b, [1.0], visibility)
        visibility_clear = y / y.max()

        return w / np.pi / 2, 10 * np.log10(abs(h)), visibility_clear

    @staticmethod
    def __get_split_num(total_time: float, speed: float):
        split_num = total_time * speed / 0.000001
        return split_num

    @staticmethod
    def __calculate_visibility(x: np.ndarray, y: np.ndarray, split_num: float):
        splited_interference_clear: np.ndarray = np.array_split(y, split_num)
        # print(splited_interference_clear)
        maximum = (i.max() for i in splited_interference_clear)
        # print(maximum)
        minimum = (i.min() for i in splited_interference_clear)
        # print(minimum)
        visibility: np.ndarray = np.fromiter(((ma - mi) / (ma + mi) for ma, mi in zip(maximum, minimum)), float)
        # print(visibility)
        visibility_x: np.ndarray = np.linspace(x.min(), x.max(), num=visibility.shape[0])
        return visibility_x, visibility

    @staticmethod
    def __calculate_h_param(visibility_x: np.ndarray, visibility: np.ndarray, lambda_source: float,
                            delta_n: float, source_bandwith: float):
        y = np.divide(visibility, visibility.max())
        beat_length = lambda_source / delta_n
        depol_len = (lambda_source ** 2) / (source_bandwith * delta_n)
        h_par: np.ndarray = 10 * np.log10(np.square(y) / depol_len)
        h_par_x: np.ndarray = visibility_x * 2 / delta_n
        return h_par_x, h_par, beat_length, depol_len

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
