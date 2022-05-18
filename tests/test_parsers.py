from unittest import TestCase
from itertools import zip_longest
from pybtex.database import BibliographyData, Entry, Person
from pybtex.utils import OrderedCaseInsensitiveDict
from pybtexris import RISParser


class _TestParser(RISParser):
    def __init__(self, *args, **kwargs):
        super(_TestParser, self).__init__(*args, **kwargs)
        self.errors = []

    def handle_error(self, error):
        self.errors.append(error)


class ParserTest(object):
    input_string = None
    input_strings = []
    correct_result = None
    parser_options = {}
    errors = []

    def setUp(self):
        if not self.input_strings:
            self.input_strings = [self.input_string]

    def test_parser(self):
        parser = _TestParser(encoding="UTF-8", **self.parser_options)
        for input_string in self.input_strings:
            parser.parse_string(input_string)
        result = parser.data
        correct_result = self.correct_result

        print("Expected result:")
        print(correct_result)
        print("Parsed result:")
        print(result)
        assert (
            result == correct_result
        ), f"Parsed result:\n--------\n{result}\n--------\nis not the same as expected:\n--------\n{correct_result}"
        for error, correct_error in zip_longest(parser.errors, self.errors):
            actual_error = str(error)
            assert actual_error == correct_error


class EmptyDataTest(ParserTest, TestCase):
    input_string = ""
    correct_result = BibliographyData()


class TestSingleJournal(ParserTest, TestCase):
    input_string = """
        TY  - JOUR
        AU  - Shannon, Claude E.
        PY  - 1948
        DA  - July
        TI  - A Mathematical Theory of Communication
        T2  - Bell System Technical Journal
        SP  - 379
        EP  - 423
        VL  - 27
        ER  - 
    """  # taken from https://en.wikipedia.org/wiki/RIS_(file_format)
    correct_result = BibliographyData(
        entries=OrderedCaseInsensitiveDict(
            [
                (
                    'Shannon1948',
                    Entry(
                        'article',
                        fields=[
                            ('type', 'Journal Article'),
                            ('title', 'A Mathematical Theory of Communication'),
                            ('journal', 'Bell System Technical Journal'),
                            ('volume', '27'),
                            ('pages', '379--423'),
                            ('year', '1948'),
                            ('month', 'July'),
                        ],
                        persons=OrderedCaseInsensitiveDict([('author', [Person('Shannon, Claude E.')])]),
                    ),
                )
            ]
        ),
        preamble=[],
    )


class TestMultiEntry(ParserTest, TestCase):
    input_string = """
        TY  - JOUR
        AU  - Shannon, Claude E.
        PY  - 1948
        DA  - July
        TI  - A Mathematical Theory of Communication
        T2  - Bell System Technical Journal
        SP  - 379
        EP  - 423
        VL  - 27
        ER  - 
        TY  - JOUR
        T1  - On computable numbers, with an application to the Entscheidungsproblem
        A1  - Turing, Alan Mathison
        JO  - Proc. of London Mathematical Society
        VL  - 47
        IS  - 1
        SP  - 230
        EP  - 265
        Y1  - 1937
        ER  - 
    """  # taken from https://en.wikipedia.org/wiki/RIS_(file_format)
    correct_result = BibliographyData(
        entries=OrderedCaseInsensitiveDict(
            [
                (
                    'Shannon1948',
                    Entry(
                        'article',
                        fields=[
                            ('type', 'Journal Article'),
                            ('title', 'A Mathematical Theory of Communication'),
                            ('journal', 'Bell System Technical Journal'),
                            ('volume', '27'),
                            ('pages', '379--423'),
                            ('year', '1948'),
                            ('month', 'July'),
                        ],
                        persons=OrderedCaseInsensitiveDict([('author', [Person('Shannon, Claude E.')])]),
                    ),
                ),
                (
                    'Turing1937',
                    Entry(
                        'article',
                        fields=[
                            ('type', 'Journal Article'),
                            ('title', 'On computable numbers, with an application to the Entscheidungsproblem'),
                            ('journal', 'Proc. of London Mathematical Society'),
                            ('number', '1'),
                            ('volume', '47'),
                            ('pages', '230--265'),
                            ('year', '1937'),
                        ],
                        persons=OrderedCaseInsensitiveDict([('author', [Person('Turing, Alan Mathison')])]),
                    ),
                ),
            ]
        ),
        preamble=[],
    )


