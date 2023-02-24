class BoardException(Exception): # классы исключений. это вместо условий,которые отбраковывали неправильный ввод коорд. в игре крестик-нолик
    pass
class BoardOutException(BoardException): # исключение для пользователя
    def __str__(self):
        return "координаты твоего выстрела вне игрового поля"
class BoardUsedException(BoardException): # исключение для пользователя
    def __str__(self):
        return 'ты уже стрелял в эту точку'
class BoardWrong_shipException(BoardException): # исключение для размещения кораблей
    pass

class Dot: # класс точек
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other): # сравнение точек по координатам, например точка выстрела попала в точку корабля
        return self.x == other.x and self.y == other.y
    def __repr__(self): # запись точек в таком виде Dot(1, 4), такой вид можно сразу в код подставить
        return f'Dot({self.x}, {self.y})'


class Ship: # класс про корабль
    def __init__(self, bow, l, o): # задаем 3 параметра конструктора:(нос,длина,ориентация(вертик-горизон)) - корабля.
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l # длина корабля и его жизнь это одно и тоже, длина закончилась и жизни тоже
    @property # защитим наши корабли, это не просто метод, это свойства кораблей
    def dots(self): # точки корабля
        ship_dots = []
        for i in range(self.l): # проходимся циклом по длине корабля от (0) до (l - 1)
            cur_x = self.bow.x # координаты носа, от них и едем
            cur_y = self.bow.y
            if self.o == 0: # если 0, то вертикальный и значит координата x будет увеличена на 1
                cur_x += i
            elif self.o == 1: # если 1, то горизонтальный и значит координата у будет увеличена на 1
                cur_y += i
            ship_dots.append(Dot(cur_x,cur_y))
        return ship_dots
    def shooting(self, shot): # выстрел попал по кораблю
        return shot in self.dots, 'попал, стреляй еще'

class Board:
    def __init__(self, hidden = False, size = 6): # аргументы скрытое поле (игроки не должны видеть поля друг друга) и размер
        self.hidden = hidden
        self.size = size
        self.count = 0 # количество пораженных кораблей
        self.busy = [] # список где лежат занятые точки, либо кораблями , либо уже туда стреляли
        self.ships = [] # координаты всех кораблей, секретная инфа
        self.field = [[' ']*size for _ in range(size)] # генератор списка, матрица 6 на 6
    def __str__(self): # отрисовка поля
        res = ''
        res += '    1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i+1} | ' + ' | '.join(row) + ' |'
        if self.hidden: res = res.replace("■",' ') # если поле должно быть скрыто, заменяем квадратик на пробел
        return res
    def out(self, dott): # находится ли выстрел за пределами доски
        return not(0<=dott.x<self.size and 0<=dott.y<self.size) # нули нужны. точка (0,0) у нас на карте будет на месте 1-1
    def contour(self, ship, verb = False): # метод контур, заполняет все точки вокруг корабля, там не распологать новые корабли, verb - обрисовка контура "."
        near = [(-1,-1),(-1,0),(0,-1),(-1,1),(0,0),(1,-1),(1,0),(0,1),(1,1)] # список точек вокруг корабля с координатой (0,0)
        for d in ship.dots: # берем каждую точку корабля
            for dx,dy in near: # проходим по списку near
                cur = Dot(d.x + dx, d.y + dy) # сдвигаем исх точку на dx, dy
                if not(self.out(cur)) and cur not in self.busy: # если точка не вышла за границы и не занята
                    if verb:                        #нужно ли ставить точки вокруг кораблей? если карта твоя то да, если не твоя то нет
                        self.field[cur.x][cur.y] = '.' # ставим на этом месте точку, контур точками обрисовываем
                    self.busy.append(cur)           # заносим такие точки в занятые
    def add_ship(self, ship):   #  добавляем кораблики
        for d in ship.dots:
            if self.out(d) or d in self.busy: # проверяем что точка не выходит за границы и не занята
                raise BoardWrong_shipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■" # нарисуем кораблик ввиде квадратиков
            self.busy.append(d)         # сразу занесем эти точки как занятые
        self.ships.append(ship)
        self.contour(ship)
    def shot(self, d): # метод стрельба
        if self.out(d):
            raise BoardOutException() # выстрел за карту
        if d in self.busy:
            raise BoardUsedException # выстрел куда уже стрелял
        self.busy.append(d)
        for ship in self.ships: # попадание по кораблю
            if d in ship.dots:  #  можно и так ship.shooting(d):
                ship.lives -= 1
                self.field[d.x][d.y] = '◘' # пробоина в корабле, если он не 1 в длину
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабель уничтожен')
                    return False  # повтори ход
                else:
                    print('Корабель ранен')
                    return True
        self.field[d.x][d.y] = '.' # выстрел никуда не попал
        print('МиМо')
        return False
    def defeat(self): # функция о поражении, если кол пораж кораб == длине списка размещенных корабл
        return self.count == len(self.ships)
    def begin(self):  # когда начнем игру важно чтобы список бизи был пустым
        self.busy = [] # до игры тут хранились точки кораблей и контур кораблей, а теперь тут будут храниться ходы игрока

