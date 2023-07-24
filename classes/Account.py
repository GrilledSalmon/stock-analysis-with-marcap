from .BaseStockFunction import BaseStockFunction

class Account(BaseStockFunction):
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.stocks = {}
        self.transaction_history = []

        # transaction_history 요소 예시 : {'date': 2023-07-22, 'stock_name':'삼성전자', 'price':1000, 'count':10}

    def show_account(self):
        print(f"이름: {self.name}")
        print(f"잔고: {self.balance}원")
        print(f"보유 주식: {self.stocks}")

    def _record_transaction(self, date, stock_name, price, count):
        self.transaction_history.append(
            {"date": date, "stock_name": stock_name, "price": price, "count": count}
        )

    def _initialize_stock(self, stock_name: str) -> None:
        self.stocks[stock_name] = {"count": 0, "purchase_amount": 0}

    def get_avergae_purchase_price(self, stock_name: str) -> float:
        """평균 매입 단가 구하는 함수"""
        if stock_name not in self.stocks or self.stocks[stock_name]["count"] == 0:
            raise Exception(f"갖고 있는 {stock_name} 주식이 없습니다.")
        return (
            self.stocks[stock_name]["purchase_amount"]
            / self.stocks[stock_name]["count"]
        )

    def get_earning_rate(self, stock_name: str, now_price: int) -> float:
        """수익률 계산"""
        average_purchase_price = self.get_avergae_purchase_price(stock_name)
        return self._calc_change_rate(average_purchase_price, now_price)

    def buy_stock(self, stock_name: str, price: int, count: int):
        if self.balance < price * count:
            raise Exception("잔액이 부족합니다.")
        if stock_name not in self.stocks:
            self._initialize_stock(stock_name)
        buy_amount = price * count
        self.stocks[stock_name]["count"] += count
        self.stocks[stock_name]["purchase_amount"] += buy_amount
        self.balance -= buy_amount

    def sell_stock(self, stock_name: str, price: int, count: int):
        if stock_name not in self.stocks:
            raise Exception("해당 주식이 없습니다.")

        remain_stock_count = self.stocks[stock_name]["count"]
        if remain_stock_count <= count:
            self.stocks[stock_name]["count"] = 0
            self.stocks[stock_name]["purchase_amount"] = 0
            self.balance += price * remain_stock_count * (1 - self.TAX_RATE)
            if remain_stock_count == count:
                print(f"{stock_name} 주식을 {remain_stock_count}개 전량 매도했습니다.")
            else:
                print(
                    f"{stock_name}의 보유량이 부족합니다. {count}개가 아닌 {remain_stock_count}만큼 보유수량을 전량 매도합니다."
                )
        else:
            sell_amount = price * count
            self.stocks[stock_name]["count"] -= count
            self.stocks[stock_name]["purchase_amount"] -= sell_amount
            self.balance += sell_amount * (1 - self.TAX_RATE)

    def sell_every_stock(self, stock_name, price):
        if stock_name not in self.stocks:
            raise Exception("해당 주식이 없습니다.")
        self.sell_stock(stock_name, price, self.stocks[stock_name]["count"])


if __name__ == "__main__":
    yoonwoo = Account("yoonwoo", 1000000)
    yoonwoo.show_account()
