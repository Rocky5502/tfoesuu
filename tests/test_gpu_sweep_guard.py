from __future__ import annotations

import numpy as np
import pytest

from tfoesuu.allocation import AllocationResult, require_valid_allocation


@pytest.mark.parametrize(
    "allocation",
    [
        AllocationResult(10.0, np.ones(2), False, "iteration limit", 0.0),
        AllocationResult(10.0, np.ones(2), True, "ok", 1e-3),
        AllocationResult(float("nan"), np.ones(2), True, "ok", 0.0),
    ],
)
def test_gpu_sweep_rejects_untrustworthy_allocation(allocation):
    with pytest.raises(RuntimeError, match="allocation solver failed"):
        require_valid_allocation(allocation)


def test_gpu_sweep_accepts_feasible_successful_allocation():
    allocation = AllocationResult(2.0, np.ones(2), True, "ok", 1e-10)

    assert require_valid_allocation(allocation) is allocation
