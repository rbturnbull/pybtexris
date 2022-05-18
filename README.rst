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
    :target: https://rbturnbull.github.io/pybtexris/coverage/

.. |git3moji badge| image:: https://img.shields.io/badge/git3moji-%E2%9A%A1%EF%B8%8F%F0%9F%90%9B%F0%9F%93%BA%F0%9F%91%AE%F0%9F%94%A4-fffad8.svg
    :target: https://robinpokorny.github.io/git3moji/

.. end-badges

A pybtex plugin for inputting RIS files. (Outputting still to come.)

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

Credit
==================

Robert Turnbull (Melbourne Data Analytics Platform, University of Melbourne)