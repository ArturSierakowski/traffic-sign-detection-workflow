from enum import Enum


class PictureType(str, Enum):
    flat = "flat"
    equirectangular = "equirectangular"  # 360° picture
