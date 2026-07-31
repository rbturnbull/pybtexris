from importlib.metadata import entry_points

from pybtexris import RISParser


def get_entry_points(group):
    discovered = entry_points()
    if hasattr(discovered, "select"):
        return discovered.select(group=group)
    return discovered.get(group, ())


def test_database_input():
    hook = "pybtex.database.input"
    ris_entry_points = [entry_point for entry_point in get_entry_points(hook) if entry_point.name == "ris"]

    assert len(ris_entry_points) == 1
    assert ris_entry_points[0].load() == RISParser


def test_database_input_suffixes():
    hook = "pybtex.database.input.suffixes"
    ris_entry_points = [entry_point for entry_point in get_entry_points(hook) if entry_point.name == ".ris"]

    assert len(ris_entry_points) == 1
    assert ris_entry_points[0].load() == RISParser
