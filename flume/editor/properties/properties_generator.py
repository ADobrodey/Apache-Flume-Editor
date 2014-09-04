import pickle

avro_source = {
    "channels": {"value": None, "required": True, "description": ""},

    "type": {"value": "avro", "required": True,
             "description": "The component type name, needs to be avro"},

    "bind": {"value": None, "required": True,
             "description": "hostname or IP address to listen on"},

    "port": {"value": None, "required": True,
             "description": "Port # to bind to"},

    "threads": {"value": None, "required": False,
                "description": "Maximum number of worker threads to spawn"},

    "compression-type": {"value": "none", "required": False,
                         "description": "This can be “none” or “deflate”. The compression-type must match the compression-type of matching AvroSource"},

    "ssl": {"value": "false", "required": False,
            "description": "Set this to true to enable SSL encryption. You must also specify a 'keystore' and a 'keystore-password'."},
}

thrift_source = {
    "channels": {"value": None, "required": True,
                 "description": ""},

    "type": {"value": "thrift", "required": True,
             "description": "The component type name, needs to be thrift"},

    "bind": {"value": None, "required": True,
             "description": "hostname or IP address to listen on"},

    "port": {"value": None, "required": True,
             "description": "Port # to bind to"},

    "threads": {"value": None, "required": False,
                "description": "Maximum number of worker threads to spawn"},
}

netcat_source = {
    "channels": {"value": None, "required": True, "description": ""},

    "type": {"value": "netcat", "required": True,
             "description": "The component type name, needs to be netcat"},

    "bind": {"value": None, "required": True,
             "description": "hostname or IP address to listen on"},

    "port": {"value": None, "required": True,
             "description": "Port # to bind to"},
}

logger_sink = {
    "channel": {"value": None, "required": True,
                "description": ""},

    "type": {"value": "logger", "required": True,
             "description": "The component type name, needs to be logger"},
}

avro_sink = {
    "channel": {"value": None, "required": True,
                "description": ""},

    "type": {"value": "avro", "required": True,
             "description": "The component type name, needs to be avro"},

    "bind": {"value": None, "required": True,
             "description": "hostname or IP address to listen on"},

    "port": {"value": None, "required": True,
             "description": "Port # to bind to"},

    "batch-size": {"value": "100", "required": False,
                   "description": "Number of event to batch together for send."},

    "connect-timeout": {"value": "20000", "required": False,
                        "description": "Amount of time (ms) to allow for the first (handshake) request."},
}

memory_channel = {
    "type": {"value": "memory", "required": True,
             "description": "The component type name, needs to be memory"},
    "capacity": {"value": "100", "required": False,
                 "description": "The maximum number of events stored in the channel"},
}


def dump_props():
    pickle.dump(avro_source, open("properties/source/avro.dat", "wb"))
    pickle.dump(thrift_source, open("properties/source/thrift.dat", "wb"))
    pickle.dump(netcat_source, open("properties/source/netcat.dat", "wb"))
    pickle.dump(logger_sink, open("properties/sink/logger.dat", "wb"))
    pickle.dump(avro_sink, open("properties/sink/avro.dat", "wb"))
    pickle.dump(memory_channel, open("properties/channel/memory.dat", "wb"))


if __name__ == '__main__':
    dump_props()

# print(pickle.load(open("properties/channel/memory.dat", "rb")))


