from pprint import pprint as pp

class CsvLinter:
    pass

class RuleValidator:
    pass

class Rule:
    pass

class RuleStore:
    def __init__(self):
        self.meta1 = None
        self.rules = []

    def _map_strip(self, arr):
        return  map(lambda v: v.strip(), arr)

    def load_from_string(self, text):
        lines = text.split("\n")
        while True:
            line = lines.pop(0)
            if line.startswith("meta1: "):
                self.meta1 = line.split(":")[1].strip()
                continue
            if line.startswith("meta2: "):
                self.meta2 = line.split(":")[1].strip()
                continue
            if line.startswith("---"):
                break
            raise Exception(f"Unknown meta line: {line}")

        reader = CsvReader(lines, Rule)
        self.rules = reader.rows
        headers = self._map_strip(lines.pop(0).split(","))

    def save_to_string(self):
        text = ""
        writer = CsvWriter(self.rules, Rule)
        writer