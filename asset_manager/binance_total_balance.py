import os
import json
import matplotlib.pyplot as plt
from datetime import datetime

'''
Represents the total balance of all binance crypto assets
'''
class BinanceTotalBalance(object):
    def __init__(self):
        self.total_balance = 0
        self.total_output_file = f"data/total_balance.json"

    def add_symbol_balance(self, symbol_balance: float):
        self.total_balance += symbol_balance

    def write(self):
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        total_output = self._get_total_output()

        total_output["balances"].append({
            "timestamp": timestamp,
            "balance": self.total_balance
        })

        self._write_total_output(total_output)

    def _get_total_output(self):
        if not os.path.exists(self.total_output_file) or not os.path.isfile(self.total_output_file):
            return {
                "balances": []
            }
        else:
            with open(self.total_output_file) as f:
                return json.load(f)

    def _write_total_output(self, total_output):
        with open(self.total_output_file, "w+") as f:
            json.dump(total_output, f, indent=4)


    def to_graph(self):
        x_axis = []
        y_axis = []

        balances = self._get_total_output()["balances"]

        for entry in balances:
            y_axis.append(float(entry["balance"]))
            x_axis.append(datetime.strptime(entry["timestamp"], "%d-%m-%Y %H:%M:%S").strftime("%d.%m.%Y"))

        plt.plot(x_axis, y_axis)
        plt.title("Total Balance Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Balance")
        
        plt.savefig(f"img/total_balance-{datetime.now().strftime('%d-%m-%Y_%H_%M_%S')}")
        
        #plt.show()

        plt.clf()