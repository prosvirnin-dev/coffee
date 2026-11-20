"""Не дает macOS уйти в сон из-за бездействия: имитирует активность пользователя."""

import ctypes
import logging
import os
import time
from dataclasses import dataclass, field

from pynput import keyboard, mouse

# Логи пишутся в терминал. Уровень задается переменной окружения COFFEE_LOG_LEVEL.
logging.basicConfig(
    level=os.environ.get('COFFEE_LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Системная библиотека macOS. Из нее нужна одна функция — время с последнего ввода.
_cg = ctypes.CDLL('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
# Типы аргументов и результата, иначе ctypes неверно передаст числа.
_cg.CGEventSourceSecondsSinceLastEventType.restype = ctypes.c_double
_cg.CGEventSourceSecondsSinceLastEventType.argtypes = [ctypes.c_int32, ctypes.c_uint32]


@dataclass
class Coffee:
    """Имитирует активность пользователя, когда бездействие превышает порог.

    Attributes:
        threshold: Порог бездействия в секундах.
        interval: Интервал проверки в секундах.
    """

    threshold: float = 150
    interval: float = 30
    # Контроллеры pynput создают события мыши и клавиатуры. В конструктор и вывод объекта не попадают.
    _mouse: mouse.Controller = field(default_factory=mouse.Controller, init=False, repr=False)
    _keyboard: keyboard.Controller = field(default_factory=keyboard.Controller, init=False, repr=False)

    @property
    def idle_time(self) -> float:
        """Секунды с последнего события мыши или клавиатуры."""
        # Состояние всей системы (1) по любому виду ввода (0xFFFFFFFF).
        return _cg.CGEventSourceSecondsSinceLastEventType(1, 0xFFFFFFFF)

    def nudge(self) -> None:
        """Сдвигает курсор на пиксель и обратно и нажимает F15."""
        # Курсор возвращается на место, поэтому движение незаметно.
        self._mouse.move(1, 0)
        self._mouse.move(-1, 0)
        # F15 обычно ни к чему не привязана, поэтому нажатие не мешает работе.
        self._keyboard.tap(keyboard.Key.f15)

    def run(self) -> None:
        """Проверяет бездействие и имитирует активность до Ctrl+C."""
        logger.info('Запущен: {}.'.format(self))
        try:
            # Раз в интервал сверяет бездействие с порогом. Если порог превышен, система получает событие ввода и
            # сбрасывает таймер бездействия.
            while True:
                idle = self.idle_time
                logger.debug('Бездействие: {} сек.'.format(int(idle)))
                if idle >= self.threshold:
                    self.nudge()
                    logger.info('Имитирована активность. Бездействие: {} сек.'.format(int(idle)))
                time.sleep(self.interval)
        except KeyboardInterrupt:
            # Ctrl+C завершает цикл без трассировки.
            logger.info('Остановлен.')


def main() -> None:
    """Запускает Coffee с настройками по умолчанию."""
    Coffee().run()
