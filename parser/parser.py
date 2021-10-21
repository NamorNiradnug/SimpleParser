from __future__ import annotations

from copy import deepcopy
from typing import Iterable, Final, Set, Callable, List, Union, Tuple, Any, Literal, Optional
from regex import regex
from math import inf


class ParseError(ValueError):
    pass


class Operator:
    """Simple structure for storing operators data."""

    def __init__(self, name: str, operator_type: Literal[1, 2], func: Callable[[Any], Any] | Callable[[Any, Any], Any],
                 signs: Iterable[str] = tuple(),
                 priority: int = -1):
        """
        :param name: name of operator. Can be used in boolean functions expressions, but only explicitly separated by spaces from other.
        :param operator_type: unary (1) or binary (2)
        :param func: function which is realisation of this boolean operator in python.
        :param signs: operator denotations.
        :param priority: operator priority (more positive value is less priority). -1 is lowest priority.
        """
        self.func = func
        if operator_type not in {1, 2}:
            raise ValueError(f"Operator type must be 1 (unary) or 2 (binary), not {operator_type}")
        self.type = operator_type
        self.name = name
        self.signs = tuple(signs)
        if priority < -1:
            raise ValueError("Operator priority must be non-negative integer or -1.")
        if priority == -1:
            priority = inf
        self.priority = priority

    def __repr__(self):
        return self.name


class ConstantType:
    """Structure for storing different types of constant tokens such numbers of booleans."""

    def __init__(self, regexp: str, to_value: Callable[[str], Any]):
        self.regexp = regexp
        self.to_value = to_value


# tokens structs
class VariableToken:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"VariableToken({self.name})"


class BraceToken:
    OPEN = 1
    CLOSE = -1

    def __init__(self, which: Union[BraceToken.OPEN | BraceToken.CLOSE]):
        self.which = which

    def __repr__(self):
        return "BraceToken(BraceToken.OPEN)" if self.which == BraceToken.OPEN else "BraceToken(BraceToken.CLOSE)"


class OperatorToken:
    def __init__(self, operator: Operator):
        self.operator = operator

    def __repr__(self):
        return f"OperatorToken({self.operator})"


class ConstantToken:
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return f"ConstantToken({self.value})"


Token: Final = Union[VariableToken, BraceToken, OperatorToken, ConstantToken]


class ParsedExpression:
    def __init__(self, operations: List[Tuple[Operator, Tuple[int | VariableToken]]],
                 precalculated: Optional[List[Any]]):
        """
        :param operations: each tuple is pair of operator and its arguments which are variable names or indexes of one of previous calculations which result uses as argument
        """
        self.operations = operations
        if precalculated is None:
            precalculated = []
        self.precalculated = precalculated

    def __call__(self, **kwargs):
        calc_stack = deepcopy(self.precalculated)
        for operation in self.operations:
            calc_stack.append(operation[0].func(
                *(calc_stack[param] if isinstance(param, int) else kwargs[param.name] for param in operation[1])))
        return calc_stack[-1]


