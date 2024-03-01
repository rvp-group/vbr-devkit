import os
import sys
from pathlib import Path
from typing import Sequence, List
import natsort

from vbr_devkit.tools import convert_msg_to_datum


class RosReader:
    def __init__(self, data_dir: Sequence[Path], topics: List[str] = None, *args, **kwargs):
        try:
            from rosbags.highlevel import AnyReader
        except ModuleNotFoundError:
            print("rosbags library not installed, run 'pip install -U rosbags'")
            sys.exit(-1)

        if isinstance(data_dir, Path):
            self.sequence_id = os.path.basename(data_dir).split(".")[0]
            self.bag = AnyReader([data_dir])
        else:
            self.sequence_id = os.path.basename(data_dir[0]).split(".")[0]
            self.bag = AnyReader(data_dir)
            print("Reading multiple .bag files in directory:")
            print("\n".join(natsort.natsorted([path.name for path in self.bag.paths])))

        self.bag.open()
        connections = self.bag.connections

        if topics:
            print("Reading the following topics")
            print("\n".join(topics))
            connections = [x for x in self.bag.connections if x.topic in topics]
        self.msgs = self.bag.messages(connections=connections)

    def __del__(self):
        if hasattr(self, "bag"):
            self.bag.close()

    def __len__(self):
        return self.bag.message_count

    def __getitem__(self, item):
        connection, timestamp, rawdata = next(self.msgs)
        msg = self.bag.deserialize(rawdata, connection.msgtype)
        # msg = deserialize_cdr(ros1_to_cdr(rawdata, connection.msgtype), connection.msgtype)
        datum = convert_msg_to_datum(msg, connection.msgtype)
        return timestamp, connection.topic, datum
