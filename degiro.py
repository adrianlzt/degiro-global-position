#!/usr/bin/env python

import sys
import getpass
import argparse
import logging

from datetime import datetime

import degiroapi
from degiroapi.utils import pretty_json

FORMAT = "[%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger(__name__)


class Main:
    def __init__(self, args=False):
        self.args = args
        self.degiro = degiroapi.DeGiro()
        self.degiro.login(args.username, args.password)

    def run(self):
        logger.info(sys._getframe().f_code.co_name)

        portfolio, total_buyed, sum_positions, cash, total_payed_to_degiro, first_date = self.analyze_position()

        print(f'{"Nombre":45} | {"Valor":>8}   | {"Beneficio":>8}  | Beneficio %')
        for name,data in portfolio.items():
            print(f'{name:45} | {data["value"]:>8.2f} € | {data["beneficio"]:>8.2f} € | {data["beneficio_pct"]*100:>4.2f}%')

        print(f"\nGastos en compras: {total_buyed:.2f} €\nSuma de las posiciones: {sum_positions:.2f} €\nEn cash: {cash:.2f} €")

        print(f"Dinero ingresado en DEGIRO: {total_payed_to_degiro:.2f}")
        print(f"Primer ingreso: {first_date}")

        global_net = sum_positions+cash
        print(f"Total en DEGIRO: {(sum_positions+cash):.2f} €")

        gain_net = global_net-total_payed_to_degiro
        gain_net_pct = gain_net/total_payed_to_degiro
        print(f"Ganancia global: {gain_net:.2f} € ({gain_net_pct*100:.2f} %)")

    def analyze_position(self):
        """
        Explicación de los valores retornados:
          * calculated_portfolio: por producto, su valor actual y el beneficio (respecto a lo que pagué a DEGIRO por esa posición)
          * total_buyed: la suma de todas las transacciones de compra realizadas
          * sum_positions: la suma de los valores de las posiciones
          * cash: valor del dinero líquido almacenado en DEGIRO
          * total_payed_to_degiro: suma todos los ingresos realizados a DEGIRO
          * open_date: fecha del primer ingreso
        """
        overview = self.degiro.account_overview(datetime(2019, 1, 1), datetime.now())
        portfolio = self.degiro.getdata(degiroapi.Data.Type.PORTFOLIO, True)
        transactions = self.degiro.transactions(datetime(2019, 1, 1), datetime.now())

        # sumamos todo el dinero ingresado en degiro
        total_payed_to_degiro = 0
        first_transaction = datetime.strptime(overview["cashMovements"][0]['date'], "%Y-%m-%dT%H:%M:%S%z")
        for o in overview["cashMovements"]:
            if o["type"] == "CASH_TRANSACTION" and (o["description"] == "flatex Deposit" or o["description"] == "Ingreso"):
                total_payed_to_degiro += o["change"]
                d = datetime.strptime(o['date'], "%Y-%m-%dT%H:%M:%S%z")
                if d < first_transaction:
                    first_transaction = d

        # Agrupar compras por id
        # Tendremos una key por cada producto con el total de gasto realizado para comprar ese producto (impuestos incluídos)
        buy_transactions = {}

        total_buyed = 0
        for t in transactions:
            logger.info(f"transaction: {t}")
            id = t["productId"]
            if t["buysell"] != "B":
                raise Exception("no está implementada la lógica de venta")

            total_buyed += -t["totalPlusFeeInBaseCurrency"]

            if id in buy_transactions.keys():
                buy_transactions[id] += -t["totalPlusFeeInBaseCurrency"]
            else:
                buy_transactions[id] = -t["totalPlusFeeInBaseCurrency"]

        logger.debug(f"buy_transactions: {buy_transactions}")
        logger.debug(f"portfolio: {portfolio}")

        # Por cada posición del portfolio, calculamos el total ganado y el porcentaje.
        # Añadimos ese cálculo al portfolio
        calculated_portfolio = {}
        sum_positions = 0
        cash = 0
        for p in portfolio:
            logger.info(f"portfolio: {p}")
            id = p["id"]

            if p["positionType"] == "PRODUCT":
                # En un sitio nos dan el id como int y en otro como str
                id = int(id)
                product_name = self.get_product_name(id)
                value = p["value"]
                calculated_portfolio[product_name] = {
                    "value": value,
                    "beneficio": value - buy_transactions[id],
                    "beneficio_pct": (value/buy_transactions[id])-1,
                }
                sum_positions += value
            elif p["positionType"] == "CASH":
                cash = p["value"]

        return calculated_portfolio, total_buyed, sum_positions, cash, total_payed_to_degiro, first_transaction

    def get_product_name(self, product_id):
        product = self.degiro.product_info(product_id)
        return product["name"]


def parse_args(argv):
    p = argparse.ArgumentParser(description='DEGIRO.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                   default=False,
                   help="dry-run - don't actually make any changes")
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument("-u", "--username", action="store", required=True)
    p.add_argument("-p", "--password", action="store", default=None)

    args = p.parse_args(argv)

    if args.password is None:
        args.password = getpass.getpass()

    return args

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        logger.setLevel(logging.INFO)
    main = Main(args)
    main.run()