class Parser:
    def __init__(self, operators: Iterable[Operator], constants: Iterable[ConstantType] = []):
        self.operators = set(operators)
        self.constants = constants
        self.operators_signs = {}
        for operator in operators:
            self.operators_signs |= {sign: operator for sign in operator.signs}
        self.operators_names = {operator.name: operator for operator in operators}

    def to_token(self, token: str) -> Token:
        if token == "(":
            return BraceToken(BraceToken.OPEN)
        if token == ")":
            return BraceToken(BraceToken.CLOSE)
        if token in self.operators_names:
            return OperatorToken(self.operators_names[token])
        if token in self.operators_signs:
            return OperatorToken(self.operators_signs[token])
        if token:
            for const_type in self.constants:
                if regex.match(const_type.regexp, token):
                    return ConstantToken(const_type.to_value(token))
            return VariableToken(token)

    def split(self, s: str) -> List[Token]:
        """Lexical analysis of expression, splits boolean expression to tokens."""
        ret: List[Token] = []

        def append_token(t: str):
            if not t.isspace() and t:
                ret.append(self.to_token(t))

        current_token: str = ""
        for c in s + " ":
            if c.isspace() or c in "()":
                append_token(current_token)
                append_token(c)
                current_token = ""
            elif current_token in self.operators_signs:
                if current_token + c in self.operators_signs:
                    current_token += c
                else:
                    append_token(current_token)
                    current_token = c
            else:
                current_token += c
                for sign in self.operators_signs:
                    if current_token[-len(sign):] == sign:
                        append_token(current_token[:-len(sign)])
                        current_token = sign
                        break
        return ret

    def parse(self, s: str) -> ParsedExpression:
        """Parse expression."""
        tokens = self.split(s)
        open_braces: int = 0
        close_braces: int = 0
        operators_data: List[Tuple[int, int]] = []
        # each pair in `operators_data` is number of open braces before operator considering closed braces
        # and position of operator in tokens without braces
        variables: Set[VariableToken] = set()
        precalculated = []
        tokens_without_braces: List[OperatorToken | VariableToken | int] = []
        """Set of names of all variables."""
        for i in range(len(tokens)):
            if isinstance(tokens[i], BraceToken):
                if tokens[i].which == BraceToken.OPEN:
                    open_braces += 1
                else:
                    close_braces += 1
                    if open_braces - close_braces < 0:
                        raise ParseError("Cannot parse the expression: close brace without open.")
            elif isinstance(tokens[i], OperatorToken):
                operators_data.append((open_braces - close_braces, i - (open_braces + close_braces)))
                tokens_without_braces.append(tokens[i])
            elif isinstance(tokens[i], VariableToken):
                variables.add(tokens[i])
                tokens_without_braces.append(tokens[i])
            elif isinstance(tokens[i], ConstantToken):
                precalculated.append(tokens[i].value)
                tokens_without_braces.append(len(precalculated) - 1)
        if open_braces - close_braces:
            raise ParseError("Cannot parse the expression: not all open braces have pair close brace.")

        calculation_order = [operator_data[1] for operator_data in
                             sorted(operators_data,
                                    key=lambda data:
                                    # data[0] is number of open braces: as more open braces as much priority
                                    # the second number is operator priority
                                    # data[1] is position of operator in tokens without braces list
                                    (data[0], -tokens_without_braces[data[1]].operator.priority, -data[1]),
                                    reverse=True)]
        operators_with_arguments: List[Tuple[Operator, Tuple[int, ] | Tuple[int, int]]] = []

        def update_last_calc(operator_index: int, side: Literal[-1, 1], calculation_index: int):
            old_value = tokens_without_braces[operator_index + side]
            i = operator_index + side
            while i < len(tokens_without_braces) and tokens_without_braces[i] == old_value:
                tokens_without_braces[i] = calculation_index
                i += side

        for calculation_index in range(len(calculation_order)):
            operator_index = calculation_order[calculation_index]
            operator = tokens_without_braces[operator_index].operator
            if operator.type == 1:
                operators_with_arguments.append((operator, (tokens_without_braces[operator_index + 1],)))
                update_last_calc(operator_index, 1, calculation_index + len(precalculated))
            elif operator.type == 2:
                operators_with_arguments.append(
                    (operator, (tokens_without_braces[operator_index - 1], tokens_without_braces[operator_index + 1])))
                update_last_calc(operator_index, 1, calculation_index + len(precalculated))
                update_last_calc(operator_index, -1, calculation_index + len(precalculated))
            tokens_without_braces[operator_index] = calculation_index + len(precalculated)
        return ParsedExpression(operators_with_arguments, precalculated)


class Defaults:
    pow = Operator("pow", 2, lambda a, p: a ** p, ("^", "**"), 0)
    div = Operator("div", 2, lambda a, b: a / b, ("/",), 1)
    mod = Operator("mod", 2, lambda a, b: a % b, ("%",), 1)
    mul = Operator("mul", 2, lambda a, b: a * b, ("*",), 1)
    plus = Operator("plus", 2, lambda a, b: a + b, ("+",), 2)
    minus = Operator("minus", 2, lambda a, b: a - b, ("-",), 2)

    eq = Operator("eq", 2, lambda a, b: a == b, ("==", "\u21D4", "\u2261", "\u27F7"), 3)
    not_eq = Operator("not_eq", 2, lambda a, b: a != b, ("!=", "<>"), 3)
    great_eq = Operator("great_eq", 2, lambda a, b: a >= b, (">=",), 3)
    great = Operator("great", 2, lambda a, b: a > b, (">",), 3)
    less_eq = Operator("less_eq", 2, lambda a, b: a <= b, ("<=",), 3)
    less = Operator("less", 2, lambda a, b: a < b, ("<",), 3)

    not_op = Operator("not", 1, lambda a: not a, ("!", "~", "\u00AC"), 4)
    and_op = Operator("and", 2, lambda a, b: a and b, ("&&", "\u22C0"), 5)
    or_op = Operator("or", 2, lambda a, b: a or b, ("||", "\u22C1"), 6)
    impl = Operator("impl", 2, lambda a, b: not a or b, ("->", "\u21D2", "\u2192"), 7)

    integers_decimal = ConstantType(r"[0-9]{1,}$", int)
    integers_binary = ConstantType(r"0b[0-1]{1,}$", lambda s: int(s, 2))
    integers_hex = ConstantType(r"0x[0-F]{1,}$", lambda s: int(s, 16))

    float_point = ConstantType(r"([0-9]{0,}\.?[0-9]{1,}|[0-9]{1,}\.)((e|E)[0-9]{1,})?$", float)

    boolean = ConstantType(r"(True|False|true|false)$", lambda s: True if s in {"True", "true"} else False)

    # TODO better priority implementation

    parser = Parser(
        [pow, div, mod, mul, plus, minus,
         eq, not_eq, great_eq, less_eq, great, less,
         not_op, and_op, or_op, impl],
        [integers_decimal, integers_binary, integers_hex, float_point, boolean]
    )
