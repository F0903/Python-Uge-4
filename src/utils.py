from typing import Hashable, Iterable


# NOTE: This is not going to be 100% unique for all hash values obviously
def generate_color_from_hash(object: Hashable) -> str:
    hsh = abs(hash(object))
    hex_str = hex(hsh)[2:]  # Skip the 0x prefix
    shortened_hex = hex_str[:6]
    color_str = "#" + shortened_hex
    return color_str


def generate_color_map_from_list(names: Iterable[str]) -> list[str]:
    # Generators not supported for matplotlib colors.
    colors = []
    for name in names:
        color = generate_color_from_hash(name)
        colors.append(color)
    return colors
