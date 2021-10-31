# Cálculos DEGIRO
Cálculo simple para saber cuanto se ha ganado respecto a todo lo ingresado.

* **Valor** es lo que se pagó a DEGIRO.
* **Beneficio** es el extra que existe esa posción respecto al _Valor_
* **Gastos en compras** es lo que se ha pagado a DEGIRO para comprar las posiciones.
* **Suma de las posiciones** valor total de todas las posiciónes (la suma de todos los _Valor_)
* **Dinero ingresado en DEGIRO** la suma de todos los ingresos realizados (_Gastos en compras_ + _cash_)
* **Primer ingreso** fecha de cuando se realizó el primer movimiento de dinero a DEGIRO
* **Total en DEGIRO** es el cash más los valores de las posiciones.
* **Ganancia global** es _Total en DEGIRO_ - _Total invertido_ y ese porcentaje de ganancia.

La idea de realizar así los cálculos es tener en cuenta todas las posibles comisiones que se hayan pagado a DEGIRO,
por ejemplo, la comisión de conexión a las bolsas.

NOTA: no se tiene en cuenta si se ha realizado alguna venta.

## Ejemplo output
```
➜ python degiro.py -u USUARIO -p PASSWORD
Nombre                                        |    Valor   | Beneficio  | Beneficio %
iShares Core FTSE 100 UCITS ETF GBP Dist      |  1000.00 € |    10.00 € | 1.00%
iShares Core S&P 500 UCITS ETF USD (Dist)     |  1000.00 € |    50.00 € | 5.00%
Vanguard S&P 500 UCITS ETF USD                |  1000.00 € |    10.00 € | 1.00%

Gastos en compras: 2930.00 €
Suma de las posiciones: 3100.00 €
En cash: 170.00 €
Dinero ingresado en DEGIRO: 3100.00 €
Primer ingreso: 2021-01-01 11:11:11+01:00
Total en DEGIRO: 3170.00 €
Ganancia global: 70.00 € (2.23 %)
```
## Biblioteca degiroapi
[Parcheado](https://github.com/lolokraus/DegiroAPI/pull/16/files) para tener account_overview.
