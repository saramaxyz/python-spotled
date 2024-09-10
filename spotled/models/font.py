from models.enums import Effect

class FontData:
    """
    Wraps a list of font character glyphs for text display.
    """

    def __init__(self, font_characters):
        self.font_characters = font_characters

    def serialize(self):
        d = ByteWriter()
        d.write_int(9)  # length
        d.write_short(5)  # type
        d.write_short(len(self.font_characters))
        d.write_checksum()
        for font_character in self.font_characters:
            d.write_bytes(font_character.serialize())
        return d.to_bytes()


class FontCharacterData:
    """
    Wraps a single character glyph. Must be sent before
    the glyph can be displayed in text mode.
    """

    def __init__(self, width, height, character, bitmap):
        self.width = width
        self.height = height
        self.character = character
        self.bitmap = bitmap

    def serialize(self):
        d = ByteWriter()
        d.write_int(len(self.bitmap) + 15)  # length
        d.write_short(13)  # type
        d.write_byte(1)  # always 1?
        d.write_short(self.width)
        d.write_short(self.height)
        d.write_short(ord(self.character))
        d.write_byte(len(self.bitmap))
        d.write_bytes(self.bitmap)
        d.write_checksum()
        return d.to_bytes()


class CharacterData:
    """
    A single unicode character value.
    """

    def __init__(self, char):
        self.char = char

    def serialize(self):
        d = ByteWriter()
        d.write_int(9)  # length
        d.write_short(3)  # type
        d.write_short(ord(self.char))
        d.write_checksum()
        return d.to_bytes()


class TextData:
    """
    This wraps a list of characters. The character glyphs
    must have been sent previously or the device will not
    be able to display them properly. It also sends colors
    and speed/effect data.
    """

    def __init__(self, text, speed, effects: Effect, colors=None):
        self.text = text
        self.colors = colors
        self.speed = speed
        self.effects = effects

    def serialize(self):
        d = ByteWriter()
        d.write_int(10)  # length
        d.write_short(4)  # type
        d.write_short(len(self.text))
        d.write_byte(1)  # always 1?
        d.write_checksum()
        for i, character in enumerate(self.text):
            if self.colors is not None:
                d.write_bytes(self.colors[i].serialize())
            else:
                d.write_bytes(ColorData(255, 255, 255).serialize())
            d.write_bytes(CharacterData(character).serialize())
        d.write_bytes(SpeedData(self.speed).serialize())
        d.write_bytes(TimeData(0).serialize())
        d.write_bytes(EffectData(self.effects).serialize())
        return d.to_bytes()
