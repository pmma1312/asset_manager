from asset_manager.binance_config import BinanceConfig
from asset_manager.binance_asset import BinanceAsset
from asset_manager.binance_total_balance import BinanceTotalBalance
from binance import Client
from colorama import init, Fore
from asset_manager.util.util import Util

'''
Helper class to run through the process of fetching necessary data
'''
class AssetManager(object):
    def __init__(self, binance_config_path: str, pair_asset: str, debug_mode=False):
        init()

        self.binance_config = BinanceConfig(binance_config_path)
        self.binance_total_balance = BinanceTotalBalance()
        self.debug_mode = debug_mode
        self.pair_asset = pair_asset
        self.ignore_assets = [ self.pair_asset ] # Add assets here to ignore them => we always have to ignore the pair_asset
        self.client = Client(self.binance_config.api_key, self.binance_config.api_secret)
        assets = self.client.get_account()

        # Load all assets that have a non zero balance and are
        # not in the "asset blacklist"
        self.assets = []

        for asset in assets["balances"]:
            free = float(asset["free"])

            if free > 0 and not asset["asset"] in self.ignore_assets:
                self.assets.append({
                    "asset": asset["asset"],
                    "free": free
                })
            
    def run(self):
        for asset in self.assets:
            binance_asset = BinanceAsset(asset["asset"], asset["free"], self.pair_asset, self.debug_mode)

            binance_asset.write(self.client)

            self.binance_total_balance.add_symbol_balance(binance_asset.symbol_balance)
            
        self.binance_total_balance.write()

        self.print(f"Total Balance: {Util.round(self.binance_total_balance.total_balance)} USDT")
        self.print("")

    def calculate_profits_from_inital_per_asset(self):
        for asset in self.assets:
            binance_asset = BinanceAsset(asset["asset"], asset["free"], self.debug_mode)

            asset_data = binance_asset.load_asset_data()

            if len(asset_data) < 1:
                self.print(f"[?] Skipping asset {binance_asset.asset}, no data available")
                continue

            initial_asset_data = asset_data[0]["balance"]
            last_asset_data = asset_data[len(asset_data) - 1]["balance"]

            is_at_loss = last_asset_data < initial_asset_data

            if is_at_loss:
                text = "Loss"
            else:
                text = "Profit"

            amount = Util.round(last_asset_data - initial_asset_data)
            percent = Util.round(((last_asset_data - initial_asset_data) / initial_asset_data) * 100) # We don't care about decimals

            color = Fore.RED if is_at_loss else Fore.GREEN

            print("+=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=+")
            print(f"[{binance_asset.asset}]")
            print(f"Inital Captured Value: {Util.round(initial_asset_data)} USDT") 
            print(f"Last Captured Value: {Util.round(last_asset_data)} USDT")         
            print(f"{color}{amount}{Fore.RESET} USDT | {color}{percent}{Fore.RESET}%")
            print(f"Currently at {color}{text}{Fore.RESET}")
            print("+=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=+")  
            print("")

    def print(self, text: str):
        if self.debug_mode:
            print(text)