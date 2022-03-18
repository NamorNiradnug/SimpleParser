# SimpleParser
Simple expressions parser.

# Installing
Installing via pip:
```bash
$ pip install simpleparser
```

# Usage
## Parser
To simply parse something, use `Parser.parse` method. With `Parser` you can describe different parsers.
There is ready-made `Defaults.parser`. 
```python
from simpleparser import Defaults
expr = "a + b / 2"
parsed = Defaults.parser.parse(expr)
parsed(a=2, b=4) # returns 4.0
```
`Parser.parse` returns callable `ParsedExpression` object.
### Custom parsers
`Parser` can be easily configured. It is described by a set of operators and constants types (such as numbers or booleans).
See the `Operator` and `ConstantType` documentation below.
```python
from simpleparser import Parser, Defaults
my_parser = Parser(
    operators=[Defaults.plus, Defaults.minus, Defaults.mul, Defaults.div], # using some operators from `Defaults` here
    constants=[Defaults.integers_decimal, Defaults.float_point]
)
```
Here `my_parser` parses simple math expressions with 4 basic operators and decimal numbers, for example `1 + 2.0 * a`.
## Operator
Creating a custom operator:
```python
from simpleparser import Operator, Parser
in_op = Operator(
    name="in",
    operator_type=2,
    func=lambda el, container: el in container,
    signs=("\u2208",),
    priority=3,
)
# creating new parser which uses this operator
new_parser = Parser([in_op], [])
el_in_set_checker = new_parser.parse("a in A")
el_in_set_checker(a=1, A={1, 2, 3}) # True
el_in_set_checker(a=0, A={1, 2, 3}) # False
```
## ConstantType
Describes a type of constants which can be used in expression. Here is the definition of `Defaults.boolean`:
```python
from simpleparser import ConstantType
boolean = ConstantType(r"(True|False|true|false)$", lambda s: True if s in {"True", "true"} else False)
```
Parser with this constant type replaces words which are matched by the `boolean`'s regular expression to `True` or `False`.
```python
parser = Parser([],[boolean])
parser.parse("True")() # True
parser.parse("false")() # False
```
