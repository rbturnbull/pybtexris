import re
from pathlib import Path
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

        print(self.ris_type_to_bibtex)

    def parse_stream(self, stream):
        text = stream.read()
        return self.parse_string(text)

# """
# TY  - JOUR
# AU  - Shannon, Claude E.
# PY  - 1948
# DA  - July
# TI  - A Mathematical Theory of Communication
# T2  - Bell System Technical Journal
# SP  - 379
# EP  - 423
# VL  - 27
# ER  - 
# """
    def process_entry(self, entry_text):
        """
        https://github.com/aurimasv/translators/wiki/RIS-Tag-Map
        """
        # Read entry into dictionary
        ris_dict = dict()
        for line in entry_text.split('\n'):
            m = re.match(r"^([A-Z]{2})\s*-\s*(.*)$", line.strip())
            if not m:
                continue

            code = m.group(1)
            value = m.group(2)

            if code == "ER":
                continue
            
            ris_dict[code] = value
        
        # Read type of entry
        ris_type = ris_dict.pop("TY", "GEN")
        ris_description = None
        if ris_type in self.ris_type_description.values():
            index = self.ris_type_description.values().index(ris_type)
            ris_description = ris_type
            ris_type = self.ris_type_description.keys()[index]
            
        ris_type = ris_type.upper()
        if not ris_description:
            ris_description = self.ris_type_description[ris_type]

        # Create Entry object
        bibtex_type = self.ris_type_to_bibtex.get(ris_type, "misc")
        entry = Entry(bibtex_type)
        entry.fields["type"] = ris_description
        
        # Read People
        def add_person(code, role):
            name = ris_dict.pop(code, None)
            if name:
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
        def add_field(code, bibtex_field):
            value = ris_dict.pop(code, None)
            if value:
                entry.fields[bibtex_field] = value

        add_field("TI", "title")
        add_field("DO", "doi")
        add_field("VL", "volume")
        add_field("SP", "pages")
        add_field("UR", "URL")
        add_field("PY", "year")

        # Check if DA field could be a month
        da = ris_dict.get("DA", None)
        if da:
            digital_month = da.isdigit() and (1 <= int(da) <= 12)
            text_month = da[:3].lower() in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
            if digital_month or text_month:
                entry.fields["month"] = da
                ris_dict.pop("DA")
                
        value = ris_dict.pop("EP", None)
        if value:
            if "pages" in entry.fields:
                entry.fields["pages"] += f"--{value}"
            else:
                entry.fields["pages"] = value


        for code, value in ris_dict.items():
            if code == "TY":
                continue

            entry.fields[code] = value

        print(entry)

        people = list(*entry.persons.values())
        if people:
            first_author = people[0]
            entry_key = "-".join(first_author.last_names).replace(" ", ".")
        elif "title" in entry.fields:
            entry_key = entry.fields["title"].replace(" ", ".")[:15]
        else:
            entry_key = "Unknown"

        if "year" in entry.fields:
            entry_key += entry.fields["year"]

        return entry_key,entry

            # if key_lower in Person.valid_roles:
            #     for names in value:
            #         bib_entry.add_person(Person(**names), key)

    def parse_string(self, text):
        self.unnamed_entry_counter = 1
        self.command_start = 0

        entry_texts = re.split(r"ER\s+-", text)
        entries = (self.process_entry(t) for t in entry_texts if t.strip())
        self.data.add_entries(entries)
        return self.data



