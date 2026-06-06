#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Asterisk ARI WebSocket frame serializer for Pipecat."""

import base64
import json
from typing import Any, Dict

from loguru import logger

from pipecat.audio.utils import (
    create_stream_resampler,
    pcm_to_ulaw,
    ulaw_to_pcm,
)
from pipecat.frames.frames import (
    AudioRawFrame,
    CancelFrame,
    EndFrame,
    Frame,
    InputAudioRawFrame,
    InterruptionFrame,
    StartFrame,
)
from pipecat.serializers.base_serializer import FrameSerializer
from pipecat.serializers.call_strategies import HangupStrategy, TransferStrategy


class AsteriskFrameSerializer(FrameSerializer):
    """Serializer for Asterisk ARI WebSocket protocol."""

    class InputParams(FrameSerializer.InputParams):
        asterisk_sample_rate: int = 8000
        sample_rate: int | None = None

    def __init__(
        self,
        channel_id: str,
        ari_endpoint: str,
        app_name: str,
        app_password: str,
        hangup_strategy: HangupStrategy,
        transfer_strategy: TransferStrategy,
        params: "AsteriskFrameSerializer.InputParams | None" = None,
    ):
        params = params or AsteriskFrameSerializer.InputParams()
        super().__init__(params)
        self._params: AsteriskFrameSerializer.InputParams = params
        self._channel_id = channel_id
        self._ari_endpoint = ari_endpoint
        self._app_name = app_name
        self._app_password = app_password
        self._hangup_strategy = hangup_strategy
        self._transfer_strategy = transfer_strategy
        self._asterisk_sample_rate = self._params.asterisk_sample_rate
        self._sample_rate = 0
        self._input_resampler = create_stream_resampler()
        self._output_resampler = create_stream_resampler()
        self._hangup_attempted = False

    def _call_context(self) -> Dict[str, Any]:
        return {
            "channel_id": self._channel_id,
            "ari_endpoint": self._ari_endpoint,
            "app_name": self._app_name,
            "app_password": self._app_password,
        }

    async def setup(self, frame: StartFrame) -> None:
        self._sample_rate = self._params.sample_rate or frame.audio_in_sample_rate

    async def serialize(self, frame: Frame) -> str | bytes | None:
        if not self._hangup_attempted and isinstance(frame, (EndFrame, CancelFrame)):
            self._hangup_attempted = True
            await self._hangup_strategy.execute_hangup(self._call_context())
            return None
        if isinstance(frame, InterruptionFrame):
            return json.dumps({"event": "clear"})
        if isinstance(frame, AudioRawFrame):
            encoded = await pcm_to_ulaw(
                frame.audio, frame.sample_rate,
                self._asterisk_sample_rate, self._output_resampler,
            )
            if not encoded:
                return None
            return json.dumps({
                "event": "media",
                "media": {"payload": base64.b64encode(encoded).decode("utf-8")},
            })
        return None

    async def deserialize(self, data: str | bytes) -> Frame | None:
        try:
            message = json.loads(data)
        except Exception:
            return None
        if message.get("event") == "media":
            payload = base64.b64decode(message["media"]["payload"])
            pcm = await ulaw_to_pcm(
                payload, self._asterisk_sample_rate,
                self._sample_rate, self._input_resampler,
            )
            if not pcm:
                return None
            return InputAudioRawFrame(audio=pcm, num_channels=1, sample_rate=self._sample_rate)
        return None

    async def execute_transfer(self) -> bool:
        return await self._transfer_strategy.execute_transfer(self._call_context())
