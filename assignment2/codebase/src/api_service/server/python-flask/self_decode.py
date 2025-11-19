import binascii

# ------------------------------
# Wire type constants
# ------------------------------
WIRE_VARINT = 0
WIRE_64BIT = 1
WIRE_LENGTH_DELIMITED = 2


# ------------------------------
# Helper: decode a varint
# ------------------------------
def read_varint(buffer, index):
    shift = 0
    result = 0
    while True:
        b = buffer[index]
        index += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, index


# ------------------------------
# Helper: decode 64-bit (double)
# ------------------------------
import struct
def read_64bit(buffer, index):
    data = buffer[index:index+8]
    value = struct.unpack("<d", data)[0]  # little-endian double
    return value, index + 8


# ------------------------------
# Helper: recursively decode a nested message
# ------------------------------
def parse_message(buffer, index, end):
    fields = {}
    while index < end:
        # Decode tag
        tag, index = read_varint(buffer, index)
        field_number = tag >> 3
        wire_type = tag & 0x07

        # Decode by wire type
        if wire_type == WIRE_VARINT:
            value, index = read_varint(buffer, index)

        elif wire_type == WIRE_64BIT:
            value, index = read_64bit(buffer, index)

        elif wire_type == WIRE_LENGTH_DELIMITED:
            length, index = read_varint(buffer, index)
            value_bytes = buffer[index:index+length]
            index += length

            # Try nested message parse
            # For Timestamp and strings
            try:
                # Attempt nested decode
                nested = parse_message(value_bytes, 0, len(value_bytes))
                value = nested
            except Exception:
                # Otherwise it's string
                value = value_bytes.decode("utf-8")

        else:
            raise Exception(f"Unsupported wire type: {wire_type}")

        # Store field
        fields.setdefault(field_number, []).append(value)

    return fields


# ------------------------------
# Manual ParseFromString
# ------------------------------
def manual_parse(hex_data):
    raw = binascii.unhexlify(hex_data)
    print(f"Input bytes length: {len(raw)}")

    decoded = parse_message(raw, 0, len(raw))
    return decoded


# ------------------------------
# Test with your data
# ------------------------------
if __name__ == "__main__":
    hex_data = (
        "0801120e5355535465636820486f6f6469651a63f09fa7a5204120636f7a792c2073"
        "74796c69736820686f6f64696520666561747572696e6720746865206f6666696369"
        "616c2053555354656368206c6f676f2c207065726665637420666f722073686f7769"
        "6e67207363686f6f6c207370697269742e22074170706172656c291f85eb51b8fe48"
        "40321653746179207761726d2c20737461792070726f756421420c08d4f39dc80610"
        "a0a6d69f03"
    )

    msg = manual_parse(hex_data)

    print("\nDecoded fields:")
    for field, values in msg.items():
        print(f"Field {field}:")
        for v in values:
            print("   ", v)
