# BitTorrent

## Concepts

**bencode**

- encoding format used by BitTorrent protocol.
- support 4 data types - string, int, list, dict
    - strings are encoded as `<byte_length>:<contents>`. e.g. `5:hello`, `4:🙂`
    - integers are encoded as `i<value>e`. e.g. `i42e`
    - lists are encoded as `l<el1><el2>...<elN>e`. e.g. `l5:helloi14ee`, `le` (empty list [])
    - dictionaries are encoded as `d<k1><v1><k2><v2>..<kN><vN>e, e.g. `d1:ai42e1bi52ee` ({"a": 42, "b": 52}), `de` (empty dict {})
