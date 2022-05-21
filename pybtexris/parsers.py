import re
from collections import defaultdict
from pathlib import Path
from pybtex import database
from pybtex.database.input import BaseParser
from pybtex.database import BibliographyData, Entry, Person
from pybtex.utils import OrderedCaseInsensitiveDict
import csv

data_dir = Path(__file__).parent/"data"

class RISParser(BaseParser):
    """
    Parser for RIS files.
    """
    default_suffix = '.ris'
    unicode_io = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ris_type_to_bibtex = {}
        self.ris_type_description = {}

        with open(data_dir/"types.csv") as f:
            reader = csv.reader(f, delimiter=',')
            
            #skip the header
            next(reader, None)
            for row in reader:
                ris_types = row[0]
                description = row[1]
                bibtex_type = row[2]

                for ris_type in ris_types.split(", "):
                    self.ris_type_to_bibtex[ris_type] = bibtex_type
                    self.ris_type_description[ris_type] = description

    def parse_stream(self, stream):
        text = stream.read()
        return self.parse_string(text)

    def process_entry(self, entry_text):
        """
        https://github.com/aurimasv/translators/wiki/RIS-Tag-Map
        """
        # Read entry into dictionary
        ris_dict = defaultdict(list)
        for line in entry_text.split('\n'):
            m = re.match(r"^([A-Z0-9]{2})\s*-\s*(.*)$", line.strip())
            if not m:
                continue

            code = m.group(1)
            value = m.group(2)
            
            ris_dict[code].append(value)
        
        # Read type of entry
        ris_type = ris_dict.pop("TY", ["GEN"])
        ris_type = ris_type[0]
        ris_description = None
        if ris_type in self.ris_type_description.values():
            index = list(self.ris_type_description.values()).index(ris_type)
            ris_description = ris_type
            ris_type = list(self.ris_type_description.keys())[index]
            
        ris_type = ris_type.upper()
        if not ris_description:
            ris_description = self.ris_type_description[ris_type]

        # Create Entry object
        bibtex_type = self.ris_type_to_bibtex.get(ris_type, "misc")
        entry = Entry(bibtex_type)
        entry.fields["type"] = ris_description
        
        # Read People
        def add_person(code, role):
            names = ris_dict.pop(code, [])
            for name in names:
                person = Person(name)
                entry.add_person(person, role)

        add_person("AU", "author")
        add_person("A1", "author")
        editor_role = ["ANCIENT", "BLOG", "BOOK", "CHAP", "CLSWK", "COMP", "DATA", "CPAPER", "CONF", "DICT", "EDBOOK", "EBOOK", "ECHAP", "ENCYC", "MAP", "MUSIC", "MULTI", "RPRT", "SER", "UNPB", "ELEC"]
        add_person("A2", "editor" if ris_type in editor_role else "author")
        editor_role += ["ADVS", "SLIDE", "SOUND", "VIDEO"]
        add_person("A3", "editor" if ris_type in editor_role else "author")
        add_person("A4", "editor" if ris_type in editor_role else "author")        
        add_person("ED", "editor")        

        # Read Other Fields
        def add_field(code, bibtex_field, delimiter=", "):
            values = ris_dict.pop(code, [])
            for value in values:
                if bibtex_field in entry.fields:
                    entry.fields[bibtex_field] += f"{delimiter}{value}"
                else:
                    entry.fields[bibtex_field] = value

        add_field("TI", "title")
        if "title" not in entry.fields:
            add_field("T1", "title")
        add_field("JO", "journal")

        bibtex_t2 = None
        if ris_type in ["ABST","INPR","JFULL","JOUR", "EJOUR"]:
            bibtex_t2 = "journal"
        elif ris_type in ["ANCIENT","CHAP", "ECHAP"]:
            bibtex_t2 = "booktitle"
        elif ris_type in ["BOOK","CTLG", "CLSWK", "COMP", "DATA", "MPCT", "MAP", "MULTI", "RPRT", "UNPB", "ELEC"]:
            bibtex_t2 = "series"
        if bibtex_t2:
            add_field("T2", bibtex_t2)
            
        bibtex_bt = bibtex_t2
        if ris_type == "BOOK":
            bibtex_bt = "title"
        if bibtex_bt:
            add_field("BT", bibtex_bt)

        bibtex_t3 = None
        if ris_type in ["BOOK","CTLG", "CLSWK", "COMP", "DATA", "MPCT", "MAP", "MULTI", "RPRT", "UNPB", "ELEC", "ADVS", "SLIDE", "SOUND", "VIDEO", "CHAP", "CONF", "DATA", "EBOOK", "ECHAP", "GOVDOC", "MUSIC", "SER"]:
            bibtex_t3 = "series"
        if bibtex_t3:
            add_field("T3", bibtex_t3)
            
        add_field("PB", "publisher")
        add_field("CY", "address")
        add_field("IS", "number")
        add_field("DO", "doi")
        add_field("VL", "volume")
        add_field("SP", "pages")
        add_field("UR", "url")
        add_field("KW", "keywords", delimiter=" | ")
        add_field("N1", "note", delimiter=" | ")
        add_field("N2", "note", delimiter=" | ")
        add_field("PY", "year")
        add_field("AB", "abstract")
        if "year" not in entry.fields:
            add_field("Y1", "year")

        # Read ISBN or ISSN
        serial_numbers = ris_dict.pop("SN", [])
        for serial_number in serial_numbers:
            sn_digits = re.sub(r"\D","", serial_number)
            sn_field = "issn" if len(sn_digits) == 8 else "isbn"
            entry.fields[sn_field] = serial_number

        entry_key = ris_dict.pop("ID", [None])
        entry_key = entry_key[0]

        # Check if DA field could be a month
        dates = ris_dict.get("DA", [])
        for date in dates:
            digital_month = date.isdigit() and (1 <= int(date) <= 12)
            text_month = date[:3].lower() in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
            if digital_month or text_month:
                entry.fields["month"] = date
                ris_dict.pop("DA")
                
        end_pages = ris_dict.pop("EP", [])
        for end_page in end_pages:
            if "pages" in entry.fields:
                entry.fields["pages"] += f"--{end_page}"
            else:
                entry.fields["pages"] = end_page

        # Add the remaining fields with the RIS code as the field name
        ris_dict.pop("ER", None)
        for code, values in ris_dict.items():
            entry.fields[code] = ", ".join(values)

        
        if not entry_key:
            people = [x[0] for x in entry.persons.values()]
            if people:
                first_author = people[0]
                entry_key = "-".join(first_author.last_names).replace(" ", ".")
            elif "title" in entry.fields:
                TRUNCATE_TITLE = 20
                entry_key = entry.fields["title"].replace(" ", ".")[:TRUNCATE_TITLE]
            else:
                entry_key = "Unknown"

            if "year" in entry.fields:
                entry_key += entry.fields["year"]

        return entry_key,entry

    def parse_string(self, text):
        self.unnamed_entry_counter = 1
        self.command_start = 0

        entry_texts = re.split(r"ER\s+-", text)
        entries = (self.process_entry(t) for t in entry_texts if t.strip())
        self.data.add_entries(entries)
        return self.data


class SuffixParser(BaseParser):
    """
    A parser which chooses the parser based on the suffix of each file given to it.
    """
    def parse_file(self, filename, file_suffix=None):
        if file_suffix is not None:
            filename = str(filename) + file_suffix

        file_data = database.parse_file(filename)
        self.data.add_entries(file_data.entries.items())
        if file_data._preamble:
            self.data._preamble.extend(file_data._preamble)

        return file_data

