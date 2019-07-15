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
            "ask-order": "normal"
        }
        self.learnit = main.Learn_it('./learndata-example.yaml')

    def test_file_loads(self):
        with open('./learndata-example.yaml') as f:
            filecontents = f.read()
        self.assertEqual(self.learnit._raw, filecontents)

    def test_add_cli_flags(self):
        self.learnit._cli_flags = dict(ask_sentence="What's «<>» ?")
        self.learnit.add_cli_flags()
        self.assertEqual(self.learnit._flags['ask-sentence'], "What's «<>» ?")

    def test_strip_flags(self):
        self.learnit.strip_flags()
        self.assertEqual(self.learnit._flags, self.expected_flags)

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
        }

        self.learnit.strip_flags()
        self.learnit.add_default_flags()

        self.assertEqual(self.learnit._flags, expected)


    def test_process_learndata(self):
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.assertEqual(self.learnit._askdata, [
            ('foo',            {'bar','quux'}),
            ('baz',            {'spam'}),
            ('eggs',           {'spam'}),
            ('spam',           {'wheel'}),
            ('long key name',  {'long value name'}),
        ])

    def test_ask_for_answers(self):
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.assertEqual(self.learnit._askdata, [
            ('foo',            {'bar','quux'}),
            ('baz',            {'spam'}),
            ('eggs',           {'spam'}),
            ('spam',           {'wheel'}),
            ('long key name',  {'long value name'}),
        ])

    def test_ask_for_questions(self):
        self.learnit._flags['ask-for'] = 'questions'
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.learnit.process_ask_for()

        self.assertEqual(self.learnit._askdata, [
            ('bar',   {'foo'}),
            ('quux',  {'foo'}),
            ('spam',  {'baz', 'eggs'}),
            ('wheel', {'spam'}),
            ('long value name', {'long key name'})
        ])

    def test_ask_for_both(self):
        self.learnit._flags['ask-for'] = 'both'
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.learnit.process_ask_for()

        self.assertEqual(self.learnit._askdata, [
            ('foo',             {'bar','quux'}),
            ('baz',             {'spam'}),
            ('eggs',            {'spam'}),
            ('spam',            {'wheel'}),
            ('long key name',   {'long value name'}),
            ('bar',             {'foo'}),
            ('quux',            {'foo'}),
            ('spam',            {'baz', 'eggs'}),
            ('wheel',           {'spam'}),
            ('long value name', {'long key name'})
        ])

    
    def test_ask_order_alphabetical(self):
        self.learnit._flags['ask-order'] = 'alphabetical'
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.learnit.process_ask_for()
        self.learnit.process_ask_order()

        self.assertEqual(self.learnit._askdata, [
            ('baz',            {'spam'}),
            ('eggs',           {'spam'}),
            ('foo',            {'bar','quux'}),
            ('long key name',  {'long value name'}),
            ('spam',           {'wheel'}),
        ])

    def test_ask_order_random(self):
        self.learnit._flags['ask-order'] = 'random'
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.learnit.process_ask_for()
        self.learnit.process_ask_order()

        # We can't really test for randomness, so we'll just make
        # sure that we're not getting the exact SAME result
        # as if we were not shuffling at all, but there's a slight
        # chance that this test will fail because of bad luck.
        # if it really fails because of bad luck, welp -- don't play lottery today.
        self.assertNotEqual(self.learnit._askdata, [
                ('foo',            {'bar','quux'}),
                ('baz',            {'spam'}),
                ('eggs',           {'spam'}),
                ('spam',           {'wheel'}),
                ('long key name',  {'long value name'}),
        ])

    def test_ask_order_inverted(self):
        self.learnit._flags['ask-order'] = 'inverted'
        self.learnit.process_flags()
        self.learnit.process_learndata()
        self.learnit.process_ask_for()
        self.learnit.process_ask_order()

        self.assertEqual(self.learnit._askdata, [
                ('long key name',  {'long value name'}),
                ('spam',           {'wheel'}),
                ('eggs',           {'spam'}),
                ('baz',            {'spam'}),
                ('foo',            {'bar','quux'}),
        ])

    
        


class CLITests(unittest.TestCase):
    def setUp(self):
        self.learnit = main.Learn_it('./learndata-example.yaml')
        self.learnit.process_askdata()

    def test_ask_sentence(self):

        actual = self.learnit.get_ask_sentence('foo')
        expected = "What's foo ?"
        self.assertEqual(actual, expected)

    def test_compute_score(self):
        self.assertEqual(self.learnit.compute_score(failed=4), '16.0/20')

if __name__ == "__main__":
    unittest.main()
