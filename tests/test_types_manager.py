import unittest
from decimal import Decimal
from ShortCircuitCalc.tools import TypesManager


class TestTypesManager(unittest.TestCase):
    def test_decimal_str(self):
        self.tm_dec_str1 = TypesManager("Decimal('0.1')")
        self.assertEqual(self.tm_dec_str1, Decimal('0.1'))

        self.tm_dec_str2 = TypesManager("Decimal('0.1')", as_decimal=True)
        self.assertEqual(self.tm_dec_str2, Decimal('0.1'))

        self.tm_dec_str3 = TypesManager("Decimal('0.1')", as_string=True)
        self.assertEqual(self.tm_dec_str3, "Decimal('0.1')")

        self.tm_dec_str4 = TypesManager("Decimal('0.1')", as_string=True, quoting=True)
        self.assertEqual(self.tm_dec_str4, "\"Decimal('0.1')\"")

        self.tm_dec_str5 = TypesManager("Decimal('0.1')", as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_dec_str5, "\"Decimal('0.1')\"")

    def test_decimal_type(self):
        self.tm_dec_type1 = TypesManager(Decimal('0.1'))
        self.assertEqual(self.tm_dec_type1, Decimal('0.1'))

        self.tm_dec_type2 = TypesManager(Decimal('0.1'), as_decimal=True)
        self.assertEqual(self.tm_dec_type2, Decimal('0.1'))

        self.tm_dec_type3 = TypesManager(Decimal('0.1'), as_string=True)
        self.assertEqual(self.tm_dec_type3, "Decimal('0.1')")

        self.tm_dec_type4 = TypesManager(Decimal('0.1'), as_string=True, quoting=True)
        self.assertEqual(self.tm_dec_type4, "\"Decimal('0.1')\"")

        self.tm_dec_type5 = TypesManager(Decimal('0.1'), as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_dec_type5, "\"Decimal('0.1')\"")

    def test_float_str(self):
        self.tm_float_str1 = TypesManager("0.1")
        self.assertEqual(self.tm_float_str1, 0.1)

        self.tm_float_str2 = TypesManager("0.1", as_decimal=True)
        self.assertEqual(self.tm_float_str2, Decimal('0.1'))

        self.tm_float_str3 = TypesManager("0.1", as_string=True)
        self.assertEqual(self.tm_float_str3, "0.1")

        self.tm_float_str4 = TypesManager("0.1", as_string=True, quoting=True)
        self.assertEqual(self.tm_float_str4, "\'0.1\'")

        self.tm_float_str5 = TypesManager("0.1", as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_float_str5, "\"Decimal('0.1')\"")

    def test_float_type(self):
        self.tm_float_type1 = TypesManager(0.1)
        self.assertEqual(self.tm_float_type1, 0.1)

        self.tm_float_type2 = TypesManager(0.1, as_decimal=True)
        self.assertEqual(self.tm_float_type2, Decimal('0.1'))

        self.tm_float_type3 = TypesManager(0.1, as_string=True)
        self.assertEqual(self.tm_float_type3, "0.1")

        self.tm_float_type4 = TypesManager(0.1, as_string=True, quoting=True)
        self.assertEqual(self.tm_float_type4, "\'0.1\'")

        self.tm_float_type5 = TypesManager(0.1, as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_float_type5, "\"Decimal('0.1')\"")

    def test_int_str(self):
        self.tm_int_str1 = TypesManager("1")
        self.assertEqual(self.tm_int_str1, 1)

        self.tm_int_str2 = TypesManager("1", as_decimal=True)
        self.assertEqual(self.tm_int_str2, Decimal('1'))

        self.tm_int_str3 = TypesManager("1", as_string=True)
        self.assertEqual(self.tm_int_str3, "1")

        self.tm_int_str4 = TypesManager("1", as_string=True, quoting=True)
        self.assertEqual(self.tm_int_str4, "\'1\'")

        self.tm_int_str5 = TypesManager("1", as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_int_str5, "\"Decimal('1')\"")

    def test_int_type(self):
        self.tm_int_type1 = TypesManager(1)
        self.assertEqual(self.tm_int_type1, 1)

        self.tm_int_type2 = TypesManager(1, as_decimal=True)
        self.assertEqual(self.tm_int_type2, Decimal('1'))

        self.tm_int_type3 = TypesManager(1, as_string=True)
        self.assertEqual(self.tm_int_type3, "1")

        self.tm_int_type4 = TypesManager(1, as_string=True, quoting=True)
        self.assertEqual(self.tm_int_type4, "\'1\'")

        self.tm_int_type5 = TypesManager(1, as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_int_type5, "\"Decimal('1')\"")

    def test_string(self):
        self.tm_string1 = TypesManager("billy")
        self.assertEqual(self.tm_string1, "billy")

        self.tm_string2 = TypesManager("billy", as_string=True)
        self.assertEqual(self.tm_string2, "billy")

        self.tm_string3 = TypesManager("billy", as_string=True, quoting=True)
        self.assertEqual(self.tm_string3, "\'billy\'")

    def test_bool_str(self):
        self.tm_bool_str1 = TypesManager("True")
        self.tm_bool_str2 = TypesManager("False")
        self.assertEqual(self.tm_bool_str1, True)
        self.assertEqual(self.tm_bool_str2, False)

        self.tm_bool_str3 = TypesManager("True", as_decimal=True)
        self.tm_bool_str4 = TypesManager("False", as_decimal=True)
        self.assertEqual(self.tm_bool_str3, Decimal('1'))
        self.assertEqual(self.tm_bool_str4, Decimal('0'))

        self.tm_bool_str5 = TypesManager("True", as_string=True)
        self.tm_bool_str6 = TypesManager("False", as_string=True)
        self.assertEqual(self.tm_bool_str5, "True")
        self.assertEqual(self.tm_bool_str6, "False")

        self.tm_bool_str7 = TypesManager("True", as_string=True, quoting=True)
        self.tm_bool_str8 = TypesManager("False", as_string=True, quoting=True)
        self.assertEqual(self.tm_bool_str7, "\'True\'")
        self.assertEqual(self.tm_bool_str8, "\'False\'")

        self.tm_bool_str9 = TypesManager("True", as_decimal=True, as_string=True, quoting=True)
        self.tm_bool_str10 = TypesManager("False", as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_bool_str9, "\"Decimal('1')\"")
        self.assertEqual(self.tm_bool_str10, "\"Decimal('0')\"")

    def test_bool_type(self):
        self.tm_bool_type1 = TypesManager(True)
        self.tm_bool_type2 = TypesManager(False)
        self.assertEqual(self.tm_bool_type1, True)
        self.assertEqual(self.tm_bool_type2, False)

        self.tm_bool_type3 = TypesManager(True, as_decimal=True)
        self.tm_bool_type4 = TypesManager(False, as_decimal=True)
        self.assertEqual(self.tm_bool_type3, Decimal('1'))
        self.assertEqual(self.tm_bool_type4, Decimal('0'))

        self.tm_bool_type5 = TypesManager(True, as_string=True)
        self.tm_bool_type6 = TypesManager(False, as_string=True)
        self.assertEqual(self.tm_bool_type5, "True")
        self.assertEqual(self.tm_bool_type6, "False")

        self.tm_bool_type7 = TypesManager(True, as_string=True, quoting=True)
        self.tm_bool_type8 = TypesManager(False, as_string=True, quoting=True)
        self.assertEqual(self.tm_bool_type7, "\'True\'")
        self.assertEqual(self.tm_bool_type8, "\'False\'")

        self.tm_bool_type9 = TypesManager(True, as_decimal=True, as_string=True, quoting=True)
        self.tm_bool_type10 = TypesManager(False, as_decimal=True, as_string=True, quoting=True)
        self.assertEqual(self.tm_bool_type9, "\"Decimal('1')\"")
        self.assertEqual(self.tm_bool_type10, "\"Decimal('0')\"")

    def test_none_str(self):
        self.tm_none_str1 = TypesManager("None")
        self.assertEqual(self.tm_none_str1, None)

        self.tm_none_str2 = TypesManager("None", as_string=True)
        self.assertEqual(self.tm_none_str2, "None")

        self.tm_none_str3 = TypesManager("None", as_string=True, quoting=True)
        self.assertEqual(self.tm_none_str3, "\'None\'")

    def test_none_type(self):
        self.tm_none_type1 = TypesManager(None)
        self.assertEqual(self.tm_none_type1, None)
        self.tm_none_type2 = TypesManager(None, as_string=True)
        self.assertEqual(self.tm_none_type2, "None")
        self.tm_none_type3 = TypesManager(None, as_string=True, quoting=True)
        self.assertEqual(self.tm_none_type3, "\'None\'")


if __name__ == '__main__':
    unittest.main()
