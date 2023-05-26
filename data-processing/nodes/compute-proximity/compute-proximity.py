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
import logging
from typing import Dict, Any
import struct
import json

MAX_RANGE = 40
MIN_RANGE = 5
NB_PROXIMITY_LEVEL = 4


class ComputeProximity(Operator):
    def __init__(
        self,
        context: Context,
        configuration: Dict[str, Any],
        inputs: Dict[str, Input],
        outputs: Dict[str, Output],
    ):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
        self.output = outputs.take_raw("light")
        self.in_stream = inputs.take_raw("distance")

        if self.in_stream is None:
            raise ValueError("No input 'distance' found")
        if self.output is None:
            raise ValueError("No output 'light' found")

        if configuration is not None:
            self.max_range = configuration.get('max_range', MAX_RANGE)
            self.min_range = configuration.get('min_range', MIN_RANGE)
            self.nb_proximity_level = configuration.get('number_of_proximity_levels', NB_PROXIMITY_LEVEL)

        self.last_prox_level = 0

    def finalize(self) -> None:
        return None

    async def iteration(self) -> None:
        data_msg = await self.in_stream.recv()
        # this gets converts the distance to a proximity level used to
        # turn on a LED

        # deserialize distance
        distance = deserialize_float(data_msg.data)
        logging.debug(f'Avg distance in cm {distance}')
        # compute proximity level

        prox_level = round((self.max_range - distance) * self.nb_proximity_level / (self.max_range - self.min_range))
        prox_level = max(min(prox_level, self.nb_proximity_level), 0)
        # if proximity level changed:
        logging.debug(f'Distance {distance} Proximity Level {prox_level}')
        if (prox_level != self.last_prox_level):
            # compute brightness and color depending the proximity level
            brightness = 15 + (prox_level * 240) / self.nb_proximity_level
            red = round(255 * prox_level / self.nb_proximity_level)
            green = round(255 * (1 - (prox_level / self.nb_proximity_level)))
            blue = 0
            logging.debug(f"min_dist={distance} => proximity_level={prox_level} => publish brightness={brightness},RGB=({red},{green},{blue}) to light ")
            # publish over zenoh the JSON message setting the lightbulb brightness and color
            # (see supported JSON attributes in https://www.zigbee2mqtt.io/devices/33943_33944_33946.html)
            ctrl_data = {'brightness': brightness, 'color': {'r': red, 'g': green, 'b': blue}}
            await self.output.send(json.dumps(ctrl_data).encode("utf-8"))
            self.last_prox_level = prox_level
        return None


def deserialize_float(data: bytes) -> float:
    return struct.unpack('<f', data)[0]


def register():
    return ComputeProximity