from solution.solution import SelicCalc

from datetime import date


if __name__ == '__main__':
    calc = SelicCalc()

    calc.calc_amount_earned(
        start_date=date(2010, 1, 1),
        end_date=date(2021, 3, 1),
        capital=657.43,
        frequency="daily",
        save_csv=False,
    )
