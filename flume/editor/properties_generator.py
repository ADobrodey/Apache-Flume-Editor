import pickle

avro_source = (
    {"name": "channels", "default": None, "required": True,
     "description": ""},

    {"name": "type", "default": None, "required": True,
     "description": "The component type name, needs to be avro"},

    {"name": "bind", "default": None, "required": True,
     "description": "hostname or IP address to listen on"},

    {"name": "port", "default": None, "required": True,
     "description": "Port # to bind to"},

    {"name": "threads", "default": None, "required": False,
     "description": "Maximum number of worker threads to spawn"},

    {"name": "compression-type", "default": "none", "required": False,
     "description": "This can be “none” or “deflate”. The compression-type must match the compression-type of matching AvroSource"},

    {"name": "ssl", "default": "false", "required": False,
     "description": "Set this to true to enable SSL encryption. You must also specify a “keystore” and a “keystore-password”."},
)

thrift_source = (
    {"name": "channels", "default": None, "required": True,
     "description": ""},

    {"name": "type", "default": None, "required": True,
     "description": "The component type name, needs to be thrift"},

    {"name": "bind", "default": None, "required": True,
     "description": "hostname or IP address to listen on"},

    {"name": "port", "default": None, "required": True,
     "description": "Port # to bind to"},

    {"name": "threads", "default": None, "required": False,
     "description": "Maximum number of worker threads to spawn"},
)

logger_sink = (
    {"name": "channel", "default": None, "required": True,
     "description": ""},

    {"name": "type", "default": None, "required": True,
     "description": "The component type name, needs to be logger"},
)

avro_sink = (
    {"name": "channel", "default": None, "required": True,
     "description": ""},

    {"name": "type", "default": None, "required": True,
     "description": "The component type name, needs to be avro"},

    {"name": "bind", "default": None, "required": True,
     "description": "hostname or IP address to listen on"},

    {"name": "port", "default": None, "required": True,
     "description": "Port # to bind to"},

    {"name": "batch-size", "default": 100, "required": False,
     "description": "Number of event to batch together for send."},

    {"name": "connect-timeout", "default": 20000, "required": False,
     "description": "Amount of time (ms) to allow for the first (handshake) request."},
)

memory_channel = (
    {"name": "type", "default": None, "required": True,
     "description": "The component type name, needs to be memory"},
    {"name": "capacity", "default": 100, "required": False,
     "description": "The maximum number of events stored in the channel"},
)

if __name__ == '__main__':
    import sys

    pickle.dump(avro_source, open("properties/source/avro.dat", "wb"))
    pickle.dump(thrift_source, open("properties/source/thrift.dat", "wb"))
    pickle.dump(logger_sink, open("properties/sink/logger.dat", "wb"))
    pickle.dump(avro_sink, open("properties/sink/avro.dat", "wb"))
    pickle.dump(memory_channel, open("properties/channel/memory.dat", "wb"))

print(pickle.load(open("properties/channel/memory.dat", "rb")))


