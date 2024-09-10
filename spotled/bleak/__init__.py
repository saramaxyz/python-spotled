from bleak import BleakClient, BleakGATTCharacteristic
from asyncio import Event
import time
import os.path

from .models.commands import * 
from .models.animation import * 
from .models.enums import *
from .models.responses import * 
from .graphics import *
from .fontops import *


class LedConnection:
    def __init__(self, address):
        self.mtu = 23
        self.connection = BleakClient(address)
        self.connection.on_connect = lambda mtu: self._set_mtu(mtu)
        self.current_wait_event = Event()
        self.last_data = None
        self.data_serial_no = 0
        self.command_serial_no = 0

    async def _init(self):
        await self._ensure_connection()
        self.cmd_handle, self.data_handle = (
            self.connection.services.services[75].characteristics[0],
            self.connection.services.services[75].characteristics[1],
        )
        await self.connection.write_gatt_char(self.cmd_handle, b"\x00\x00\x00\x01")
        await self.connection.start_notify(self.cmd_handle, self._on_notification)

        self.buffer_size = (
            await self.query_command(GetBufferSizeCommand())
        ).buffer_size
        
        display_info = await self.query_command(GetDisplayInfoCommand())
        self.width = display_info.width
        self.height = display_info.height
        self.frame_limit = display_info.frame_limit
        self.brightness = display_info.brightness
        self.color_depth = display_info.color_depth

    def _on_notification(self, handle, data):
        if handle == self.cmd_handle:
            self.last_data = data
            self.current_wait_event.set()

    def _set_mtu(self, mtu):
        self.mtu = mtu

    def _next_data_serial_no(self):
        self.data_serial_no = (self.data_serial_no + 1) & 0xFFFFFFFF
        return self.data_serial_no

    def _next_command_serial_no(self):
        self.command_serial_no = (self.command_serial_no + 1) & 0xFFFF
        return self.command_serial_no

    async def _ensure_connection(self):
        if not self.connection.is_connected:
            try:
                await self.connection.connect()
            except:
                # will sometimes throw if already trying to connect
                pass
            for _ in range(50):
                if self.connection.is_connected:
                    break
                time.sleep(0.1)
            else:
                raise TimeoutError("Timeout exceeded waiting for bluetooth connection.")

    async def send_command(self, command):
        """
        Send a control command to the device.
        Used for basic commands and data sending flow control.
        """
        await self._ensure_connection()
        self.current_wait_event.clear()
        await self.connection.write_gatt_char(self.cmd_handle, command.serialize())

    async def query_command(self, command, timeout=0.2, attempts=5):
        """
        Send a control command to the device and wait for a response.
        Used for basic commands and data sending flow control.
        """
        for i in range(attempts + 1):
            try:
                await self.send_command(command)
                return await self.wait_for_response(timeout)
            except TimeoutError:
                if i == attempts:
                    raise
                await self.connection.disconnect()

    async def wait_for_response(self, timeout=0.2):
        """
        Wait for and return a response, usually from a command sent via send_command.
        """
        if not await self.current_wait_event.wait():
            raise TimeoutError("Timeout exceeded waiting for GATT response.")
        return getCommandResponse(self.last_data)

    async def _send_data_internal(self, data_command, timeout=0.2):
        await self._ensure_connection()
        data_command.serial_no = self._next_data_serial_no()
        serial_no = self._next_command_serial_no()

        payload = data_command.serialize()
        await self.send_command(
            SendingDataStartCommand(serial_no, data_command.command_type, len(payload))
        )
        response = await self.wait_for_response(timeout)
        assert type(response) == SendingDataResponse
        assert response.serial_no == serial_no
        assert response.command_type == data_command.command_type
        assert response.error_code == 0

        seek = 0
        sent_payloads = 0
        send_size = self.mtu - 3
        send_count = self.buffer_size // send_size

        
        while seek < len(payload):
            self.current_wait_event.clear()

            await self.connection.write_gatt_char(
                self.data_handle, payload[seek : seek + send_size], response=False
            )
            sent_payloads += 1
            seek += send_size
            

            if sent_payloads >= send_count:
                sent_payloads = 0
                
                response = await self.wait_for_response(timeout)
                assert type(response) == ContinueSendingResponse
                assert response.serial_no == serial_no
                assert response.command_type == data_command.command_type
                seek = response.continue_from

            

        await self.send_command(
            SendingDataFinishCommand(serial_no, data_command.command_type, len(payload))
        )
        await self.wait_for_response(timeout)

    async def send_data(self, data_command, timeout=0.2, attempts=5):
        """
        Send a data command to the device.
        Currently only SendDataCommand is used, which accepts raw serialized data.
        """
        for i in range(attempts + 1):
            try:
                await self._send_data_internal(data_command, timeout)
                return
            except TimeoutError:
                if i == attempts:
                    raise
                await self.connection.disconnect()

    async def set_brightness(self, brightness):
        """
        Sets the display brightness. 0 is lowest and 100 is highest.
        """
        await self.send_data(SendDataCommand(BrightnessData(brightness).serialize()))
        self.brightness = brightness

    async def set_screen_mode(self, mode: ScreenMode):
        """
        This allows flipping and mirroring the display. See ScreenMode Enum.
        """
        await self.send_data(SendDataCommand(ScreenModeData(mode.value).serialize()))

    async def set_text_by_chars(
        self, text, effect=Effect.SCROLL_LEFT, font="6x12", speed=0, char_limit=72
    ):
        """
        Sends text as characters. The device decides how to display them.
        This tends to be slower and more limited than set_text which sends the text as an animation.
        """
        if len(text) > char_limit:
            raise ValueError("The text exceeds the device character limit.")

        font_data = find_and_load_font(font)
        font_characters = create_font_characters(text, font_data, self.height)
        font_character_data = SendDataCommand(FontData(font_characters).serialize())
        text_data = SendDataCommand(TextData(text, speed, effect).serialize())
        await self.send_data(font_character_data)
        await self.send_data(text_data)

    async def set_text_lines(
        self,
        text,
        align=Align.CENTER,
        font="4x6",
        frame_duration=2,
        line_height=6,
        effect=Effect.NONE,
        speed=20,
        reflow=True,
    ):
        """
        Sends multi-line text as an animation. Can pack two lines of text onto the display.
        """
        font_data = find_and_load_font(font)

        if reflow:
            lines = reflow_text(text, font_data, self.width)
        else:
            lines = text.replace("\r", "").split("\n")

        frames = lines_to_frames(
            lines, font_data, align, self.width, self.height // line_height, line_height
        )

        
        if len(frames) > self.frame_limit:
            raise ValueError("The animation exceeds the device frame limit.")

        frame_data = SendDataCommand(
            AnimationData(
                [
                    FrameData(self.width, self.height, gen_bitmap(*frame))
                    for frame in frames
                ],
                int(frame_duration * 1000),
                speed,
                effect,
            ).serialize()
        )

        await self.send_data(frame_data)

    async def set_text(self, text, effect=Effect.SCROLL_LEFT, font="6x12", speed=0):
        """
        Sends single-line scrolling text as an animation.
        """
        await self.set_text_lines(
            text,
            Align.LEFT,
            font,
            line_height=self.height,
            effect=effect,
            speed=speed,
            reflow=False,
        )

    async def clear(self):
        """
        Clears the display by sending an empty frame.
        """
        frame_data = SendDataCommand(
            AnimationData(
                [
                    FrameData(
                        self.width,
                        self.height,
                        b"\x00" * int(self.width * self.height / 8),
                    )
                ],
                0,
                0,
                Effect.NONE,
            ).serialize()
        )

        await self.send_data(frame_data)

    async def disconnect(self):
        await self.connection.disconnect()


async def createLedConnection(address):
    sender = LedConnection(address)
    await sender._init()
    return sender
