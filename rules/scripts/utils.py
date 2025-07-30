import re
import warnings
from custom_types import *
from typing import List, Optional, Union
from pathlib import Path

FilePath = Union[str, Path]

def read_file_contents(file_path: FilePath) -> List[str]:
    with open(file_path) as f:
        content = f.readlines()

    return [l.strip() for l in content]


def get_value_from_line(line: str, search_string: str) -> float:
    # line = line.strip()
    # if search_string in line:
    #     _, value = line.rsplit(" ", 1)
    #     return float(value)

    # raise ValueError(
    #     f"The given line '{line}' does not contain the search string '{search_string}'."
    # )
    """
    Extract the first float number after the search_string in the line.
    """
    if search_string not in line:
        raise ValueError(f"Search string '{search_string}' not found in line: {line}")
    
    # Lấy phần sau dấu ':' hoặc search_string
    value_part = line.split(search_string)[-1]

    # Tìm số thực đầu tiên (có thể âm)
    match = re.search(r"-?\d+\.\d+", value_part)
    if match:
        return float(match.group())

    raise ValueError(f"Không tìm được số thực sau '{search_string}' trong dòng: {line}")


# def get_single_value_from_file(input_file: FilePath, search_string: str) -> float:
#     with open(input_file) as f:
#         lines = f.readlines()

#     for l in lines:
#         if search_string in l:
#             return get_value_from_line(l, search_string)

#     raise ValueError(
#         f"The given input file {input_file} does not contain the search string '{search_string}'."
#     )

def get_single_value_from_file(input_file: FilePath, search_string: str) -> Optional[float]:
    with open(input_file) as f:
        for line in f:
            if search_string in line:
                return get_value_from_line(line, search_string)
    warnings.warn(f"[WARNING] {input_file} không chứa '{search_string}'")
    return None


def get_multiple_values_from_file(
    input_file: FilePath, search_string: str
) -> List[float]:
    with open(input_file) as f:
        lines = f.readlines()

    values = []
    for l in lines:
        if search_string in l:
            values.append(get_value_from_line(l, search_string))

    if len(values) == 0:
        raise ValueError(
            f"The given input file {input_file} does not contain the search string '{search_string}'."
        )

    return values
