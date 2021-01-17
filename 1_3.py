import csv

class Item:
    def __init__(self, date, time, price):
        self.date = date
        self.time = time
        self.price = price

def solve(file, start_money, K):
    reader = csv.DictReader(file, delimiter=',')

    list = []
    for line in reader:
        list.append(Item(line['date'], line['time'], float(line['price'])))

    list.append(Item('', '', 0.0)) # чтобы последний элемент было легче обработать на локальный максимум

    # Будем решать динамикой
    # Для начала заметим, что продавать акции имеет смысл только в локальных максимумах
    # Тогда для начала найдем и пронумеруем локальные максимумы
    # dp[i][k] = max_value, максимальный итоговый капитал, который можно получить,
    # если сделать не более k транзакций на префиксе до локального максимума с номером i
    # dp[i][k] = max(dp[i - 1][k], max_{j < i} f(dp[j][k - 1], j, i))
    # где f(start_value, start_position, position_of_sale) -- функция, которая максимизирует прибыль,
    # когда ей разрешено сделать одну транзакцию на отрезке [start_position, position_of_sale], 
    # и продажа должна произойти ровно в position_of_sale
    # Эта функция должна просто искать минимум на отрезке [start_position, position_of_sale]
    # и покупать в этот минимум, и продавать в position_of_sale
    # Решение работает за O(n^2), где n -- число строк в таблице, но можно применить оптимизацию:
    # При поиске max_{j < i} f(dp[j][k - 1], j, i) можно проходить не по всем j < i, а только по j,
    # при которых минимум на отрезке от j до i уменьшается по сравнению с предыдушим минимумом 
    # (если мы перешли от одного j к другому и минимум на отрезке не изменился, то ответ точно не улучшится)
    # поэтому будет для каждого локального максимума i хранить номер предыдущего локального максимума j,
    # такой, что min_on_segment[j + 1] < min_on_segment[i + 1]
    # и будем ходить по этим номерам, так как если мы могли пропустить какой-то максимум j,
    # то и дальше мы можем его пропускать

    min_on_segment = [0] # min_on_segment[i] -- это минимум между i-1 и i локальными максимами
    pos_of_local_max = [-1] # по номеру локального максимума получить номер в исходном списке всех измерений 
    dp = [[start_money] * (K + 1)] # номера локальных максимумов начинаются с 1, для этого добавляем во все списки фиктивные элементы
    prev_sale_pos = [[-1] * (K + 1)] # когда была совершена предыдущая продажа
    
    last_sale_pos = [[-1] * (K + 1)] # когда была совершена последняя продажа

    max_value = start_money # максимальный конечный капитал
    pos_of_max_value = -1 # при каком локальном максимуме был достигнут этот max_value

    number_of_local_max = 0 # количество локальных максимумов

    prev = [-1] * len(list) # будем пропускать максимумы, отрезок после которых не уменьшает минимум

    current_min = list[0].price # поддерживаем минимум между предыдущим локальным максимумом и следующим

    ten_percent = int(len(list) // 10)

    for i in range(1, len(list) - 1):
        if (i - 1) % ten_percent == 0:
            print(f'Выполнено {((i - 1) // ten_percent) * 10}%')

        if list[i].price < current_min:
            current_min = list[i].price

        if list[i].price >= list[i - 1].price and list[i].price > list[i + 1].price: # слева может быть нестрогое равенство, справа строгое
            # нашли локальный максимум
            min_on_segment.append(current_min)
            current_min = list[i].price # нужно забыть про уже пройденные элементы и начать считать минимум на новом отрезке

            # добавляем элементы, которые сейчас будем вычислять
            dp.append([start_money] * (K + 1))
            prev_sale_pos.append([-1] * (K + 1))
            last_sale_pos.append([-1] * (K + 1))

            number_of_local_max += 1

            pos_of_local_max.append(i)

            prev[number_of_local_max] = number_of_local_max - 1 # изначально указываем на предыдущий максимум, так как его точно нужно полетить

            min_on_suffix = min_on_segment[-1] # изначально берем минимум между текущим локальным максимумом и предыдущим
            j = number_of_local_max - 1
                
            while True:
                for k in range(1, K + 1):
                    if dp[j][k] > dp[number_of_local_max][k]: # может быть в текущий максимум менее выгодно продавать
                        dp[number_of_local_max][k] = dp[j][k]
                        last_sale_pos[number_of_local_max][k] = last_sale_pos[j][k]
                        if k > 1:
                            prev_sale_pos[number_of_local_max][k] = prev_sale_pos[j][k]

                    start_value = dp[j][k - 1]
                    number_of_stocks = start_value // min_on_suffix
                    end_value = number_of_stocks * list[i].price + start_value % min_on_suffix

                    if end_value > dp[number_of_local_max][k]:
                        dp[number_of_local_max][k] = end_value
                        if k > 1:
                            prev_sale_pos[number_of_local_max][k] = j
                        last_sale_pos[number_of_local_max][k] = number_of_local_max
                if prev[j] == -1: # значит все предыдущие значения больше текущего минимума
                    break
                cur = j
                while True: # ищем первое число, которое меньше текущего минимума (ищем отрезок, в котором он есть)
                    j = prev[j]
                    if min_on_segment[j + 1] < min_on_suffix: # нашли 
                        min_on_suffix = min_on_segment[j + 1]
                        prev[cur] = j # сохранили переход
                        break
                    else:
                        if prev[j] == -1:
                            break
                if prev[j] == -1:
                    break
            

            if dp[number_of_local_max][K] > max_value: # ищем оптимальный ответ, он точно где-то есть, значит мы его найдем
                max_value = dp[number_of_local_max][K]
                pos_of_max_value = number_of_local_max

    ans = []

    while True:
        pos_of_min = -1
        left = 0
        right = pos_of_local_max[last_sale_pos[pos_of_max_value][K]]
        if not (prev_sale_pos[pos_of_max_value][K] == -1):
            left = pos_of_local_max[prev_sale_pos[pos_of_max_value][K]]
        minimum = list[left].price
        for i in range(left, right): 
            # мы знаем, когда была совершена текущая и предудущая продажа,
            # поэтому осталось найти минимум между ними, в нем была совершена покупка
            if list[i].price < minimum:
                minimum = list[i].price
                pos_of_min = i
        ans.append((pos_of_min, right)) # пара -- когда купили и когда продали
        if prev_sale_pos[pos_of_max_value][K] == -1:
            break
        pos_of_max_value = prev_sale_pos[pos_of_max_value][K]
        K = K - 1
        
    i = 1
    for (a, b) in reversed(ans):
        print(i)
        i += 1
        number_of_stocks = int(start_money // list[a].price)
        change_of_value = number_of_stocks * (list[b].price - list[a].price)
        print('Покупка:', list[a].date, 'Продажа:', list[b].date, 'Изменение стоимости акций:', change_of_value)
        print('Купили', number_of_stocks, 'акций за:', list[a].price, 'Продали за:', list[b].price)
        start_money += change_of_value
        print()
    print('Итоговый капитал:', max_value)
    assert(max_value == start_money)





if __name__ == '__main__':
    print('Введите начальный капитал:')
    start_money = int(input())
    print('Введите допустимое количество транзакций:')
    K = int(input())
    csv_file = 'new.csv'
    with open(csv_file, 'r') as file:
        solve(file, start_money, K)