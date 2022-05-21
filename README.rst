============
pybtexris
============

.. start-badges

|pipline badge| |coverage badge| |black badge| |git3moji badge|

.. |pipline badge| image:: https://github.com/rbturnbull/pybtexris/actions/workflows/coverage.yml/badge.svg
    :target: https://github.com/rbturnbull/pybtexris/actions
    
.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/665c8745fce7077155f99ad694a7e762/raw/coverage-badge.json
    :target: https://rbturnbull.github.io/pybtexris/

.. |git3moji badge| image:: https://img.shields.io/badge/git3moji-%E2%9A%A1%EF%B8%8F%F0%9F%90%9B%F0%9F%93%BA%F0%9F%91%AE%F0%9F%94%A4-fffad8.svg
    :target: https://robinpokorny.github.io/git3moji/

.. end-badges

A pybtex plugin for working with RIS files.

Installation
============

Install pybtexris from PyPI using pip::

    pip install pybtexris

Command-line usage
==================

To convert an RIS file to another format, use the ``pybtex-convert`` command. For example::

    pybtex-convert bibliography.ris bibliography.bib

The extension of the output file must be supported by ``pybtex`` or an associated plugin.

To format an RIS file into a human-readable bibliography, use the pybtex-format command. For example::

    pybtex-format bibliography.ris bibliography.txt

For more information, see `the documentation for pybtex <https://docs.pybtex.org/cmdline.html>`_.

Programmatic usage
==================

RIS files can be formatted into a human-readable bibliography as a string as follows:

.. code-block:: python

    from pybtex import format_from_file
    bibliography_string = format_from_file(
        "path/to/file.ris", 
        style="plain", 
        output_backend="plaintext",
        bib_format="ris",
    )

Multiple RIS files can be formatted in a similar way:

.. code-block:: python

    from pybtex import format_from_files
    bibliography_string = format_from_files(
        ["path/to/file1.ris", "path/to/file2.ris"],
        style="plain", 
        output_backend="plaintext",
        bib_format="ris",
    )

So that RIS files can be combined with bibliography files of other formats (such as BibTeX), 
`pybtexris` also adds `SuffixParser` to the list of plugins which pybtex can use.
The user just needs to give ``suffix`` as the argument to ``bib_format``.

.. code-block:: python

    from pybtex import format_from_files
    result = format_from_files(
        ["path/to/file1.ris", "path/to/file2.bib"],
        style="plain", 
        output_backend="plaintext",
        bib_format="suffix",
    )

The parsers for the files for other formats need to be registered on the ``pybtex.database.input.suffixes``
entry point as discussed pybtex `plugin documentation <https://docs.pybtex.org/api/plugins.html>`_.
To combine with NBIB citation files, please use the `pybtexnbib <https://github.com/rbturnbull/pybtexnbib>`_ plugin.

For more information on programmatic use of pybtex, 
see `the documentation of the Python API of pybtex <https://docs.pybtex.org/api/index.html>`_.

Credit
==================

Robert Turnbull (Melbourne Data Analytics Platform, University of Melbourne)