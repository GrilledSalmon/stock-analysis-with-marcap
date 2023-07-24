from .BaseStockFunction import BaseStockFunction
from .Account import Account
import pandas as pd


class Strategy(BaseStockFunction):
    """전략의 이름과 기간, 초기 예산을 입력하면 전략을 생성
    buy_percent는 지금 전략대로라면 음수로 입력해야 함"""

    def __init__(
        self,
        name: int,
        strategy_budget: int,
        divide_number: int,
        buy_percent: float,
        sell_percent: float,
        profit_limit_percent: float,
        stock_name: str,
        df: pd.DataFrame,
        account: Account,
    ):
        self.name = name
        self.strategy_budget = strategy_budget
        self.std_amount = strategy_budget // divide_number
        self.divide_number = divide_number
        self.buy_percent = buy_percent
        self.sell_percent = sell_percent
        self.profit_limit_percent = profit_limit_percent
        self.stock_name = stock_name
        self.target_df = df[df["Name"] == stock_name]
        self.account = account

    def show_strategy(self):
        print(f"전략 이름: {self.name}")
        print(f"전략 예산: {self.strategy_budget}")
        print(f"일별 예산: {self.std_amount}")
        print(f"분할 매수 횟수: {self.divide_number}")
        print(f"매수 기준 상승률: {self.buy_percent}")
        print(f"매도 기준 하락률: {self.sell_percent}")
        print(f"전체 익절 상한 수익률: {self.profit_limit_percent}")
        print(f"매매 대상 주식: {self.stock_name}")
        print(f"매매 대상 주식 데이터: {self.target_df.head(3)}")

    def _get_day_data(self, index: int):
        day_data = self.target_df.iloc[index]
        return day_data

    def _get_prev_price_data(self, index: int):
        if index < 0:
            raise Exception("index가 0보다 작을 수 없습니다.")
        if index == 0:
            raise Exception("index가 0입니다.")
        day_data = self._get_day_data(index - 1)
        prev_open, prev_close, prev_high, prev_low = (
            day_data["Open"],
            day_data["Close"],
            day_data["High"],
            day_data["Low"],
        )
        return prev_open, prev_close, prev_high, prev_low

    def _get_now_price_data(self, index: int):
        if index < 0:
            raise Exception("index가 0보다 작을 수 없습니다.")
        day_data = self._get_day_data(index)
        open, close, high, low = (
            day_data["Open"],
            day_data["Close"],
            day_data["High"],
            day_data["Low"],
        )
        return open, close, high, low

    def _get_buy_price(self, prev_close: int) -> int:
        """전날 종가보다 buy_percent만큼 낮은 가격"""
        return self._get_changed_price(prev_close, self.buy_percent)

    def _get_sell_price(self, prev_close: int) -> int:
        """전날 종가보다 sell_percent만큼 높은 가격"""
        return self._get_changed_price(prev_close, self.sell_percent)

    def first_buy_strategy(self, index):
        open, close, high, low = self._get_now_price_data(index)
        count = self._calc_stock_count(self.std_amount, close)
        self.account.buy_stock(self.stock_name, close, count)

    def buy_strategy(self, index: int):
        prev_open, prev_close, prev_high, prev_low = self._get_prev_price_data(index)
        open, close, high, low = self._get_now_price_data(index)
        min_change_rate = self._calc_change_rate(prev_close, low)
        if min_change_rate <= self.sell_percent:
            buy_price = self._get_buy_price(prev_close)
            count = self._calc_stock_count(self.std_amount, buy_price)
            self.account.buy_stock(self.stock_name, buy_price, count)

    def sell_strategy(self, index: int):
        prev_open, prev_close, prev_high, prev_low = self._get_prev_price_data(index)
        open, close, high, low = self._get_now_price_data(index)
        max_change_rate = self._calc_change_rate(prev_close, high)
        max_earning_rate = self.account.get_earning_rate(
            self.stock_name, high
        )  # high일 때 현재 주식 수익률

        # 수익률이 profit_limit_percent 이상이면 전량 매도
        if max_earning_rate >= self.profit_limit_percent:
            average_purchase_price = self.account.get_avergae_purchase_price(
                self.stock_name
            )
            sell_price = self._get_changed_price(
                average_purchase_price, self.profit_limit_percent
            )
            self.account.sell_every_stock(self.stock_name, sell_price)
        elif max_change_rate > self.sell_percent:
            sell_price = self._get_sell_price(prev_close)
            count = self._calc_stock_count(self.std_amount, sell_price)
            self.account.sell_stock(self.stock_name, sell_price, count)
