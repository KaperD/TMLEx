import csv

class Item:
    def __init__(self, date, time, price):
        self.date = date
        self.time = time
        self.price = price
        self.max_on_suffix = 0
        self.position_of_max = 0

def solve(file, start_money):
    reader = csv.DictReader(file, delimiter=',')

    list = []
    for line in reader:
        list.append(Item(line['date'], line['time'], float(line['price'])))

    max_price = 0 # текущий максимум цены на суффиксе
    position_of_max = 0

    for i in range(len(list) - 1, -1, -1):
        if list[i].price > max_price:
            max_price = list[i].price
            position_of_max = i
        list[i].max_on_suffix = max_price
        list[i].position_of_max = position_of_max

    max_new_value = start_money
    position_of_purchase = -1
    position_of_sale = -1

    for i in range(len(list)):
        new_value = list[i].max_on_suffix * (start_money // list[i].price) + start_money % list[i].price
        if new_value > max_new_value:
            max_new_value = new_value
            position_of_purchase = i
            position_of_sale = list[i].position_of_max

    if position_of_purchase == -1 and position_of_sale == -1:
        print('Невозможно увеличить стартовый капитал')
    else:
        number_of_stocks = int(start_money // list[position_of_purchase].price)
        change_of_value = number_of_stocks * (list[position_of_sale].price - list[position_of_purchase].price)
        print('Покупка:', list[position_of_purchase].date, 'Продажа:', list[position_of_sale].date, 'Изменение стоимости акций:', change_of_value)
        print('Купили', number_of_stocks, 'за:', list[position_of_purchase].price, 'Продали за:', list[position_of_sale].price)
        print('Итоговый капитал:', max_new_value)

if __name__ == '__main__':
    print('Введите начальный капитал:')
    start_money = int(input())
    csv_file = 'new.csv'
    with open(csv_file, 'r') as file:
        solve(file, start_money) 