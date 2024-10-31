from itertools import islice


def generate_color_from_name(name: str) -> str:
    hsh = hash(name)
    hash_str = str(abs(hsh))
    digit_iter = map(int, iter(hash_str))

    MAX_DIGITS = 6  # Hex colors usually only support 6 digits
    n_digit_iter = islice(digit_iter, MAX_DIGITS)

    color_str = "#" + "".join("0123456789abcdef"[n] for n in n_digit_iter)
    return color_str


def generate_color_map_from_list(names: list[str]) -> list[str]:
    colors = []
    for name in names:
        color = generate_color_from_name(name)
        colors.append(color)
    return colors
