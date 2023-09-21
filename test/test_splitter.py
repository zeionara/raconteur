from unittest import TestCase, main

from rr import Splitter


class TestSplitter(TestCase):

    def test_no_constraints(self):
        self.assertEqual(Splitter().split('foo'), ('foo', ))

    def test_multiple_tokens_with_single_space(self):
        self.assertEqual(Splitter(max_n_characters = 10).split('foo bar baz qux quux'), ('foo bar', 'baz qux', 'quux'))

    def test_multiple_tokens_with_multiple_intermediate_spaces(self):
        self.assertEqual(Splitter(max_n_characters = 10).split('foo    bar baz qux quux'), ('foo    bar', 'baz qux', 'quux'))

    def test_multiple_tokens_with_multiple_intermediate_spaces_2(self):
        self.assertEqual(Splitter(max_n_characters = 10).split('foo     bar baz qux quux'), ('foo', 'bar baz', 'qux quux'))

    def test_leading_and_trailing_spaces(self):
        self.assertEqual(Splitter(max_n_characters = 10).split('         foo  bar baz qux quux          '), ('foo  bar', 'baz qux', 'quux'))

    def test_long_tokens(self):
        self.assertEqual(Splitter(max_n_characters = 10).split('foo onetwothreefour five sixs eveneight'), ('foo', 'onetwothre', 'efour five', 'sixs', 'eveneight'))


if __name__ == '__main__':
    main()
