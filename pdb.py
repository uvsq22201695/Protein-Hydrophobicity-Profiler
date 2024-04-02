class Header:
    def __init__(self, data: str):
        self.classification = data[10:50].strip()
        self.date = data[50:59].strip()
        self.id = data[62:66].strip()
        self.pdb_link = f"https://www.rcsb.org/structure/{self.id}"

    def __repr__(self):
        return f"Header(classification={self.classification}, date={self.date}, id={self.id})"


class JournalReference:
    def __init__(self, data: str):
        self.pub_name = ""
        self.volume = ""
        self.page = ""
        self.year = ""

        for _ in data.split("\n"):
            self.pub_name += data[19:47].strip()
            self.volume += data[51:55].strip()
            self.page += data[56:61].strip()
            self.year += data[62:66].strip()


class Journal:
    def __init__(self, data: str):
        self.authors = []
        self.title = ""
        self.publisher = ""
        self.international_standard_serial_number = ""
        self.pubmed_id = ""
        self.digital_object_identifier = ""
        reference = ""
        for line in data.split("\n"):
            if line[12:16] == "AUTH":
                if line[-1] == ",":
                    line = line[:-1]
                self.authors.extend(line[19:].strip().split(","))
            elif line[12:16] == "TITL":
                if line[16:18] != "  ":
                    self.title += " "
                self.title += line[19:].strip()
            elif line[12:16] == "REF ":
                reference += line
            elif line[12:16] == "PMID":
                self.pubmed_id += line[19:].strip()
            elif line[12:16] == "DOI ":
                self.digital_object_identifier += line[19:].strip()
            elif line[12:16] == "PUBL":
                self.publisher += line[19:].strip()
            elif line[12:16] == "REFN":
                self.international_standard_serial_number = line[40:].strip()
        self.reference = JournalReference(reference)
        self.pubmed_link = f"https://pubmed.ncbi.nlm.nih.gov/{self.pubmed_id}"


class PDBFile:
    def __init__(self, path):
        self.seqres = {}
        remarks = {}
        self.authors = []
        self.header = None
        journal = ""
        with open(path, 'r') as file:
            line = file.readline().strip()
            while line != "END":
                if line[0:6] == "SEQRES":
                    if line[11] not in self.seqres:
                        self.seqres[line[11]] = []
                    self.seqres[line[11]].extend(line[19:].split())

                elif line[0:6] == "HEADER":
                    self.header = Header(line)

                elif line[0:6] == "REMARK":
                    if line[7:10] not in remarks:
                        remarks[line[7:10]] = ""
                    remarks[line[7:10]] += f"{line[11:].strip()}\n"

                elif line[0:6] == "AUTHOR":
                    self.authors.extend(line[10:].strip().split(","))

                elif line[0:6] == "JRNL  ":
                    journal += line + "\n"

                line = file.readline().strip()

        self.remarks = list(remarks.values())
        self.journal = Journal(journal)
