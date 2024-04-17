import json
from abc import ABC, abstractmethod


class TypeCode:
    """
    Coin Type Index:
    https://github.com/satoshilabs/slips/blob/master/slip-0044.md
    https://github.com/ensdomains/address-encoder/blob/master/src/consts/coinTypeToNameMap.ts
    """

    BTC = 0
    LTC = 2
    DOGE = 3
    ETH = 60

    typecode = {
        BTC: "btc",
        LTC: "ltc",
        DOGE: "doge",
        ETH: "eth",
    }

    def get_symbol(code):
        return TypeCode.typecode.get(code, None)


class IDatabase(ABC):
    @abstractmethod
    def get_name(self, name_hash):
        pass

    @abstractmethod
    def get_address(self, name_hash, code):
        pass


class Database(IDatabase):
    def __init__(self, data_path) -> None:
        with open(data_path, "r") as f:
            self.db = json.load(f)

    def get_name(self, name_hash):
        return self.db.get(name_hash, {}).get("name", None)

    def get_address(self, name_hash, code):
        ticker = TypeCode.get_symbol(code)
        return self.db.get(name_hash, {}).get("address", {}).get(ticker, None)
