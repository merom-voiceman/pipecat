#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""A no-op audio mixer that outputs silence (used when ambient noise is disabled)."""

from pipecat.audio.mixers.base_audio_mixer import BaseAudioMixer


class SilenceAudioMixer(BaseAudioMixer):
    """Audio mixer that produces silence — pass-through with no extra mixing."""

    async def start(self, frame):
        pass

    async def stop(self, frame):
        pass

    async def update_settings(self, settings: dict):
        pass

    async def mix(self, audio: bytes) -> bytes:
        return audio
