# -*- coding: utf-8 -*-
import iscc_observer_evm as evm


def test_registry():
    assert hasattr(evm, "registry")
