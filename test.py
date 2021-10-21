import unittest
from simpleparser.simpleparser import *


class ParserTest(unittest.TestCase):
    def test_boolean(self):
        expr1 = Defaults.parser.parse("(a -> b -> c) and d")
        self.assertEqual(expr1(a=False, b=True, c=False, d=True), False)
        self.assertEqual(expr1(a=True, b=False, c=True, d=False), False)
        expr2 = Defaults.parser.parse("a != 1 and a * 1 <> 2 and not a ** 2 == 9")
        for a in range(-3, 5):
            self.assertEqual(expr2(a=a), a != 1 and a * 1 != 2 and not a ** 2 == 9)

    def test_calculator(self):
        expr1 = Defaults.parser.parse("a + b * c^a / b")
        self.assertEqual(expr1(a=1, b=7, c=3), 4)
        expr2 = Defaults.parser.parse("(a - b) / (a + b) + a ^ b / a")
        self.assertEqual(expr2(a=23, b=8), (23 - 8) / (23 + 8) + (23 ** 8) / 23)

    def test_constants(self):
        expr1 = Defaults.parser.parse("1 + a / 2.0")
        self.assertEqual(expr1(a=4.0), 1 + 4.0 / 2.0)
        expr2 = Defaults.parser.parse("0b10+4e5^(0x8F/10+a*.07)")
        self.assertEqual(expr2(a=0.7), 0b10 + 4e5 ** (0x8F / 10 + 0.7 * .07))

    def test_deep(self):
        self.assertEqual(str(Defaults.parser.split("(True&&a->!False)||8>=8&&8<9")), str([
            BraceToken(BraceToken.OPEN),
            ConstantToken(True),
            OperatorToken(Defaults.and_op),
            VariableToken("a"),
            OperatorToken(Defaults.impl),
            OperatorToken(Defaults.not_op),
            ConstantToken(False),
            BraceToken(BraceToken.CLOSE),
            OperatorToken(Defaults.or_op),
            ConstantToken(8),
            OperatorToken(Defaults.great_eq),
            ConstantToken(8),
            OperatorToken(Defaults.and_op),
            ConstantToken(8),
            OperatorToken(Defaults.less),
            ConstantToken(9),
        ]))  # not comparing actual values here because Token.__eq__ is not defined
        parsed = Defaults.parser.parse("(True&&a->!False)||8>=8&&8<9")
        self.assertEqual(parsed.precalculated, [True, False, 8, 8, 8, 9])
        self.assertEqual(str(parsed.operations), str([
            (Defaults.not_op, (1,)),                        # 6 (5 precalculated + 1st operation)
            (Defaults.and_op, (0, VariableToken("a"))),     # 7
            (Defaults.impl, (7, 6)),                        # 8
            (Defaults.great_eq, (2, 3)),                    # 9
            (Defaults.less, (4, 5)),                        # 10
            (Defaults.and_op, (9, 10)),                     # 11
            (Defaults.or_op, (8, 11)),                      # 12
            ]))
        self.assertEqual(parsed(a=True), True)
        self.assertEqual(parsed(a=False), True)


if __name__ == '__main__':
    unittest.main()