class Players: # класс игроков и комп и чел
    def __init__(self, my_board, enemy_board): # аргументы 2 доски
        self.board = my_board
        self.enemy = enemy_board
    def ask(self): # этот метод должен быть, но только у потомков этого класса, а вызов из этого класса будет ошибка
        raise NotImplementedError() # нереализованная ошибка
    def move(self):
        while True: # бесконечный цикл опроса стрельбы
            try:
                target = self.ask()
                repeat = self.enemy.shot(target) # попал, стреляй еще раз
                return repeat
            except BoardException as e: # не попал, переход хода
                print(e)

from random import randint
class AI(Players): # класс ИИ
    def ask(self):
        d = Dot(randint(0,5), randint(0,5))
        print(f'Ход компа: {d.x+1} {d.y+1}')
        return d

class User(Players): # класс пользователя
    def ask(self):
        while True:
            coordinates = input('Ход игрока:').split()
            if len(coordinates) != 2:
                print('введите 2 координаты')
                continue
            x,y = coordinates
            if not(x.isdigit()) or not(y.isdigit()):
                print('введите числа')
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1) # -1 потому что индексы у нас с 0, а поле 123456

class Game:  # класс ИГРА
    def __init__(self, size = 6):
        self.size = size
        self.list_ships_lens = [3, 2, 2, 1, 1, 1, 1]  # разновидности кораблей (1- длиной 3), (2- длиной 2), (4- длиной 1)
        player = self.random_board() # случайная доска для плеера
        comp = self.random_board()  # случайная доска для компа
        comp.hidden = True      # для доски компюьтера скрываем корабли, чтобы игрок не увидел. экран то один
        self.ai = AI(comp,player) # создаем 2-х игроков
        self.user = User(player,comp)
    def try_board(self): # попытки создания поля игры и расстановка кораблей
        board = Board(size=self.size)
        attempts = 0 # попытки создания корабля ИИ
        for l in self.list_ships_lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None # иногда при создании поля игры вылетает None, нужно еще раз запустить
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break # если корабль поставился, то цикл прерывается и делается 2-й корабль
                except BoardWrong_shipException: # если не получилось и выпало исключение, то while True запускаем снова
                    pass
        board.begin()
        return board
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board
    def greeting(self):
        print('Игра морской бой')
        print("Правила: игрок и компьютер ходят по-очереди")
        print("Человек ходит так: вводим координаты сначала номер строки, потом столба х,у")
        print(" -----------------------------------------------")
    def print_board(self):
        print('-' * 20)
        print('Доска пользователя:')
        print(self.user.board)
        print('-' * 20)
        print('Доска компа:')
        print(self.ai.board)
        print('-' * 20)
    def loop(self):
        num = 0  # номер хода
        while True:
            self.print_board()
            if num % 2 == 0: # четный ход - ход игрока
                print('Ходит пользователь!')
                repeat = self.user.move()
            else:
                print('Ходит комп:')
                repeat = self.ai.move()
            if repeat:  # нужно ли повторить ход(когда корабль поражен), если нужно то номер хода откатываем
                num -= 1 # если номер хода увеличится, то ход перейдет др игроку
            if self.user.board.count == len(self.user.board.ships): # а можно и так количество пораж кораб == len списка размещенных кораблей на доске
                self.print_board()                                  # вывод доски и после конца игры
                print('-' * 20)
                print('Компьютер выгирал!!!!')
                break
            if self.ai.board.defeat():  # количество пораженных кораблей компа, вызываем из класса Board. а можно так self.ai.board.count == 7
                self.print_board()
                print('-' * 20)
                print('Пользователь выиграл!!!!')
                break
            num += 1
    def start(self):
        self.greeting()
        self.loop()
g = Game()
g.start()






























