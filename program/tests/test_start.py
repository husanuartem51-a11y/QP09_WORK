import unittest
from shop_core import quote, RuleError
class StarterTests(unittest.TestCase):
    def test_reference_pickup(self):
        self.assertEqual(quote([{"id":"N200","quantity":1}],"","pickup")["total"],20000)
    def test_zero_quantity_is_rejected(self):
        with self.assertRaises(RuleError) as context:
            quote([{"id":"N200","quantity":0}],"","pickup")
        self.assertEqual(context.exception.code,"QUANTITY")
if __name__ == "__main__":
    unittest.main()
