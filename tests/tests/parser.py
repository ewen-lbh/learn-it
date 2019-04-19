import os

import src.parser
import src.helpers
import unittest


def learndata_path(file) -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'learndata', file)


def learndata(file) -> list:
    file = learndata_path(file.replace('.txt', '') + '.txt')
    with open(file, 'r', encoding='utf8') as f:
        lines = f.readlines()
    return lines


class FlagsPresets(unittest.TestCase):
    def test_override(self):
        lines = learndata('test_presets')
        self.assertEqual(src.parser.parse_preset(lines), {
            "ask-order": "random", "ask-for": "both", "show-items-count": "yes", "ask-sentence": "How do you say <> ?"
        })

    def test_no_preset(self):
        lines = learndata('test_no_presets')
        self.assertEqual(src.parser.parse_preset(lines), {})


class Flags(unittest.TestCase):
    def test_no_preset(self):
        lines = learndata('test_no_presets')
        self.assertEqual(src.parser.parse_flags(lines, {})[0], {
            "ask-order": "alphabetical", "header": "LOLZ <>"
        })

    def test_with_preset(self):
        lines = learndata('test_presets')
        parsed = src.parser.parse_preset(lines)
        parsed, _ = src.parser.parse_flags(lines=lines, flags=parsed)
        self.assertEqual(parsed, {
            "ask-order": "random", "ask-for": "both", "show-items-count": "yes", "ask-sentence": "OwO <> UwU"
        })


class Data(unittest.TestCase):
    def test_parse(self):
        lines = learndata('test_data')
        data, flags = src.parser.parse(lines)
        self.assertEqual(data, {
            'Hello': 'Bonjour', 'Aurevoir': 'Bye', 'Hehehe': 'goood sh*t', 'lol--ask-sentence': '---ayylmao True',
        })
        self.assertEqual(flags, {})
