import luqum
from luqum.tree import SearchField, FieldGroup, OrOperation, AndOperation, Regex, Word
from luqum.parser import parser
from luqum.pretty import prettify
from pprint import pprint as pp
from luqum.utils import UnknownOperationResolver
import re
from functools import reduce


def search_from_data(rows, tree):
    key = tree.name
    expr = tree.expr  #Word(dog)
    result = []

    for row in rows:
        if type(expr) == Regex:
            if re.match(str(expr)[1:-1], row[key]):
                result.append(row)
        elif type(expr) == Word:
            if str(expr) == row[key]:
                result.append(row)
        else:
            import pdb; pdb.set_trace()
            raise Exception(f"Unknown type: {type(expr)}")

    return result

def merge(rowses, op):
    
    if op == 'or':
        # 和集合を返す
        unioned = reduce(lambda a, b: a + b, rowses)
        return list(map(dict, set(tuple(sorted(sub.items())) for sub in unioned)))
    elif op == 'and':
        # 積集合を返す
        return 

def search(rows, tree):

    # if type(tree) == FieldGroup:
    #     resolver = UnknownOperationResolver(resolve_to=OrOperation)
    #     return search_from_data(rows, tree)
    if type(tree) == SearchField:
        return search_from_data(rows, tree)

    if type(tree) == OrOperation:
        result = [search(rows, child) for child in tree.children]
        return merge(result, op='or')
    elif type(tree) == AndOperation:
        result = [search(rows, child) for child in tree.children]
        return merge(result, op='and')
    import pdb; pdb.set_trace()

def _main(data, query):
    tree = parser.parse(query)
    print(repr(tree))
    print(prettify(tree))

    result = search(data, tree)
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
