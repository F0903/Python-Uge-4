from .parser import CsvRow


def row_to_dict(row: CsvRow) -> dict[str, str]:
    d = {}
    for values in row.get_all_values():
        d[values.get_column_type()] = values.get_value()
    return d
