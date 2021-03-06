#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import torch
from pytorch_translate.rescoring.model_scorers import SimpleModelScorer
from pytorch_translate.tasks import pytorch_translate_task as tasks
from pytorch_translate.test import utils as test_utils


class TestModelScorers(unittest.TestCase):
    def test_reverse_tgt_tokens(self):
        test_args = test_utils.ModelParamsDict()
        _, src_dict, tgt_dict = test_utils.prepare_inputs(test_args)
        task = tasks.PytorchTranslateTask(test_args, src_dict, tgt_dict)
        model = task.build_model(test_args)

        with patch(
            "pytorch_translate.utils.load_diverse_ensemble_for_inference",
            return_value=([model], test_args, task),
        ):
            scorer = SimpleModelScorer(test_args, None, task)

            pad = task.tgt_dict.pad()
            tgt_tokens = torch.Tensor([[1, 2, 3], [1, 2, pad], [1, pad, pad]])
            expected_tokens = torch.Tensor([[3, 2, 1], [2, 1, pad], [1, pad, pad]])
            reversed_tgt_tokens = scorer.reverse_tgt_tokens(tgt_tokens)
            assert torch.equal(reversed_tgt_tokens, expected_tokens)

    def test_convert_hypos_to_tgt_tokens(self):
        test_args = test_utils.ModelParamsDict()
        _, src_dict, tgt_dict = test_utils.prepare_inputs(test_args)
        task = tasks.PytorchTranslateTask(test_args, src_dict, tgt_dict)
        model = task.build_model(test_args)

        with patch(
            "pytorch_translate.utils.load_diverse_ensemble_for_inference",
            return_value=([model], test_args, task),
        ):
            scorer = SimpleModelScorer(test_args, None, task)

            hypos = [
                {"tokens": torch.Tensor([1, 2, 3, 4, 5])},
                {"tokens": torch.Tensor([1, 2, 3, 4])},
                {"tokens": torch.Tensor([1, 2, 3])},
                {"tokens": torch.Tensor([1, 2])},
                {"tokens": torch.Tensor([1])},
            ]
            tgt_tokens = scorer.convert_hypos_to_tgt_tokens(hypos)

            pad = task.tgt_dict.pad()
            eos = task.tgt_dict.eos()
            expected_tgt_tokens = torch.Tensor(
                [
                    [eos, 1, 2, 3, 4, 5],
                    [eos, 1, 2, 3, 4, pad],
                    [eos, 1, 2, 3, pad, pad],
                    [eos, 1, 2, pad, pad, pad],
                    [eos, 1, pad, pad, pad, pad],
                ]
            ).type_as(tgt_tokens)
            assert torch.equal(tgt_tokens, expected_tgt_tokens)
