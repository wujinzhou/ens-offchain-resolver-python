from eth_utils import keccak
from eth_abi.packed import encode_packed

BASE_NODE = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"


def to_ens_name(name: bytes) -> str:
    """
    # b'\x00\x05 23 5\x0coffchaindemo\x03eth\x00'
    # [b'', b' 23 5', b'offchaindemo', b'eth']
    """
    if not name:
        return ""
    lables = []
    i = 0
    while i + 1 < len(name):
        lable_len = name[i]
        lable = name[i + 1 : i + 1 + lable_len]
        lables.append(lable)
        i += lable_len + 1

        # set a break limit for the loop
        if len(lables) > 64:
            raise ValueError("too may lables")

    return b".".join(lables).decode()


def remove_0x(calldata: str) -> str:
    calldata = calldata.lower().strip(" ")
    if calldata.startswith("0x"):
        return calldata[2:]
    return calldata


def remove_selector(calldata: str | bytes) -> bytes:
    if isinstance(calldata, str):
        calldata = bytes.fromhex(remove_0x(calldata))[4:]
    elif isinstance(calldata, bytes):
        calldata = calldata[4:]
    return calldata


def make_message_hash(target, expiry, request, result):
    return keccak(
        encode_packed(
            ["bytes2", "address", "uint64", "bytes32", "bytes32"],
            [b"\x19\x00", target, expiry, keccak(request), keccak(result)],
        )
    )


def namehash(name: str) -> str:
    if name == "":
        return BASE_NODE.hex()
    names = name.lower().split(".")[::-1]
    node = BASE_NODE
    for n in names:
        node = keccak(node + keccak(n.encode(encoding="utf-8")))
    return node.hex()
