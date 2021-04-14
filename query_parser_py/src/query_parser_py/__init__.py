import luqum
from luqum.tree import SearchField, FieldGroup, OrOperation, AndOperation, Regex, Word, Group, Phrase, Not, UnknownOperation
from luqum.parser import parser
from luqum.pretty import prettify
from pprint import pprint as pp
from luqum.utils import UnknownOperationResolver
import re
from functools import reduce
import fnmatch


class MatcherBase():
    def __init__(self, query):
        self._query = query
        self._tree = parser.parse(query)

    def matchWord(self, elem, key, expr, has_wildcard):
        if has_wildcard:
            if fnmatch.fnmatch(elem.get(key, ""), expr):
                return True
        else:
            if expr == elem.get(key, ""):
                return True
        return False

    def matchRegex(self, elem, key, expr, has_wildcard):
        return re.match(expr, elem.get(key, ""))

    def matchPhrase(self, elem, key, expr, has_wildcard):
        if has_wildcard:
            if fnmatch.fnmatch(elem.get(key, ""), expr):
                return True
        else:
            if expr == elem.get(key, ""):
                return True

    def check_match(self, item, tree, negative=False):
        key = tree.name
        expr = tree.expr

        def inner_matched(elem, expr, negative=False):
            if type(expr) == Word:
                if self.matchWord(elem, key, str(expr), expr.has_wildcard()):
                    return True ^ negative
            elif type(expr) == Regex:
                if self.matchRegex(elem, key, str(expr)[1:-1], expr.has_wildcard()):
                    return True ^ negative
            elif type(expr) == Phrase:
                if self.matchPhrase(elem, key, str(expr)[1:-1], expr.has_wildcard()):
                    return True ^ negative
            else:
                raise Exception(f"Unknown type: {type(expr)}")
            return False ^ negative

        if type(expr) in [Regex, Word, Phrase]:
            return inner_matched(item, expr, negative=negative)
        elif type(expr) == FieldGroup:
            if type(expr.children[0]) == OrOperation or \
              (type(expr.children[0]) == UnknownOperation and self.default_operator_in_search_field == 'or'):
                result = [inner_matched(item, child, negative=negative) for child in expr.children[0].children]
                if negative:
                    return all(result)
                else:
                    return any(result)
            elif type(expr.children[0]) == AndOperation or \
                (type(expr.children[0]) == UnknownOperation and self.default_operator_in_search_field == 'and'):
                result = [inner_matched(item, child, negative=negative) for child in expr.children[0].children]
                if negative:
                    return any(result)
                else:
                    return all(result)
            else:
                import pdb; pdb.set_trace()
                raise Exception(f"Unknown type: {type(expr)}")
        else:
            import pdb; pdb.set_trace()
            raise Exception(f"Unknown type: {type(expr)}")

        return False

    def _match(self, item, tree, negative=False):
        if type(tree) == SearchField:
            return self.check_match(item, tree, negative=negative)

        if type(tree) == OrOperation or \
            (type(tree) == UnknownOperation and self.default_operator == 'or'):
            results = [self._match(item, child, negative=negative) for child in tree.children]
            if negative:
                return all(results)
            else:
                return any(results)
        elif type(tree) == AndOperation or \
            (type(tree) == UnknownOperation and self.default_operator == 'and'):
            results = [self._match(item, child, negative=negative) for child in tree.children]
            if negative:
                return any(results)
            else:
                return all(results)
        elif type(tree) == Group:
            if len(tree.children) != 1:
                raise Exception(f"Group instance has elements more one. {tree}")
            return self._match(item, tree.children[0], negative=negative)
        elif type(tree) == Not:
            if len(tree.children) != 1:
                raise Exception(f"Group instance has elements more one. {tree}")
            return self._match(item, tree.children[0], negative=(not negative))
        else:
            raise Exception(f"Unknown type: {type(tree)}")

    def is_matched(self, item):
        return self._match(item, self._tree)
        

class Matcher(MatcherBase):
    default_operator = 'and'
    default_operator_in_search_field = 'or'

    # def matchWord(self, elem, tree, negative, has_wildcard):
    #     return True

    # def matchRegex(self, elem, tree, negative, has_wildcard):
    #     return True

    # def matchPhrase(self, elem, tree, negative, has_wildcard):
    #     return True


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
