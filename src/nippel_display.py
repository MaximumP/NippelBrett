import logging
import time
from cysystemd.journal import JournaldLogHandler

from external import I2C_LCD_driver

logger = logging.getLogger("nippel_brett_display")
logger.addHandler(JournaldLogHandler())
logger.setLevel(logging.DEBUG)
display = I2C_LCD_driver.lcd()


while True:
    display.lcd_clear()
    display.lcd_display_string("Nippel Brett", 1)
    time.sleep(1)
    display.lcd_clear()
    display.lcd_display_string("Nippel Brett", 2)
    time.sleep(1)
