#
# Copyright (c) 2022 ZettaScale Technology
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ZettaScale Zenoh Team, <zenoh@zettascale.tech>
#


from zenoh_flow.interfaces import Operator
from zenoh_flow import Input, Output
from zenoh_flow.types import Context
from typing import Dict, Any
import struct

MAX_BUFFER_SIZE = 5


class ComputeMovingAverage(Operator):
    def __init__(
        self,
        context: Context,
        configuration: Dict[str, Any],
        inputs: Dict[str, Input],
        outputs: Dict[str, Output],
    ):

        self.output = outputs.take_raw("distance")
        self.in_stream = inputs.take_raw("distance")

        if self.in_stream is None:
            raise ValueError("No input 'distance' found")
        if self.output is None:
            raise ValueError("No output 'distance' found")

        self.buffer = []

    def finalize(self) -> None:
        return None

    async def iteration(self) -> None:
        data_msg = await self.in_stream.recv()

        # this gets the moving average distance from the sensor
        current_value = deserialize_long(data_msg.data)

        print(f'Current value {current_value}')
        if len(self.buffer) >= MAX_BUFFER_SIZE:
            print(f"buffer is full, removing {self.buffer.pop(0)} ")

        self.buffer.append(current_value)

        average = sum(self.buffer) / len(self.buffer)
        print(f'Moving average {average}')

        await self.output.send(serialize_float(average))
        return None


def deserialize_long(data: bytes) -> int:
    return struct.unpack('<l', data)[0]


def serialize_float(value: float) -> bytes:
    return struct.pack('<f', value)


def register():
    return ComputeMovingAverage
