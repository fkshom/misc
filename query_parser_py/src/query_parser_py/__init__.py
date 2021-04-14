import luqum
from luqum.tree import SearchField, FieldGroup, OrOperation, AndOperation, Regex, Word, Group, Phrase
from luqum.parser import parser
from luqum.pretty import prettify
from pprint import pprint as pp
from luqum.utils import UnknownOperationResolver
import re
from functools import reduce
import fnmatch

def is_matched(elem, tree):
    key = tree.name
    expr = tree.expr
    
    def inner_matched(elem, expr):
        if type(expr) == Regex:
            import pdb; pdb.set_trace()

            if re.match(str(expr)[1:-1], elem[key]):
                return True
        elif type(expr) == Word:
            if expr.has_wildcard():
                if fnmatch.fnmatch(elem[key], str(expr)):
                    return True
            else:
                if str(expr) == elem[key]:
                    return True
        elif type(expr) == Phrase:
            if expr.has_wildcard():
                if fnmatch.fnmatch(elem[key], str(expr)[1:-1]):
                    return True
            else:
                if str(expr)[1:-1] == elem[key]:
                    return True
        else:
            raise Exception(f"Unknown type: {type(expr)}")
        return False

    if type(expr) in [Regex, Word, Phrase]:
        return inner_matched(elem, expr)
    elif type(expr) == FieldGroup:
        if type(expr.children[0]) == OrOperation:
            result = [inner_matched(elem, child) for child in expr.children[0].children]
            return any(result)
        elif type(expr.children[0]) == AndOperation:
            result = [inner_matched(elem, child) for child in expr.children[0].children]
            return all(result)
        else:
            import pdb; pdb.set_trace()
            raise Exception(f"Unknown type: {type(expr)}")
    else:
        import pdb; pdb.set_trace()
        raise Exception(f"Unknown type: {type(expr)}")

    return False

def match(elem, tree):

    # if type(tree) == FieldGroup:
    #     resolver = UnknownOperationResolver(resolve_to=OrOperation)
    #     return search_from_data(rows, tree)
    if type(tree) == SearchField:
        return is_matched(elem, tree)

    if type(tree) == OrOperation:
        results = [match(elem, child) for child in tree.children]
        return any(results)
    elif type(tree) == AndOperation:
        results = [match(elem, child) for child in tree.children]
        return all(results)
    elif type(tree) == Group:
        if len(tree.children) != 1:
            raise Exception(f"Group instance has elements more one. {tree}")
        return match(elem, tree.children[0])

    import pdb; pdb.set_trace()

def _main(data, query):
    tree = parser.parse(query)
    pp(tree)

    result = []
    for row in data:
        tmp = match(row, tree)
        if tmp:
            result.append(row)
    return result


class SearcherBase():
    def __init__(self, data):
        self.rows = data

    def match(self, tree):
        pass

    def search(self, query):
        tree = parser.parse(query)
        result = []
        for row in self.rows:
            tmp = self.match(row, tree)
            if tmp:
                result.append(row)
        return result

class Searcher(SearcherBase):
    default_operator = 'and'
    default_operator_in_search_field = 'or'

    def matchWord(elem, tree, negative=False, has_wildcard=False):
        return True

    def matchRegex(elem, tree, negative=False, has_wildcard=False):
        return True

    def matchPhrase(elem, tree, negative=False, has_wildcard=False):
        return True

def _main2(data, query):
    s = Searcher(data)
    reslt = s.search(query)
    return result

def main():
    data = [
        dict(title="foo bar", body="quick fox"),
        dict(title="fox", body="unko1"),
        dict(title="unko2", body="unko2"),
        dict(title="dog", body="unko3")
    ]

    #query = '(title:"foo bar" AND body:"quick fox") OR title:fox OR NOT title:dog'
    query = 'title:dog'
    query = "title:/dog/ OR title:fox OR title:cat*"
    result = _main(data, query)
    pp(result)

if __name__ == '__main__':
    main()
