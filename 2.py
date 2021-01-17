import random
import pickle
import sys

def get_changed_big_order():
    untouchable = random.randint(1, 3)
    order = []
    if untouchable == 1:
        order = [0, 1, 2, 6, 7, 8, 3, 4, 5]
    elif untouchable == 2:
        order = [6, 7, 8, 3, 4, 5, 0, 1, 2]
    else:
        order = [3, 4, 5, 0, 1, 2, 6, 7, 8]
    return order

def get_changed_small_order():
    big = random.randint(0, 2)
    a = random.randint(0, 2)
    b = (a + random.randint(1, 2)) % 3
    a += 3 * big
    b += 3 * big
    order = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    order[a], order[b] = order[b], order[a]
    return order

class Game:
    def __init__(self, number_of_open_cells):
        # Генерируем начальное судоку, а затем получаем новое путем допустимых преобразований
        self.table = [[(j + 3 * i + i // 3) % 9 + 1 for j in range(9)] for i in range(9)]
        for i in range(random.randint(0, 100)):
            if bool(random.getrandbits(1)):
                self.transpose_table()
            if bool(random.getrandbits(1)):
                self.swap_big_rows()
            if bool(random.getrandbits(1)):
                self.swap_big_columns()
            if bool(random.getrandbits(1)):
                self.swap_small_rows()
            if bool(random.getrandbits(1)):
                self.swap_small_columns()
        # Теперь нужно оставить number_of_open_cells клеток видными игроку
        all_cells = [i for i in range(81)]
        random.shuffle(all_cells) # перемешаем все индексы и возьмем первые number_of_open_cells
        self.is_open = [[0 for i in range(9)] for j in range(9)] # если ноль, то не заполнена изначально
        self.game_field = [[0 for i in range(9)] for j in range(9)] # поле, которое будет видеть игрок
        for i in range(number_of_open_cells):
            pos = all_cells[i]
            y = pos // 9
            x = pos % 9
            self.is_open[y][x] = 1
            self.game_field[y][x] = self.table[y][x] 

    def transpose_table(self):
        self.table = [[self.table[i][j] for i in range(9)] for j in range(9)]

    def swap_big_rows(self):
        new_rows_order = get_changed_big_order()
        self.table = [[self.table[j][i] for i in range(9)] for j in new_rows_order]

    def swap_big_columns(self):
        new_columns_order = get_changed_big_order()
        self.table = [[self.table[j][i] for i in new_columns_order] for j in range(9)]

    def swap_small_rows(self):
        new_rows_order = get_changed_small_order()
        self.table = [[self.table[j][i] for i in range(9)] for j in new_rows_order]

    def swap_small_columns(self):
        new_columns_order = get_changed_small_order()
        self.table = [[self.table[j][i] for i in new_columns_order] for j in range(9)]


    def save(self):
        with open('game.pkl', 'wb') as file:
            pickle.dump(self, file)

    def check_end(self):
        for row in range(9):
            numbers = [0] * 10
            for column in range(9):
                x = self.game_field[row][column]
                if numbers[x] == 1 or x == 0:
                    return False
                numbers[x] = 1
        
        for column in range(9):
            numbers = [0] * 10
            for row in range(9):
                x = self.game_field[row][column]
                if numbers[x] == 1 or x == 0:
                    return False
                numbers[x] = 1
        
        for x in range(3):
            for y in range(3):
                numbers = [0] * 10
                for a in range(3):
                    for b in range(3):
                        n = self.game_field[3 * x + a][3 * y + b]
                        if numbers[n] == 1 or n == 0:
                            return False
                        numbers[n] = 1
        return True

    def set_num(self, row, column, num):
        if column < 0 or column > 8 or row < 0 or row > 8 or num < 1 or num > 9:
            raise ValueError
        if self.is_open[row][column] == 0:
            self.game_field[row][column] = num

    def display(self):
        for row in self.game_field:
            for i in row:
                print(i, end=' ')
            print()

    def get_current_game_field(self):
        return self.game_field.copy()

class Bot:
    def __init__(self, game):
        self.game = game

    def play(self):
        self.possible_numbers = [[[1, 2, 3, 4, 5, 6, 7, 8, 9] for i in range(9)] for i in range(9)]
        game_field = self.game.get_current_game_field()
        for row in range(9):
            for column in range(9):
                x = game_field[row][column]
                if x != 0:
                    self.set_number(row, column, x)
        while True:
            if self.game.check_end():
                print('Копьютер решил судоку!')
                return
            was_turn = False
            for row in range(9):
                for column in range(9):
                    if len(self.possible_numbers[row][column]) == 1:
                        was_turn = True
                        x = self.possible_numbers[row][column][0]
                        self.game.set_num(row, column, x)
                        self.set_number(row, column, x)
                        print(row + 1, column + 1, x)
                        self.game.display()
                        print()
            if not was_turn:
                print('Невозможно однозначно решить судоку.')
                return



    def set_number(self, row, column, num): # устанавливает число и пересчитывает возможные варианты для оставшихся клеток
        self.possible_numbers[row][column] = []
        for k in range(9):
            if self.possible_numbers[row][k].count(num) > 0:
                self.possible_numbers[row][k].remove(num)
            if self.possible_numbers[k][column].count(num) > 0:
                self.possible_numbers[k][column].remove(num)
        y = row // 3
        x = column // 3
        for a in range(3):
            for b in range(3):
                if self.possible_numbers[3 * y + a][3 * x + b].count(num) > 0:
                    self.possible_numbers[3 * y + a][3 * x + b].remove(num)


if __name__ == '__main__':
    print('''Введите номер режима игры:
    1. Играете вы.
    2. Играет компьютер.''')
    game_mode = int(input())    
    if game_mode == 1:
        print('''Выберите откуда взять игру:
    1. Начать новую игру
    2. Загрузить игру из файла''')
        begin_type = int(input())
        if begin_type == 1:
            print('Введите число изначально заполненных клеточек:')
            i = int(input())
            if i < 1 or i > 81:
                print('Некорректное число')
                sys.exit(1)
            game = Game(i)
        elif begin_type == 2:
            with open('game.pkl', 'rb') as file:
                game = pickle.load(file)
        else:
            print('Некорректное число')
            sys.exit(1)
        
        print('\nВводите свой ход в виде 3 чисел (Строка, Колонка, Число).')
        print('Введите слово "save", если хотите сохранить игру и выйти.')
        print('Введите слово "exit", если хотите выйти без сохранения.\n')
        while True: # Игровой цикл
            game.display()

            if game.check_end():
                print()
                print('Вы разгадали судоку!')
                sys.exit(0)

            turn = input().strip()
            if turn == 'save':
                game.save()
                sys.exit(0)
            if turn == 'exit':
                sys.exit(0)
            try:
                y, x, n = map(int, turn.split())
                game.set_num(y - 1, x - 1, n)
            except ValueError:
                print('Некорректный ход, попробуйте ещё раз')
            print()

    elif game_mode == 2:
        print('Введите число изначально заполненных клеточек:')
        i = int(input())
        if i < 1 or i > 81:
            print('Некорректное число')
            sys.exit(1)
        game = Game(i)
        print('Стартовое состояние')
        game.display()
        print()
        bot = Bot(game)
        bot.play()
    else:
        print('Некорректное число')
        sys.exit(1)
