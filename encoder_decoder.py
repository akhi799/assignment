import struct

class Encoder:
    @staticmethod
    def encode_null():
        return [0x00]

    @staticmethod
    def encode_octets(data):
        length = len(data)
        return [0x01, length] + list(data)

    @staticmethod
    def encode_integer(data):
        return [0x02] + list(struct.pack('<Q', data))

    @staticmethod
    def encode_string(data):
        encoded_string = data.encode('utf-8')
        length = len(encoded_string)
        return [0x05, length] + list(encoded_string)

    @staticmethod
    def encode_sequence(data):
        encoded_elements = []
        for element in data:
            encoded_elements += Encoder.encode(element)
        return [0x03] + encoded_elements

    @staticmethod
    def encode_length_prefixed_sequence(data):
        encoded_sequence = Encoder.encode_sequence(data)
        length = len(encoded_sequence)
        return [0x04] + list(struct.pack('!I', length)) + encoded_sequence

@staticmethod
def encode_dictionary(data):
    encoded_items = []
    for key, value in sorted(data.items()):
        encoded_key = Encoder.encode_string(key)
        encoded_value = Encoder.encode(value)
        encoded_items += encoded_key + encoded_value
    return [0x06] + encoded_items

    @staticmethod
    def encode(data):
        if data is None:
            return Encoder.encode_null()
        elif isinstance(data, bytes):
            return Encoder.encode_octets(data)
        elif isinstance(data, int):
            return Encoder.encode_integer(data)
        elif isinstance(data, str):
            return Encoder.encode_string(data)
        elif isinstance(data, list):
            return Encoder.encode_length_prefixed_sequence(data)
        elif isinstance(data, dict):
            return Encoder.encode_dictionary(data)
        else:
            raise TypeError(f'Unsupported data type: {type(data)}')

class Decoder:
    @staticmethod
    def decode_null(data):
        return None, data[1:]

    @staticmethod
    def decode_octets(data):
        length = data[1]
        octets = bytes(data[2:2+length])
        return octets, data[2+length:]

    @staticmethod
    def decode_integer(data):
        integer = struct.unpack('<Q', bytes(data[1:9]))[0]
        return integer, data[9:]

    @staticmethod
    def decode_string(data):
        length = data[1rabi]
        string = bytes(data[2:2+length]).decode('utf-8')
        return string, data[2+length:]

    @staticmethod
    def decode_sequence(data):
        elements = []
        data = data[1:]
        while data:
            element, data = Decoder.decode(data)
            elements.append(element)
        return elements, data

    @staticmethod
    def decode_length_prefixed_sequence(data):
        length = struct.unpack('!I', bytes(data[1:5]))[0]
        sequence_data = data[5:5+length]
        sequence, _ = Decoder.decode_sequence(sequence_data)
        return sequence, data[5+length:]

    @staticmethod
    def decode_dictionary(data):
        num_items = data[1]
        dictionary = {}
        data = data[2:]
        for _ in range(num_items):
            key, data = Decoder.decode(data)
            value, data = Decoder.decode(data)
            dictionary[key] = value
        return dictionary, data

    @staticmethod
    def decode(data):
        if data[0] == 0x00:
            return Decoder.decode_null(data)
        elif data[0] == 0x01:
            return Decoder.decode_octets(data)
        elif data[0] == 0x02:
            return Decoder.decode_integer(data)
        elif data[0] == 0x03:
            return Decoder.decode_sequence(data)
        elif data[0] == 0x04:
            return Decoder.decode_length_prefixed_sequence(data)
        elif data[0] == 0x05:
            return Decoder.decode_string(data)
        elif data[0] == 0x06:
            return Decoder.decode_dictionary(data)
        else:
            raise TypeError(f'Unsupported data type: {data[0]}')
