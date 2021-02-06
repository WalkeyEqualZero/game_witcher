
import pygame

from typing import Tuple, Optional


def pygame_load_image(start_value: int, count_frames: int, pattern_name: str, size_image: Tuple[int, int],
                      max_number_len: Optional[int] = None ):
    if max_number_len is None:
        max_number_len = len(str(start_value+count_frames))

    return list(map(
        lambda i: pygame.transform.scale(pygame.image.load(
            pattern_name.format(str(i).zfill(max_number_len))), size_image),
        range(start_value, start_value+count_frames)
    ))
