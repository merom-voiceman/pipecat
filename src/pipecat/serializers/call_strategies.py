#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Abstract strategy interfaces for call-level operations (hangup, transfer)."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class HangupStrategy(ABC):
    """Abstract base for provider-specific call hangup implementations."""

    @abstractmethod
    async def execute_hangup(self, context: Dict[str, Any]) -> bool:
        """Execute the hangup operation."""


class TransferStrategy(ABC):
    """Abstract base for provider-specific call transfer implementations."""

    @abstractmethod
    async def execute_transfer(self, context: Dict[str, Any]) -> bool:
        """Execute the transfer operation."""
