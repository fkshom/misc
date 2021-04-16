from pprint import pprint as pp
import re
import cerberus
import ipaddress


RULE_LABELS = "description,action,source_ip,destination_ip,source_port,destination_port,protocol,comment".split(',')

decimal_type = cerberus.TypeDefinition('decimal', (str,), ())


class AlignedCsvLinter:
    def __init__(self):
        self.errors = []
        self._validators = []

        self._validators.append(self._各カラムについてすべての行の幅が同一である)

    def _error(self, lineno, msg):
        pass

    def _各カラムについてすべての行の幅が同一である(self, data):
        expect_widths = [len(rawheader) for rawheader in data['rawheaders']]

        for rawbodyline in rawbody:
            values = rawbodyline.split(',')



    def validate(self, f):
        text = f.read()

        rawlines = text.split("\n")
        rawheaders = lines[0].split(',')
        rawbody = lines[1:]

        data = dict(
            raw=text,
            rawlines=rawlines,
            rawheaders=rawheaders,
            rawbody=rawbody
        )

        for _validator in self._validators:
            _validator(data)




class RuleValidator(cerberus.Validator):
    def __init__(self):
        super().__init__()
        self.schema = {
            "description": {
                "type": 'string'
            },
            "action": {
                "type": 'string',
                "allowed": ["accept", "drop", ""]
            },
            "source_ip": {
                "type": "string",
                "check_with": "ipaddr"
            },
            "destination_ip": {
                "type": "string",
                "check_with": "ipaddr"
            },
            "source_port": {
                "type": "string",
                "regex": r"^\d+$|^\d+-\d+$"
            },
            "destination_port": {
                "type": "string",
                "regex": r"^\d+$|^\d+-\d+$"
            },
            "protocol": {
                "type": "string",
                "allowed": ["tcp", "ucp", "arp", "any"]
            }
        }
        self.require_all = True
        self.allow_unknown = False
    
    def _check_with_ipaddr(self, field, value):
        if not re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}|ANY", value):
            self._error(field, f"'{field}' must be x.x.x.x/x or ANY. {value}")

        try:
            ipaddress.IPv4Interface(value)
        except:
            self._error(field, f"'{field}' cant be parsed by ipaddr.IPv4Interface. {value}")


class Rule:
    def __init__(self, kwargs):
        self.keys = kwargs.keys()
        for key in self.keys:
            setattr(self, key, kwargs[key])

    def validate(self):
        v = RuleValidator()
        v.validate(self.__dir__)
        if v.errors:
            pp(v.errors)
            raise ""

    def to_dict(self):
        result = {}
        for key in self.keys:
            result[key] = getattr(self, key)
        return result

class RuleStore:
    def __init__(self):
        self.dcname = None
        self.pgname = None
        self.rules = []
        self.errors = []

    def _error(self, line_idx, msg):
        self.errors.append(dict(
            line_idx=line_idx,
            message=msg,
        ))

    def load(self, f):
        lines = f.readlines()
        line_cnt = 0
    
        # read meta area
        while True:
            line = lines.pop(0).rstrip()
            line_cnt += 1
            if line.strip() == '':
                continue

            if re.match(r'---+', line):
                break

            if line.startswith('dcname: '):
                self.dcname = line.split(':', 2)[1].strip()
                continue
            elif line.startswith('pgname: '):
                self.pgname = line.split(':', 2)[1].strip()
            else:
                raise Exception(f'Unknown meta data: {line}')

        # read header
        headers = list(map(lambda col: col.strip(), lines.pop(0).split(',')))
        line_cnt += 1

        # read data
        for line_idx, line in enumerate(lines):
            if line.strip() == '':
                continue
            values = list(map(lambda col: col.strip(), line.strip().split(',')))
            if len(RULE_LABELS) != len(values):
                self._error(line_cnt+line_idx, f"A number of columns is invalid. expect:{len(RULE_LABELS)}, actual:{len(values)}. Anyway continue.")

            self.rules.append(Rule(dict(zip(headers, values))))


    def save(self, f, format=True):
        meta = []
        meta.append(f'dcname: {self.dcname}' + "\n")
        meta.append(f'pgname: {self.pgname}' + "\n")
        meta.append(f'---' + "\n")

        # prepare header
        data = []
        data.append(RULE_LABELS)

        # prepate data
        for rule in self.rules:
            data.append([getattr(rule, key) for key in RULE_LABELS])

        # calculate column size
        data_t = list(zip(*data))
        widths = list(map(lambda val: len(val), [max(cols, key=len) for cols in data_t]))

        data2 = []
        for row_num, row in enumerate(data):
            new_row = []
        
            for val, width, col_name in zip(row, widths, RULE_LABELS):
                val = val.ljust(width)
                if col_name == 'comment':
                    val = val.strip()
                new_row.append(val)
                        
            line = ' , '.join(new_row) + "\n"
            data2.append(line)

        f.writelines(meta + data2)
