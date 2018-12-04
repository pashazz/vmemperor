import graphene
from graphql.language import ast

MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
class Long(graphene.Scalar):
    '''
    Long scalar represents integer value between JS MIN_SAFE_INTEGER and MAX_SAFE_INTEGER
    Not standartized
    '''

    @staticmethod
    def coerce_long(value):
        try:
            num = int(value)
        except ValueError:
            try:
                num = int(float(value))
            except ValueError:
                return None
        if MIN_SAFE_INTEGER <= num <= MAX_SAFE_INTEGER:
            return num

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, (ast.FloatValue, ast.IntValue)):
            return int(ast.value)

    serialize = coerce_long
    parse_value = coerce_long