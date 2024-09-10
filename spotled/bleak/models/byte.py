class ByteWriter:
    """
    A class for writing bytes into binary blob by type sequentially.
    Also supports writing checksums for written data.
    """

    def __init__(self):
        self.content = bytearray()
        self.checksum_start_pos = 0

    def write_byte(self, value):
        self.content.append(value & 255)

    def write_short(self, value):
        self.content.append((value >> 8) & 255)
        self.content.append(value & 255)

    def write_int(self, value):
        self.content.append((value >> 24) & 255)
        self.content.append((value >> 16) & 255)
        self.content.append((value >> 8) & 255)
        self.content.append(value & 255)

    def write_bytes(self, value):
        self.content.extend(value)

    def start_checksum(self):
        self.checksum_start_pos = len(self.content)

    def write_checksum(self):
        value = 0
        for b in self.content[self.checksum_start_pos :]:
            value += 255 & b
        if value > 255:
            value = (~value) + 1
        self.content.append(value & 255)

    def to_bytes(self):
        return bytes(self.content)


class ByteReader:
    """
    A class for reading bytes out of a binary blob by type sequentially.
    """

    def __init__(self, content):
        self.content = content
        self.current_pos = 0

    def read_byte(self):
        value = self.content[self.current_pos]
        self.current_pos += 1
        return value

    def read_short(self):
        value = (self.content[self.current_pos] << 8) + self.content[self.current_pos + 1]
        self.current_pos += 2
        return value

    def read_int(self):
        value = (
            (self.content[self.current_pos] << 24)
            + (self.content[self.current_pos + 1] << 16)
            + (self.content[self.current_pos + 2] << 8)
            + self.content[self.current_pos + 3]
        )
        self.current_pos += 4
        return value

    def read_bytes(self, count):
        value = self.content[self.current_pos : self.current_pos + count]
        self.current_pos += count
        return value
