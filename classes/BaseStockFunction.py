class BaseStockFunction:
    TAX_RATE = 0.0025

    def __init__(self):
        pass

    def _calc_stock_count(self, amount: int, price: int) -> int:
        return amount // price

    def _calc_change_rate(self, prev_price: int, price: int) -> float:
        return (price - prev_price) / prev_price

    def _get_changed_price(self, price, change_percent: float):
        """price에서 change_percent만큼 변화한 가격"""

        return int(price * (1 + change_percent))
