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
        assert result == correct_result, f"Parsed result:\n--------\n{result}\n--------\nis not the same as expected:\n--------\n{correct_result}"
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
  entries=OrderedCaseInsensitiveDict([
    ('Shannon1948', Entry('article',
      fields=[
        ('type', 'Journal Article'), 
        ('title', 'A Mathematical Theory of Communication'), 
        ('journal', 'Bell System Technical Journal'), 
        ('volume', '27'), 
        ('pages', '379--423'), 
        ('year', '1948'), 
        ('month', 'July')],
      persons=OrderedCaseInsensitiveDict([('author', [Person('Shannon, Claude E.')])])))]),

  preamble=[])


class TestMulti(ParserTest, TestCase):
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
  entries=OrderedCaseInsensitiveDict([
    ('Shannon1948', Entry('article',
      fields=[
        ('type', 'Journal Article'), 
        ('title', 'A Mathematical Theory of Communication'), 
        ('journal', 'Bell System Technical Journal'), 
        ('volume', '27'), 
        ('pages', '379--423'), 
        ('year', '1948'), 
        ('month', 'July')],
      persons=OrderedCaseInsensitiveDict([('author', [Person('Shannon, Claude E.')])]))), 
    ('Turing1937', Entry('article',
      fields=[
        ('type', 'Journal Article'), 
        ('title', 'On computable numbers, with an application to the Entscheidungsproblem'), 
        ('journal', 'Proc. of London Mathematical Society'), ('number', '1'), 
        ('volume', '47'), 
        ('pages', '230--265'), 
        ('year', '1937')],
      persons=OrderedCaseInsensitiveDict([('author', [Person('Turing, Alan Mathison')])])))]),

  preamble=[])

