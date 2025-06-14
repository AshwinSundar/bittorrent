import json
import sys

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


def decode_bencode(bencoded_value):
    first_char = chr(bencoded_value[0])
    match first_char:
        # strings
        case first_char if first_char.isdigit():
            first_colon_index = bencoded_value.find(b":")
            if first_colon_index == -1:
                raise ValueError(f"Invalid encoded string value - Did not find ':' after integer. Given: {bencoded_value}")

            length = int("".join([chr(b) for b in bencoded_value[:first_colon_index]]))

            if length != len(bencoded_value[first_colon_index + 1:]):
                raise ValueError(f"Invalid encoded string value - length {length} does not match size of value. Given: {bencoded_value}")

            value = [chr(b) for b in bencoded_value[first_colon_index + 1:first_colon_index + 1 + length]]
            return bencoded_value[first_colon_index + 1:]

        # digits
        case "i":
            if chr(bencoded_value[-1]) != "e":
                raise ValueError(f"Invalid encoded value. Expected i<int>e, got: {bencoded_value}")

            # may be improved...
            if any([not (chr(v).isdigit() or chr(v) == "-") for v in bencoded_value[1:-1]]):
                raise ValueError(f"Invalid encoded value. Expected i<int>e, got: {bencoded_value}")

            return int("".join([chr(v) for v in bencoded_value[1:-1]]))

        # lists
        case "l":
            if chr(bencoded_value[-1]) != "e":
                raise ValueError(f"Invalid encoded value. Expected l<el1><el2>...<elN>e, got: {bencoded_value}")

            # print([print(i, chr(val)) for i, val in enumerate(bencoded_value[1: -1], start = 1)])
            # discards first 'l' and last 'e'
            for i, val in enumerate(bencoded_value[1:-1]):
                ch = chr(val)
                print(ch)
                pass



            # YOU ARE HERE
            # probably want to use recursion?
            # identify each element
            # decode each element
            # put it back together in a list


        case _:
            raise NotImplementedError("Type not implemented.")


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

        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
