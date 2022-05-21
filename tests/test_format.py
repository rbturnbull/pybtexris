from pathlib import Path
from pybtex import format_from_files, format_from_file

shannon1948 = "[1] Claude E. Shannon. A mathematical theory of communication. Bell System Technical Journal, 27:379–423, July 1948.\n"
files_dir = Path(__file__).parent / "files"


def test_format_from_files():
    result = format_from_files(
        [files_dir/"Shannon1948.ris"], 
        style="plain", 
        output_backend="plaintext",
        bib_format="ris",
    )
    assert result == shannon1948


def test_format_from_file():
    result = format_from_file(
        files_dir/"Shannon1948.ris", 
        style="plain", 
        output_backend="plaintext",
        bib_format="ris",
    )
    assert result == shannon1948


def test_format_from_files_suffix():
    result = format_from_files(
        [files_dir/"Shannon1948.ris"], 
        style="plain", 
        output_backend="plaintext",
        bib_format="suffix",
    )
    assert result == shannon1948


def test_format_from_file_suffix():
    result = format_from_file(
        files_dir/"Shannon1948.ris", 
        style="plain", 
        output_backend="plaintext",
        bib_format="suffix",
    )
    assert result == shannon1948


def test_format_from_files_suffix_multi():
    result = format_from_files(
        [files_dir/"Shannon1948.ris", files_dir/"Knuth1986.bib"], 
        style="plain", 
        output_backend="plaintext",
        bib_format="suffix",
    )
    expected = (
        "[1] Donald E. Knuth. The \TeX  Book. Addison-Wesley Professional, 1986.\n"
        "[2] Claude E. Shannon. A mathematical theory of communication. Bell System Technical Journal, 27:379–423, July 1948.\n"
    )
    assert result == expected

