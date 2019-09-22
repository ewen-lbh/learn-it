#!/usr/bin/python3
import unittest
import yaml
import main


class LearndataProcessorTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.expected_flags = {
            "whitelist": ['spam', 'eggs', 'foo'],
            "ask-sentence": "What's <> ?",
            "allow-typos": True,
            "good-grade": 0.75,
            "title": "Example test",
            "show-items-count": True,
            "debug": True,
            "ask-order": "normal",
        }
        self.learnit = main.Learn_it(['learndata-example.yaml'], 'training')

    def test_file_loads(self):
        with open('./learndata-example.yaml') as f:
            filecontents = f.read()
        self.assertEqual(self.learnit._raws[0], filecontents)

    def test_add_cli_flags(self):
        self.learnit._cli_flags = dict(ask_sentence="What's «<>» ?")
        self.learnit.add_cli_flags()
        self.assertEqual(self.learnit.flags['ask-sentence'], "What's «<>» ?")

    def test_strip_flags(self):
        self.learnit.strip_flags()
        self.assertEqual(self.learnit.flags, self.expected_flags)

    def test_add_default_flags(self):
        expected = {
            "whitelist": ['spam', 'eggs', 'foo'],
            "blacklist": [],
            "ask-sentence": "What's <> ?",
            "ask-for": "answers",
            "ask-order": "normal",
            "allow-typos": True,
            "grade-max": 20,
            "good-grade": 0.75,
            "title": "Example test",
            "show-items-count": True,
            "debug": True,
            "success-sentence": '✓ Success!',
            "fail-sentence": '✕ Fail',
            "hide-timeout": 0,
            "math-delimiter": '$$',
        }

        self.learnit.strip_flags()
        self.learnit.add_default_flags()

        self.assertEqual(self.learnit.flags, expected)

    def test_process_learndata(self):
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.assertEqual(self.learnit.askdata, [
            ('foo',            ['bar', 'quux']),
            ('baz',            ['spam']),
            ('eggs',           ['spam']),
            ('spam',           ['wheel']),
            ('long key name',  ['long value name']),
        ])

    def test_get_flipped_askdata(self):
        self.learnit.process_flags()
        self.learnit.process_learndata()

        self.assertEqual(self.learnit.get_flipped_askdata(), [
            ('bar',   ['foo']),
            ('quux',  ['foo']),
            ('spam',  ['baz', 'eggs']),
            ('wheel', ['spam']),
            ('long value name', ['long key name'])
        ])

    def test_ask_order_alphabetical(self):
        self.learnit.process_flags()
        self.learnit.flags['ask-order'] = 'alphabetical'
        self.learnit.process_learndata()
        self.learnit.process_ask_order()

        self.assertEqual(self.learnit.askdata, [
            ('baz',            ['spam']),
            ('eggs',           ['spam']),
            ('foo',            ['bar', 'quux']),
            ('long key name',  ['long value name']),
            ('spam',           ['wheel']),
        ])

    def test_ask_order_random(self):
        self.learnit.process_flags()
        self.learnit.flags['ask-order'] = 'random'
        self.learnit.process_learndata()
        self.learnit.process_ask_order()

        # We can't really test for randomness, so we'll just make
        # sure that we're not getting the exact SAME result
        # as if we were not shuffling at all, but there's a slight
        # chance that this test will fail because of bad luck.
        # if it really fails because of bad luck, welp -- don't play lottery today.
        self.assertNotEqual(self.learnit.askdata, [
            ('foo',            ['bar', 'quux']),
            ('baz',            ['spam']),
            ('eggs',           ['spam']),
            ('spam',           ['wheel']),
            ('long key name',  ['long value name']),
        ])

    def test_ask_order_inverted(self):
        self.learnit.process_flags()
        self.learnit.flags['ask-order'] = 'inverted'
        self.learnit.process_learndata()
        self.learnit.process_ask_order()

        self.assertEqual(self.learnit.askdata, [
            ('long key name',  ['long value name']),
            ('spam',           ['wheel']),
            ('eggs',           ['spam']),
            ('baz',            ['spam']),
            ('foo',            ['bar', 'quux']),
        ])


class CLITests(unittest.TestCase):
    def setUp(self):
        self.learnit = main.Learn_it(['learndata-example.yaml'], 'training')
        self.learnit.process_flags()
        self.learnit.process_askdata()

    def test_ask_sentence(self):

        actual = self.learnit.get_ask_sentence('foo')
        expected = "What's foo ?"
        self.assertEqual(actual, expected)

    def test_compute_score_normal(self):
        self.learnit.fails = ['spam', 'foo']
        self.assertEqual(self.learnit.compute_score(), '12/20')

    def test_compute_score_0(self):
        self.learnit.fails = ['long key name',  'spam', 'eggs', 'baz',  'foo']
        self.assertEqual(self.learnit.compute_score(), '0/20')

    def test_compute_score_1(self):
        self.learnit.fails = []
        self.assertEqual(self.learnit.compute_score(), '20/20')

    def test_compute_score_decimal(self):
        self.learnit.flags['grade-max'] = 1
        self.learnit.fails = ['spam']
        self.assertEqual(self.learnit.compute_score(), '0.80/1')
    
    def test_compute_score_percentage(self):
        self.learnit.flags['grade-max'] = 100
        self.learnit.fails = ['spam', 'foo', 'long key name']
        self.assertEqual(self.learnit.compute_score(), '40%')

import extract
from os.path import join as path
from os.path import dirname
import os
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.base_dir = path(dirname(dirname(__file__)), 'test-data')
        self.extractor = extract.Extractor(path(self.base_dir, 'extractor-test-data.adoc'))
        self.extractor.TITLE_FMT = '%(Subject)s: %(notion)s'
        with open(path(self.base_dir,'extractor-expected-output.yaml')) as f:
            self.expected_dict = dict(yaml.load(f.read(), Loader=yaml.BaseLoader))
    
    def test_destination(self):
        actual = self.extractor._dst
        expected = path(path(self.base_dir, 'learndata'),'extractor-test-data.yaml')
        self.assertEqual(actual, expected)

    def test_get_infos(self):
        self.extractor.get_infos()
        actual = self.extractor.infos
        expected = {
            'subject': 'test-data',
            'notion': 'Verbes irréguliers'
        }
        self.assertEqual(actual, expected)

    def test_flags(self):
        self.extractor.get_infos()
        self.extractor.compute_flags()
        actual = self.extractor._flags
        expected = self.expected_dict[main.Learn_it.FLAGS_KEY_NAME]
        self.assertEqual(actual, expected)

    def test_data(self):
        self.extractor.compute_data()
        actual = self.extractor._data
        expected = {k:v for k,v in self.expected_dict.items() if k != main.Learn_it.FLAGS_KEY_NAME}
        self.assertEqual(actual, expected)

    def test_files(self):
        self.extractor.get_infos()
        self.extractor.compute_flags()
        self.extractor.compute_data()
        self.extractor.save_file()

        with open(self.extractor._dst, 'r') as f:
            actual = f.read()
        with open(path(self.base_dir,'extractor-expected-output.yaml'), 'r') as f:
            expected = f.read()
        self.assertEqual(actual, expected)
    
    def tearDown(self):
        if os.path.isfile(self.extractor._dst):
            os.remove(self.extractor._dst)

if __name__ == "__main__":
    unittest.main()
