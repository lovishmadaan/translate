#!/usr/bin/env python3

import unittest
from collections import Counter
from unittest.mock import Mock, patch

from pytorch_translate.research.unsupervised_morphology import bpe


txt_content = ["123 124 234 345", "112 122 123 345", "123456789", "123456 456789"]


class TestBPE(unittest.TestCase):
    def test_vocab_init(self):
        bpe_model = bpe.BPE()

        with patch("builtins.open") as mock_open:
            mock_open.return_value.__enter__ = mock_open
            mock_open.return_value.__iter__ = Mock(return_value=iter(txt_content))
            bpe_model.init_vocab(txt_path="no_exist_file.txt")

            vocab_items = Counter()
            for vocab_entry in bpe_model.vocab.keys():
                items = vocab_entry.split()
                for item in items:
                    vocab_items[item] += bpe_model.vocab[vocab_entry]

            assert vocab_items[bpe_model.eow_symbol] == 11
            assert vocab_items["3"] == 7
            assert len(vocab_items) == 10
            assert "12" not in vocab_items
            assert "123" not in vocab_items

    def test_best_candidate(self):
        bpe_model = bpe.BPE()

        with patch("builtins.open") as mock_open:
            mock_open.return_value.__enter__ = mock_open
            mock_open.return_value.__iter__ = Mock(return_value=iter(txt_content))
            bpe_model.init_vocab(txt_path="no_exist_file.txt")

            assert bpe_model.get_best_candidate() == ("1", "2")
