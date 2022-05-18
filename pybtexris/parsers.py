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

    def process_entry(self, entry_text):
        """
        https://github.com/aurimasv/translators/wiki/RIS-Tag-Map
        """
        # Read entry into dictionary
        ris_dict = dict()
        for line in entry_text.split('\n'):
            m = re.match(r"^([A-Z0-9]{2})\s*-\s*(.*)$", line.strip())
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
                if bibtex_field in entry.fields:
                    entry.fields[bibtex_field] += f"| value"
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
            
        add_field("IS", "number")
        add_field("DO", "doi")
        add_field("VL", "volume")
        add_field("SP", "pages")
        add_field("UR", "URL")
        add_field("PY", "year")
        add_field("AB", "abstract")
        if "year" not in entry.fields:
            add_field("Y1", "year")

        # Read ISBN or ISSN
        sn = ris_dict.pop("SN", None)
        if sn:
            sn_digits = re.sub(r"\D","", sn)
            sn_field = "issn" if len(sn_digits) == 8 else "isbn"
            entry.fields[sn_field] = sn

        entry_key = ris_dict.pop("ID", None)

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

        if not entry_key:
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

    def parse_string(self, text):
        self.unnamed_entry_counter = 1
        self.command_start = 0

        entry_texts = re.split(r"ER\s+-", text)
        entries = (self.process_entry(t) for t in entry_texts if t.strip())
        self.data.add_entries(entries)
        return self.data



