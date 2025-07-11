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

    # string. returns <int> values after ':', rest
    # 5:hello = "hello"
    if s[0].isdigit():
        colon_index = s.index(":")

        size = int(bencoded_value[:colon_index])
        end_index = colon_index + 1 + size
        value = bencoded_value[colon_index + 1:end_index]

        return (value, bencoded_value[end_index:])

    # int. return int(values) after i and before e, rest
    # i42e = 42
    elif s[0] == "i":
        end_index = s.index("e")
        value = bencoded_value[1:end_index]

        return (int(value), bencoded_value[end_index + 1:])

    # list - pass everything into decode_bencode, append each result into blist until rest is empty
    # li42ee = [42]
    # l5:helloi12ee = ["hello", 12]
    # lli4eei5ee = [[4], 5]
    elif s[0] == "l":
        blist: list[bytes] = []
        rest = bencoded_value[1:]  # Skip the 'l' character

        # Check if it's an empty list
        if rest[0:1] == b'e':
            return (blist, rest[1:])

        # Parse list elements until we hit 'e'
        while len(rest) > 0 and rest[0:1] != b'e':
            value, rest = decode_bencode(rest)
            blist.append(value)

        # Skip the 'e' character and return
        if rest[0:1] == b'e':
            return (blist, rest[1:])
        else:
            raise ValueError("List not properly terminated with 'e'")

    # dictionary, pass k-v pairs into decode_bencode, push results into dictionary until rest is empty
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