class TestMultiAuthor(ParserTest, TestCase):
    input_string = """
        TY  - JOUR
        AU  - Seemann, Torsten
        AU  - Lane, Courtney R.
        AU  - Sherry, Norelle L.
        AU  - Duchene, Sebastian
        AU  - Gonçalves da Silva, Anders
        AU  - Caly, Leon
        AU  - Sait, Michelle
        AU  - Ballard, Susan A.
        AU  - Horan, Kristy
        AU  - Schultz, Mark B.
        AU  - Hoang, Tuyet
        AU  - Easton, Marion
        AU  - Dougall, Sally
        AU  - Stinear, Timothy P.
        AU  - Druce, Julian
        AU  - Catton, Mike
        AU  - Sutton, Brett
        AU  - van Diemen, Annaliese
        AU  - Alpren, Charles
        AU  - Williamson, Deborah A.
        AU  - Howden, Benjamin P.
        PY  - 2020
        DA  - 2020/09/01
        TI  - Tracking the COVID-19 pandemic in Australia using genomics
        JO  - Nature Communications
        SP  - 4376
        VL  - 11
        IS  - 1
        AB  - Genomic sequencing has significant potential to inform public health management for SARS-CoV-2. Here we report high-throughput genomics for SARS-CoV-2, sequencing 80% of cases in Victoria, Australia (population 6.24 million) between 6 January and 14 April 2020 (total 1,333 COVID-19 cases). We integrate epidemiological, genomic and phylodynamic data to identify clusters and impact of interventions. The global diversity of SARS-CoV-2 is represented, consistent with multiple importations. Seventy-six distinct genomic clusters were identified, including large clusters associated with social venues, healthcare and cruise ships. Sequencing sequential samples from 98 patients reveals minimal intra-patient SARS-CoV-2 genomic diversity. Phylodynamic modelling indicates a significant reduction in the effective viral reproductive number (Re) from 1.63 to 0.48 after implementing travel restrictions and physical distancing. Our data provide a concrete framework for the use of SARS-CoV-2 genomics in public health responses, including its use to rapidly identify SARS-CoV-2 transmission chains, increasingly important as social restrictions ease globally.
        SN  - 2041-1723
        UR  - https://doi.org/10.1038/s41467-020-18314-x
        DO  - 10.1038/s41467-020-18314-x
        ID  - Seemann2020
        ER  - 
    """  # taken from https://en.wikipedia.org/wiki/RIS_(file_format)
    correct_result = BibliographyData(
        entries=OrderedCaseInsensitiveDict(
            [
                (
                    'Seemann2020',
                    Entry(
                        'article',
                        fields=[
                            ('type', 'Journal Article'),
                            ('title', 'Tracking the COVID-19 pandemic in Australia using genomics'),
                            ('journal', 'Nature Communications'),
                            ('number', '1'),
                            ('doi', '10.1038/s41467-020-18314-x'),
                            ('volume', '11'),
                            ('pages', '4376'),
                            ('url', 'https://doi.org/10.1038/s41467-020-18314-x'),
                            ('year', '2020'),
                            (
                                'abstract',
                                'Genomic sequencing has significant potential to inform public health management for SARS-CoV-2. Here we report high-throughput genomics for SARS-CoV-2, sequencing 80% of cases in Victoria, Australia (population 6.24 million) between 6 January and 14 April 2020 (total 1,333 COVID-19 cases). We integrate epidemiological, genomic and phylodynamic data to identify clusters and impact of interventions. The global diversity of SARS-CoV-2 is represented, consistent with multiple importations. Seventy-six distinct genomic clusters were identified, including large clusters associated with social venues, healthcare and cruise ships. Sequencing sequential samples from 98 patients reveals minimal intra-patient SARS-CoV-2 genomic diversity. Phylodynamic modelling indicates a significant reduction in the effective viral reproductive number (Re) from 1.63 to 0.48 after implementing travel restrictions and physical distancing. Our data provide a concrete framework for the use of SARS-CoV-2 genomics in public health responses, including its use to rapidly identify SARS-CoV-2 transmission chains, increasingly important as social restrictions ease globally.',
                            ),
                            ('issn', '2041-1723'),
                            ('DA', '2020/09/01'),
                        ],
                        persons=OrderedCaseInsensitiveDict(
                            [
                                (
                                    'author',
                                    [
                                        Person('Seemann, Torsten'),
                                        Person('Lane, Courtney R.'),
                                        Person('Sherry, Norelle L.'),
                                        Person('Duchene, Sebastian'),
                                        Person('Gonçalves da Silva, Anders'),
                                        Person('Caly, Leon'),
                                        Person('Sait, Michelle'),
                                        Person('Ballard, Susan A.'),
                                        Person('Horan, Kristy'),
                                        Person('Schultz, Mark B.'),
                                        Person('Hoang, Tuyet'),
                                        Person('Easton, Marion'),
                                        Person('Dougall, Sally'),
                                        Person('Stinear, Timothy P.'),
                                        Person('Druce, Julian'),
                                        Person('Catton, Mike'),
                                        Person('Sutton, Brett'),
                                        Person('van Diemen, Annaliese'),
                                        Person('Alpren, Charles'),
                                        Person('Williamson, Deborah A.'),
                                        Person('Howden, Benjamin P.'),
                                    ],
                                )
                            ]
                        ),
                    ),
                )
            ]
        ),
        preamble=[],
    )


class TestBook(ParserTest, TestCase):
    """
    Testing example from http://refdb.sourceforge.net/examples.html
    """

    input_string = """
        TY  - BOOK
        AU  - Miller,A.
        AU  - Myers,B.
        BT  - My first book about dinosaurs
        SN  - 1-56592-580-7
        PB  - O'Reilly
        CY  - Sebastopol
        PY  - 1999
        T3  - My first book series
        A3  - Smith,K.
        N1  - In my opinion this is not bad, after all
        N2  - Dinosaurs were big animals that ate a lot
        KW  - dinosaurs
        KW  - evolution
        KW  - animals
        UR  - http://www.address.com
        ER  - 
    """
    correct_result = BibliographyData(
        entries=OrderedCaseInsensitiveDict(
            [
                (
                    'Miller1999',
                    Entry(
                        'book',
                        fields=[
                            ('type', 'Book'),
                            ('title', 'My first book about dinosaurs'),
                            ('series', 'My first book series'),
                            ('publisher', "O'Reilly"),
                            ('address', 'Sebastopol'),
                            ('url', 'http://www.address.com'),
                            ('keywords', 'dinosaurs | evolution | animals'),
                            (
                                'note',
                                'In my opinion this is not bad, after all | Dinosaurs were big animals that ate a lot',
                            ),
                            ('year', '1999'),
                            ('isbn', '1-56592-580-7'),
                        ],
                        persons=OrderedCaseInsensitiveDict(
                            [('author', [Person('Miller, A.'), Person('Myers, B.')]), ('editor', [Person('Smith, K.')])]
                        ),
                    ),
                )
            ]
        ),
        preamble=[],
    )
