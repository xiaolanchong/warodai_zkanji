# -*- coding: utf-8 -*-
import os.path
import unittest
import sys
import warodai_to_zkanji as wd


class TestWarodai(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract_word(self):
        w, k = wd.extract_word_kanji('びんどめ【鬢留め】(биндомэ)〔1-055-2-31〕')
        self.assertEqual(w, 'びんどめ')
        self.assertEqual(k, '鬢留め')

        w, k = wd.extract_word_kanji('ビニロン(бинирон)〔1-055-2-33〕')
        self.assertEqual(w, 'ビニロン')
        self.assertIsNone(k)

    def test_definitions(self):
        defs = wd.process_definitions(['заколка <i>(для волос)</i>.'])
        self.assertEqual(defs, ['заколка (для волос).'])

        defs = wd.process_definitions(['1) сообразительность, находчивость;',
                                       '2) сообразительный (находчивый) человек.'])
        self.assertEqual(defs, ['сообразительность, находчивость;',
                                'сообразительный (находчивый) человек.'])

        defs = wd.process_definitions( ['(<i>англ.</i> bill)',
                                        '1) счёт <i>(документ)</i>;',
                                        '2) вексель.'])
        self.assertEqual(defs, ['(англ. bill) счёт (документ);',
                                'вексель.'])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWarodai)
    unittest.TextTestRunner(verbosity=2).run(suite)
