from pathlib import Path
from pybtex import PybtexEngine


def test_format_plain():
    style="plain"
    output_backend="plaintext"
    engine = PybtexEngine()
    file = Path(__file__).parent/"files/Shannon1948.ris"
    result = engine.format_from_files(
        bib_files_or_filenames=[file], 
        style=style, 
        output_backend=output_backend,
        bib_format="suffix",
    )
    assert result == "[1] Claude E. Shannon. A mathematical theory of communication. Bell System Technical Journal, 27:379–423, July 1948.\n"

