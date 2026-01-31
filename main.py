from crccheck.crc import Crc16Modbus
import serial
import RPi.GPIO as GPIO
from serial.rs485 import RS485Settings
from time import sleep
import struct
from dataclasses import dataclass
from textwrap import dedent
from generics import write_to_csv, get_next_midnight, rename_log_file, DATA_LOG_PATH
from datetime import datetime

RIVER_SENSOR_COMM_0 = b'\x80\x04\x00\x01\x00\x09\x7F\xDD'


@dataclass(frozen=True)
class ResponseMessage:
    slave_address: int
    function_code: int
    byte_count: int
    water_level: int  # Reg 1: x1000
    air_height: int  # Reg 2: x1000
    signal_strength: int  # Reg 3
    noise_threshold: int  # Reg 4
    filter_times: int  # Reg 5
    bottom_to_gauge: int  # Reg 6: x1000 (Read value)
    # Note: There are more registers in the payload, but we only strictly map up to Reg 6 here

    @classmethod
    def from_bytes(cls, raw_data: bytes) -> 'ResponseMessage':
        FMT = '>BBBHHHHHH'
        max_size = struct.calcsize(FMT)
        unpacked_data = struct.unpack(FMT, raw_data[:max_size])
        return cls(*unpacked_data)

    def print_clean(self):
        print(dedent(f"""\
        --- SENSOR READINGS ---
        Water Level:     {self.water_level / 1000.0:.3f} m
        Air Height:      {self.air_height / 1000.0:.3f} m
        Dist to Bottom:  {self.bottom_to_gauge / 100.0:.3f} m 
        -----------------------
        """))

    def save_to_file(self, filepath: str) -> None:
        date = datetime.now()
        write_to_csv(filepath, [date, self.air_height])


def do_crc_check(data) -> int:
    crc = Crc16Modbus()
    crc.process(data)
    return crc.final()


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


def connect_to_serial() -> serial.Serial:
    try:
        ser = serial.Serial(
            port='/dev/ttyAMA3',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
    except serial.SerialException as e:
        print(f'Waiting for RS485 connection: {e}')
        sleep(3)
    else:
        return ser


RIVER_SENSOR_PORT = connect_to_serial()


RIVER_SENSOR_PORT.rs485_mode = RS485Settings(
    rts_level_for_tx=True,
    rts_level_for_rx=False,
    delay_before_tx=0.0,
    delay_before_rx=0.0
)


if __name__ == "__main__":
    now = datetime.now()
    next_midnight = get_next_midnight(now)
    while RIVER_SENSOR_PORT.is_open:
        # RIVER_SENSOR_PORT.write(RIVER_SENSOR_COMM_0)
        # sleep(5)
        RIVER_SENSOR_PORT.write(RIVER_SENSOR_COMM_0)
        sleep(5)  # TODO: Change this value, possible
        raw_data = RIVER_SENSOR_PORT.read(RIVER_SENSOR_PORT.in_waiting)
        if do_crc_check(raw_data) != 0:
            print('Reply:', raw_data)
            print('CRC Check Failed!')
            # TODO: Add retry mechanism (3 retries every 5 seconds).
        else:
            if now > next_midnight:
                rename_log_file(now)
                next_midnight = get_next_midnight(now)

            # Handle Displaying Data
            print('Reply:', raw_data)
            data = ResponseMessage.from_bytes(raw_data)
            print(data)
            data.print_clean()

            # Handle Saving Data
            data.save_to_file(DATA_LOG_PATH)

            now = datetime.now()
    else:
        print('PORT CLOSED')
