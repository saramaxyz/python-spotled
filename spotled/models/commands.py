from models.byte import ByteWriter

class SendingDataStartCommand:
    """
    Indicates to the device that it is about to be sent
    new command data.
    """

    def __init__(self, serial_no, command_type, command_length):
        self.serial_no = serial_no
        self.command_type = command_type
        self.command_length = command_length

    def serialize(self):
        d = ByteWriter()
        d.write_byte(10)  # length
        d.write_byte(1)  # SendingDataStartCommand
        d.write_short(self.serial_no)
        d.write_short(self.command_type)
        d.write_int(self.command_length)
        return d.to_bytes()


class SendingDataFinishCommand:
    """
    Indicates to the device that all of the command data
    has been sent off successfully.
    """

    def __init__(self, serial_no, command_type, command_length):
        self.serial_no = serial_no
        self.command_type = command_type
        self.command_length = command_length

    def serialize(self):
        d = ByteWriter()
        d.write_byte(10)  # length
        d.write_byte(3)  # SendingDataFinishCommand
        d.write_short(self.serial_no)
        d.write_short(self.command_type)
        d.write_int(self.command_length)
        return d.to_bytes()


class GetDisplayInfoCommand:
    """
    Allows retrieving display parameters.
    """

    def serialize(self):
        d = ByteWriter()
        d.write_byte(4)  # length
        d.write_byte(18)  # GetDisplayInfoCommand
        d.write_short(0)
        return d.to_bytes()


class GetVersionCommand:
    """
    Allows retrieving device version info.
    """

    def serialize(self):
        d = ByteWriter()
        d.write_byte(4)  # length
        d.write_byte(16)  # GetVersionCommand
        d.write_short(0)
        return d.to_bytes()


class GetBufferSizeCommand:
    """
    Allows retrieving data buffer size.
    """

    def serialize(self):
        d = ByteWriter()
        d.write_byte(4)  # length
        d.write_byte(20)  # GetBufferSizeCommand
        d.write_short(0)
        return d.to_bytes()


class SendDataCommand:
    """
    The main command used to send data to the device
    including animations, text, and display settings.
    This wraps ByteWriter and handles checksums for you.
    """

    def __init__(self, content):
        self.serial_no = 1
        self.command_type = 32772
        self.content = content

    def serialize(self):
        d = ByteWriter()
        d.write_int(15)  # length of header
        d.write_short(self.command_type)
        d.write_int(self.serial_no)
        d.write_int(len(self.content))
        d.write_checksum()
        d.write_bytes(self.content)
        return d.to_bytes()


class BrightnessData:
    """
    Specifies the brightness of the display
    from 0-100. Sent using a data command.
    """

    def __init__(self, brightness):
        self.brightness = brightness

    def serialize(self):
        d = ByteWriter()
        d.write_int(8)  # length
        d.write_short(14)  # type
        d.write_byte(self.brightness)
        d.write_checksum()
        return d.to_bytes()


class ScreenModeData:
    """
    Specifies if the screen should be flipped or
    mirrored. Sent using a data command.
    """

    def __init__(self, mode):
        self.mode = mode

    def serialize(self):
        d = ByteWriter()
        d.write_int(8)  # length
        d.write_short(15)
        d.write_byte(self.mode)
        d.write_checksum()
        return d.to_bytes()