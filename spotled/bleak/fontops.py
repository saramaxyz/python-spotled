from .models.enums import Effect, Align
import os.path
from typing import List
from .models.font import *


def parse_yaff_font(fontfile):
    font = {}
    with open(fontfile) as fh:
        current_char = None
        line_acc = []
        for rl in fh:
            line = rl.strip()
            if line.startswith("#"):
                continue
            if line.endswith(":") and (line.startswith("0x") or line.startswith("u+")):
                if current_char is not None:
                    font[current_char] = line_acc
                    line_acc = []
                current_char = chr(int(line[2:-1], 16))
            elif ("." in line or "@" in line) and not ":" in line:
                line_acc.append(line.replace("@", "1"))
        if current_char is not None:
            font[current_char] = line_acc
    return font


def parse_draw_font(fontfile):
    font = {}
    with open(fontfile) as fh:
        current_char = None
        line_acc = []
        for rl in fh:
            line = rl.strip()
            if len(line) > 2 and line[2] == ":":
                if current_char is not None:
                    font[current_char] = line_acc
                    line_acc = []
                current_char = chr(int(line[0:2], 16))
                if len(line) > 3:
                    line_acc.append(
                        line[3:].strip().replace("#", "1").replace("-", ".")
                    )
            elif "-" in line or "#" in line:
                line_acc.append(line.replace("#", "1").replace("-", "."))
        if current_char is not None:
            font[current_char] = line_acc
    return font


def parse_font(fontfile):
    if fontfile.endswith(".yaff"):
        return parse_yaff_font(fontfile)
    if fontfile.endswith(".draw"):
        return parse_draw_font(fontfile)
    raise TypeError("Unknown font type.")


def find_and_load_font(font_name):
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../fonts")
    extensions = ["yaff", "draw"]

    # Try to find a file with one of the extensions
    for ext in extensions:
        try_font = os.path.join(base_path, f"{font_name}.{ext}")
        if os.path.exists(try_font):
            return parse_font(try_font)

    # If no file is found with the given name and extensions
    raise FileNotFoundError(
        f"Could not find font file for '{font_name}' with extensions {extensions}"
    )


def pad_character_to_height(char_data: List[str], min_height: int, min_length: int = 0):
    height = len(char_data)
    filler_line = "." * min_length
    if height < min_height:
        diff = min_height - height
        for _ in range(diff // 2 + diff % 2):
            char_data.insert(0, filler_line)
        for _ in range(diff // 2):
            char_data.append(filler_line)
    return char_data


def pad_row_to_width(row_data: str, min_width: int, align: Align = Align.CENTER) -> str:
    width = len(row_data)
    remaining = min_width - width
    if remaining > 0:
        if align == Align.LEFT:
            return row_data + ("." * remaining)
        if align == Align.CENTER:
            return (
                ("." * (remaining // 2))
                + row_data
                + ("." * (remaining // 2 + remaining % 2))
            )
        if align == Align.RIGHT:
            return ("." * remaining) + row_data
    return row_data


def find_char_in_font(char: str, font_data: dict[str : List[str]]) -> List[str]:
    try:
        return font_data[char]
    except KeyError:
        if "\ufffd" in font_data:
            return font_data["\ufffd"]
        elif "\x00" in font_data:
            return font_data["\x00"]
        else:
            return font_data[" "]


def create_font_characters(
    text: str, font_data: dict[str : List[str]], min_height=12
) -> [FontCharacterData]:
    font_characters = []
    for char in text:
        char_data = find_char_in_font(char, font_data)
        height = len(char_data)
        width = len(char_data[0])
        if height < min_height:
            pad_character_to_height(char_data, min_height)
            height = min_height
        if width < height:
            width = height
        font_characters.append(
            FontCharacterData(
                width, height, char, gen_bitmap(*char_data, min_len=width)
            )
        )
    return font_characters


def reflow_text(text: str, font_data: dict[str : List[str]], width=48) -> List[str]:
    lines = text.replace("\r", "").split("\n")
    wrapped_lines = []
    for line in lines:
        current_line = ""
        remaining_width = width
        for i, orig_word in enumerate(line.split(" ")):
            if i != 0:
                word = " " + orig_word
            else:
                word = orig_word

            text_width = sum(
                len(find_char_in_font(char, font_data)[0]) for char in word
            )
            if remaining_width - text_width >= 0:
                remaining_width -= text_width
                current_line += word
            elif text_width > width:
                for char in word:
                    char_width = len(find_char_in_font(char, font_data)[0])
                    if remaining_width - char_width >= 0:
                        remaining_width -= char_width
                        current_line += char
                    else:
                        wrapped_lines.append(current_line)
                        remaining_width = width - char_width
                        current_line = char
            else:
                wrapped_lines.append(current_line)
                text_width = sum(
                    len(find_char_in_font(char, font_data)[0]) for char in orig_word
                )
                remaining_width = width - text_width
                current_line = orig_word
        wrapped_lines.append(current_line)
    return wrapped_lines


def lines_to_frames(
    lines: List[str],
    font_data: dict[str : List[str]],
    align: Align = Align.CENTER,
    width=48,
    lines_per_frame=2,
    line_height=6,
) -> str:
    raster_lines = []
    for line in lines:
        raster_line = ["" for _ in range(line_height)]
        for char in line:
            char_data = find_char_in_font(char, font_data)
            height = len(char_data)
            if height > line_height:
                raise ValueError("Character height exceeds line height.")
            if height < line_height:
                pad_character_to_height(char_data, line_height, len(char_data[0]))
            for i, char_line in enumerate(char_data):
                raster_line[i] += char_line
        while len(raster_line[0]) > width:
            overflow_line = []
            for i in range(len(raster_line)):
                overflow_line.append(raster_line[i][:width])
                raster_line[i] = raster_line[i][width:]
            raster_lines.append(overflow_line)
        if len(raster_line[0]) < width:
            for i in range(len(raster_line)):
                raster_line[i] = pad_row_to_width(raster_line[i], width, align)
        raster_lines.append(raster_line)
    raster_frames = []
    current_frame = []
    current_frame_line_length = 0
    for raster_line in raster_lines:
        if current_frame_line_length < lines_per_frame:
            current_frame.extend(raster_line)
            current_frame_line_length += 1
        else:
            raster_frames.append(current_frame)
            current_frame = raster_line
            current_frame_line_length = 1
    if len(current_frame) > 0:
        if current_frame_line_length < lines_per_frame:
            for _ in range(lines_per_frame - current_frame_line_length):
                current_frame.extend(["." * width for _ in range(line_height)])
        raster_frames.append(current_frame)

    return raster_frames
