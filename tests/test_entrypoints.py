import pkg_resources
from pybtexris import RISParser

def test_database_input():
    hook = "pybtex.database.input"
    ris_entry_points = []
    for entry_point in pkg_resources.iter_entry_points(hook):
        if entry_point.name == "ris":
            ris_entry_points.append(entry_point)

    assert len(ris_entry_points) == 1
    assert ris_entry_points[0].load() == RISParser

def test_database_input_suffixes():
    hook = "pybtex.database.input.suffixes"
    ris_entry_points = []
    for entry_point in pkg_resources.iter_entry_points(hook):
        if entry_point.name == ".ris":
            ris_entry_points.append(entry_point)

    assert len(ris_entry_points) == 1
    assert ris_entry_points[0].load() == RISParser
