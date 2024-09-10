from models.byte import ByteWriter
from models.enums import Effect

class TimeData:
    """
    The amount of time in milliseconds to show each frame of
    an animation. Only used if there is no effect applied.
    """

    def __init__(self, time):
        self.time = time

    def serialize(self):
        d = ByteWriter()
        d.write_int(10)  # length
        d.write_short(7)  # type
        d.write_byte(0)  # always zero?
        d.write_short(self.time)
        d.write_checksum()
        return d.to_bytes()


class SpeedData:
    """
    The speed of the animation. Used if effect is not none.
    """

    def __init__(self, speed):
        self.speed = speed

    def serialize(self):
        d = ByteWriter()
        d.write_int(8)  # length
        d.write_short(9)  # type
        d.write_byte(self.speed)
        d.write_checksum()
        return d.to_bytes()

class EffectData:
    """
    Indicates the display mode (static, scrolling, etc)
    for text/animations on the device.
    """

    def __init__(self, effect: Effect):
        self.effect = effect

    def serialize(self):
        d = ByteWriter()
        d.write_int(8)  # length
        d.write_short(8)  # type
        d.write_byte(self.effect.value)
        d.write_checksum()
        return d.to_bytes()


class FrameData:
    COLOR_DEPTH_MONOCHROME = 1
    COLOR_DEPTH_RGB = 24
    """
    A single display frame. Use gen_bitmap to generate one
    from text consisting of ./1 or convert the lines to
    bytes in order. Also supports specifying a color
    depth but I have no such devices to test this on.
    """

    def __init__(self, width, height, bitmap, depth=1):
        self.width = width
        self.height = height
        self.bitmap = bitmap
        self.depth = depth

    def serialize(self):
        d = ByteWriter()
        d.write_int(len(self.bitmap) + 12)  # length
        d.write_short(96)  # type
        d.write_short(self.width)
        d.write_short(self.height)
        d.write_byte(self.depth)
        d.write_bytes(self.bitmap)
        d.write_checksum()
        return d.to_bytes()


class AnimationData:
    """
    Wraps a series of frames (max 20) along with speed, time,
    and effect data. Time is per-frame time, but it is only
    used if no effects are used.
    """

    def __init__(self, frames, time, speed, effects: Effect):
        self.frames = frames
        self.time = time
        self.speed = speed
        self.effects = effects

    def serialize(self):
        d = ByteWriter()
        d.write_int(9)  # length
        d.write_short(11)  # type
        d.write_short(len(self.frames))
        d.write_checksum()
        for frame in self.frames:
            d.write_bytes(frame.serialize())
        d.write_bytes(TimeData(self.time).serialize())
        d.write_bytes(SpeedData(self.speed).serialize())
        d.write_bytes(EffectData(self.effects).serialize())
        return d.to_bytes()


class ColorData:
    """
    An RGB color value. Used for text.
    """

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def serialize(self):
        d = ByteWriter()
        d.write_int(10)  # length
        d.write_short(2)  # type
        d.write_byte(self.red)
        d.write_byte(self.green)
        d.write_byte(self.blue)
        d.write_checksum()
        return d.to_bytes()


class NumberBarData:
    """
    Graphs 16 values from 0-12 as a bar graph. Intended for
    displaying a music spectrum display.
    """

    def __init__(self, values):
        self.values = values

    def serialize(self):
        d = ByteWriter()
        d.write_int(len(self.values) * 2 + 9)  # length
        d.write_short(10)  # type
        d.write_short(len(self.values))
        for value in self.values:
            d.write_short(value)
        d.write_checksum()
        return d.to_bytes()