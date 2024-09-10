from .byte import ByteReader

class GenericCommandResponse:
    """
    This is the generic response wrapper for commands
    that indicates the response type.
    """

    def __init__(self, data):
        d = ByteReader(data)
        # d.read_bytes(3)  # junk data?
        length = d.read_byte()
        self.command_type = d.read_byte()
        self.content = d.read_bytes(length - 2)


class SendingDataResponse:
    """
    This response is send from the device after you send it a request to
    send a data command.
    """

    def __init__(self, content):
        assert len(content) == 5
        d = ByteReader(content)
        self.serial_no = d.read_short()
        self.error_code = d.read_byte()
        self.command_type = d.read_short()


class ContinueSendingResponse:
    """
    This response is send from the device after it has finished processing
    the last 6 data commands and is ready for more data.
    """

    def __init__(self, content):
        assert len(content) == 8
        d = ByteReader(content)
        self.serial_no = d.read_short()
        self.command_type = d.read_short()
        self.continue_from = d.read_int()


class PauseSendingResponse:
    """
    This response is sent from the device when it has an error reading sent data.
    Usually this indicates an invalid MTU (your packets are too big or too small)
    """

    def __init__(self, content):
        assert len(content) == 6
        d = ByteReader(content)
        self.serial_no = d.read_short()
        self.command_type = d.read_short()
        self._unknown = d.read_byte()
        self.offset = d.read_byte()


class DisplayInfoResponse:
    """
    Contains response from GetDisplayInfoCommand
    """

    COLOR_MONOCHROME = 16
    COLOR_RGB = 255

    def __init__(self, content):
        assert len(content) == 11
        d = ByteReader(content)
        d.read_bytes(2)  # junk data?
        assert d.read_byte() == 0
        self.width = d.read_short()
        self.height = d.read_short()
        self.color_depth = d.read_byte()
        self.frame_limit = d.read_byte()
        self.brightness = d.read_byte()
        self.font_info = d.read_byte()


class VersionResponse:
    """
    Contains response from GetVersionCommand
    """

    def __init__(self, content):
        assert len(content) == 13
        d = ByteReader(content)
        d.read_bytes(2)  # junk data?
        assert d.read_byte() == 0
        self.device_type = d.read_short()
        self.device_revision = d.read_int()
        self.software_revision = d.read_int()


class BufferSizeResponse:
    """
    Contains response from GetBufferSizeCommand
    """

    def __init__(self, content):
        assert len(content) == 7
        d = ByteReader(content)
        d.read_bytes(2)  # junk data?
        assert d.read_byte() == 0
        self.buffer_size = d.read_int()


def getCommandResponse(data):
    
    response = GenericCommandResponse(data)

    response_map = {
        2: SendingDataResponse,
        255: ContinueSendingResponse,
        254: PauseSendingResponse,
        19: DisplayInfoResponse,
        17: VersionResponse,
        21: BufferSizeResponse,
    }

    response_class = response_map.get(response.command_type)

    if response_class:
        
        return response_class(response.content)

    
    return response