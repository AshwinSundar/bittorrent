import json
import sys
from typing import Any

# import bencodepy - available if you need it!
# import requests - available if you need it!

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"
# def decode_bencode(bencoded_value):
#     if chr(bencoded_value[0]).isdigit():
#         first_colon_index = bencoded_value.find(b":")
#         if first_colon_index == -1:
#             raise ValueError("Invalid encoded value")
#         return bencoded_value[first_colon_index+1:]
#     else:
#         raise NotImplementedError("Only strings are supported at the moment")


def decode_bencode(bencoded_value: bytes) -> (Any, bytes):
    '''
        Returns (value, rest)
    '''
    s = bencoded_value.decode()

    #  string. returns <int> values after ':', rest
    if s[0].isdigit():
        colon_index = s.index(":")

        size = int(bencoded_value[:colon_index])
        end_index = colon_index + 1 + size
        value = bencoded_value[colon_index + 1:end_index]

        return (value, bencoded_value[end_index:])

    #  int. return int(values) after i and before e, rest
    elif s[0] == "i":
        end_index = s.index("e")
        value = bencoded_value[1:end_index]

        return (value, bencoded_value[end_index + 1:])

    # list - pass everything into decode_bencode, append each result into blist until rest is empty
    elif s[0] == "l":
        blist: list[bytes] = []
        value, rest = decode_bencode(bencoded_value[1:-1])
        blist.append(value)
        while len(rest) > 0:  # this may be wrong...nested loops not working properly here. everything else seems to work though. you are close!
            value, rest = decode_bencode(rest)
            blist.append(value)

        return (blist, rest)

    elif s[0] == "d":
        pass

    raise ValueError()


def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        print(json.dumps(decode_bencode(bencoded_value)[0], default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
