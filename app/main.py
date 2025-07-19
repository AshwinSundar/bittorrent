import hashlib
import json
import sys
from typing import Any, Tuple

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


def decode_bencode(bencoded_value: bytes) -> Tuple[Any, bytes]:
    '''
        Returns (value, rest)
    '''
    s = bencoded_value.decode(encoding="latin-1")

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
        bdict: dict[str, bytes] = {}
        rest = bencoded_value[1:]  # Skip the 'd' character

        # Check if it's an empty dict
        if rest[0:1] == b'e':
            return (bdict, rest[1:])

        # Parse dict elements until we hit 'e'
        while len(rest) > 0 and rest[0:1] != b'e':
            key, rest = decode_bencode(rest)
            value, rest = decode_bencode(rest)

            bdict[key.decode()] = value

        # Skip the 'e' character and return
        if rest[0:1] == b'e':
            return (bdict, rest[1:])
        else:
            raise ValueError("Dict not properly terminated with 'e'")

    raise ValueError()


def bencode(value: Any) -> bytes:
    if isinstance(value, bytes):
        value = value.decode('latin-1')

    match value:
        case str():
            length = str(len(value))
            bencoded_value = f"{length}:{value}"
            return bencoded_value.encode()

        case int():
            bencoded_value = f"i{str(value)}e"
            return bencoded_value.encode()

        case list():
            bencoded_value = "l"
            for v in value:
                bencoded_value += bencode(v).decode()

            bencoded_value += "e"
            return bencoded_value.encode()

        case dict():
            bencoded_value = "d"
            for k, v in value.items():
                bencoded_value += bencode(str(k)).decode()
                bencoded_value += bencode(v).decode()

            bencoded_value += "e"
            return bencoded_value.encode()

        case _:
            raise ValueError("This object cannot be bencoded.")


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

    elif command == "info":
        file_name = sys.argv[2]

        with open(file_name, "rb") as file:
            metainfo = file.read()
            decoded_file = decode_bencode(metainfo)
        # print("Tracker URL:", decoded_file[0]["announce"].decode())
        # print("Length:", decoded_file[0]["info"]["length"])

        # bencoded_str = bencode("test")
        # bencoded_int = bencode(24)
        # bencoded_list = bencode([1, "two", [4]])
        # bencoded_dict = bencode({"thing": "a-value"})

        # you are here - calculated sha isn't correct. see hints
        # transform the encoded values
        # if isinstance(decoded_file[0]["info"]["pieces"], bytes):
        #     decoded_file[0]["info"]["pieces"] = decoded_file[0]["info"]["pieces"].decode('latin-1')

        # if isinstance(decoded_file[0]["info"]["pieces"], bytes):
        #     decoded_file[0]["info"]["pieces"] = decoded_file[0]["info"]["pieces"].decode('latin-1')

        bencoded_info = bencode(decoded_file[0]["info"])
        hashed_info = hashlib.sha1()
        hashed_info.update(bencoded_info)
        print("Info Hash:", hashed_info.hexdigest())

    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
