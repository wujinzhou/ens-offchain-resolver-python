"""
Resolver Interfaces:
https://docs.ens.domains/resolvers/interfaces
"""

from eth_abi.abi import decode
from database import TypeCode, IDatabase
from utils import to_ens_name, remove_selector, remove_0x, namehash
import logging


class Resolver:
    def __init__(self, database: IDatabase) -> None:
        self.resolver_functions = {
            "0x9061b923": self.func_0x9061b923,
            "0x3b3b57de": self.func_0x3b3b57de,
            "0xf1cb7e06": self.func_0xf1cb7e06,
            "0x59d1d43c": self.func_0x59d1d43c,
        }
        self.database = database

    def resolve(self, calldata) -> bytes:
        if isinstance(calldata, bytes):
            selector = "0x" + calldata[:4].hex()
        elif isinstance(calldata, str):
            calldata = calldata.lower().strip(" ")
            if calldata.startswith("0x"):
                selector = calldata[:10]
            else:
                selector = "0x%s" % calldata[:8]
        else:
            raise ValueError("Failed to decode selector fom %s...", calldata[:10])
        if selector in self.resolver_functions:
            return self.resolver_functions[selector](calldata)

        logging.info(f"selector {selector} is not foud in signature mapping")
        raise NotImplementedError

    def func_0x9061b923(self, calldata) -> bytes:
        """
        Entrance to subsequent resloving call
        resolve(bytes,bytes)
        """
        calldata = remove_selector(calldata)
        (name_bytes, data) = decode(["bytes", "bytes"], calldata)
        name = to_ens_name(name_bytes)
        logging.info(f"[resolve(bytes,bytes)] name:{name} hash:{namehash(name)}")
        return self.resolve(data)

    def func_0x3b3b57de(self, calldata) -> bytes:
        """
        !!! The return value needs to be 32 bytes long !!!
        Read Ethereum Address
        addr(bytes32) -> bytes32
        """
        calldata = remove_selector(calldata)
        (name_hash,) = decode(["bytes32"], calldata)
        name_hash = "0x%s" % name_hash.hex()
        name = self.database.get_name(name_hash)
        address = self.database.get_address(name_hash, TypeCode.ETH)
        logging.info(f"[addr(bytes32)] name:{name} hash:{name_hash} address:{address}")
        if address is None:
            return b"\x00" * 32
        return bytes.fromhex(remove_0x(address)).rjust(32, b"\x00")

    def func_0x59d1d43c(self, calldata):
        """
        Read Text Record
        text(bytes32,string)
        """
        logging.info(
            "[0x59d1d43c][text(bytes32,string)][Read Text Record] is not implimented"
        )
        raise NotImplementedError

    def func_0xf1cb7e06(self, calldata):
        """
        Read Multicoin Address
        "addr(bytes32,uint256)"
        https://docs.ens.domains/ensip/9
        """
        logging.info(
            "[0xf1cb7e06][addr(bytes32,uint256)][Read Multicoin Address] is not implimented"
        )
        raise NotImplementedError
