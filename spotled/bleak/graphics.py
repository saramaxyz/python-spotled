from .models.commands import ByteWriter

def gen_color_bitmap(*lines, color_map={".": (0, 0, 0), "1": (255, 255, 255)}):
    """
    Converts a "text" bitmap consisting of a predefined map of characters to a BGR tuple.
    """
    data = bytearray()
    for text in lines:
        for i in range(0, len(text)):
            color = color_map[text[i]]
            data.append(color[0])
            data.append(color[1])
            data.append(color[2])
    return bytes(data)


def gen_bitmap(*lines: [str], min_len=0, true_char="1"):
    """
    Converts a "text" bitmap consisting of . and 1
    to a raw binary bitmap. min_len sets the minimum
    row length.
    """
    if min_len % 8 != 0:
        min_len += 8 - (min_len % 8)

    data = bytearray()
    for text in lines:
        if len(text) < min_len:
            text += "." * (min_len - len(text))
        else:
            excess = len(text) % 8
            if excess != 0:
                text += "." * (8 - excess)
        for i in range(0, len(text), 8):
            data.append(
                ((text[i] == true_char) << 7)
                | ((text[i + 1] == true_char) << 6)
                | ((text[i + 2] == true_char) << 5)
                | ((text[i + 3] == true_char) << 4)
                | ((text[i + 4] == true_char) << 3)
                | ((text[i + 5] == true_char) << 2)
                | ((text[i + 6] == true_char) << 1)
                | (text[i + 7] == true_char)
            )
    return bytes(data)
