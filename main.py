import sqlite3
total_square = 812  # Общая площадь всех квартир

water = 80  # Тариф на воду
gas = 7.1  # Тариф на газ
electricity = 5.6  # Тариф на электричество

flats_ = [27.6, 34.7, 49.1, 29.0, 127.6, 63.8, 69.6, 67.7, 68.6, 73.4, 69.9, 74.8, 56.2]  # Площади квартир
persons = [0.5, 0.5, 0, 1, 0, 0, 2, 0, 0, 0, 2, 2, 4]  # Количество жильцов в квартирах
#print(sum(persons))

class workWithElectricity():
    def add_values(self):
        '''Add new values of water's counters'''
        self.value = int(input('Введите показания счетчика: '))
        self.fact_electricity = self.value - self.get_values()[2]  # Разница между новыми показаниями и старыми

        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""INSERT INTO electricity_counter VALUES(?,?,?,?)""", (
                                                                                None,
                                                                                self.date,
                                                                                self.value,
                                                                                self.fact_electricity,))

    def get_date_from_user(self):
        self.date = str(input('Введите дату: '))
        self.check()
        '''Get values of water's counter from the user'''


    def get_values(self):
        '''Get values from database'''
        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""SELECT * FROM electricity_counter ORDER BY id DESC LIMIT 1""")
            return cursor.fetchone()

    def check(self):
        date_from_the_last_row = self.get_values()[1]  # Получаем дату последней записи
        if date_from_the_last_row[3:] == self.date[3:]:
            print(f'Ты уже делал запись для счетчика электричества в этом месяце')
            return 0
        else:
            print('Такой/их квартиры/показаный еще нет')
            self.add_values()


class workWithWater():
    def add_values(self):
        '''Add new values of water's counters'''
        self.value = int(input('Введите показания счетчика: '))
        self.fact_water = self.value - self.get_values()[1]  # Разница между новыми показаниями и старыми

        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""INSERT INTO water_counter VALUES(?,?,?,?)""", (
                                                                                None,
                                                                                self.value,
                                                                                self.fact_water,
                                                                                self.date,))

    def get_date_from_user(self):
        self.date = str(input('Введите дату: '))
        self.check()
        '''Get values of water's counter from the user'''


    def get_values(self):
        '''Get values from database'''
        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""SELECT * FROM water_counter ORDER BY id DESC LIMIT 1""")
            return cursor.fetchone()

    def check(self):
        date_from_the_last_row = self.get_values()[3]  # Получаем дату последней записи
        if date_from_the_last_row[3:] == self.date[3:]:
            print(f'Ты уже делал запись для счетчика воды в этом месяце')
            return 0
        else:
            print('Такой/их квартиры/показаный еще нет')
            self.add_values()


class workWithGas():

    def get_new_values_fromUset(self):  # Получить новые значения счетчика от пользователя
        self.gas_household = int(input('Введите показания газ быт: '))
        self.gas_warm = int(input('Введите показания газ отопление: '))
        self.corrector = int(input('Введите показания корректора: '))


    def add_new_gas_value(self):  # Добавить новые значения по счетчикам
        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""INSERT INTO gas_counters VALUES(?,?,?,?,?,?,?)""", (self.gas_household,
                                                                                   self.gas_warm,
                                                                                   self.corrector,
                                                                                   self.date,
                                                                                   None,
                                                                                   self.gas_houshold_overspending,
                                                                                   self.gas_warm_overspending,))


    def get_values(self):  # Получить  последнюю запись в таблице
        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""SELECT * FROM gas_counters ORDER BY id DESC LIMIT 1""")
            return cursor.fetchone()


    def count(self):
        self.date = str(input('Введите дату: '))

        if self.check_date() == 1:  # Если я еще не вносил показания в этом месяце
            self.get_new_values_fromUset()
            old = self.get_values()
            difference_gas_houshold = self.gas_household - old[0]  # Разница показаний бытового газа между прошлыми и нынешними месяцами
            difference_gas_warm = self.gas_warm - old[1]  # Разница показаний отопительного газа между прошлыми и нынешними месяцами
            difference_corrector = self.corrector - old[2]  # Разница показаний корректора газа между прошлыми и нынешними месяцами

            self.gas_houshold_overspending = round((difference_gas_houshold*difference_corrector)/(12*(difference_gas_warm+difference_gas_houshold)))
            self.gas_warm_overspending = round(round(difference_corrector - round((difference_gas_houshold*difference_corrector)/(difference_gas_warm+difference_gas_houshold)))/812)
            print('Перерасход бытового газа равен: ', self.gas_houshold_overspending)
            print('Перерасход газ отопление равен: ', self.gas_warm_overspending)
            print('Перерасход корректора равен: ', difference_corrector)
            self.add_new_gas_value()  # Сохраняем перерасходы и новые показания в базу данных в базу данных


    def check_date(self):
        date_from_the_last_row = self.get_values()[3]  # Получаем дату последней записи
        if date_from_the_last_row[3:] == self.date[3:]:
            print('Ты уже делал запись газовых показаний в этом месяце')
            return 0
        else:
            return 1

    def count_price(self):  # Метод для рассчета оплаты для всех квартир
        gas_houshold_overspending_from_db, gas_warm_overspending_from_db = self.get_values()[5], self.get_values()[6]  # Получаем перерасход
        for i in range(13):
            print(f'Квартира номер: {i+1}, оплатить: {round((flats_[i]*gas_warm_overspending_from_db + persons[i]*gas_houshold_overspending_from_db)*gas)}')

        print(gas_houshold_overspending_from_db, gas_warm_overspending_from_db)


class Flat():
    data = ''
    name = ''
    def get_values_from_user(self):
        self.flat_number = str(input('Введите номер квартиры: '))
        self.date = str(input('Введите дату: '))
        self.name = 'flat' + self.flat_number
        self.create_database()
        if self.check() == 1:
            self.add_values()

    def add_values(self):
        self.cold_water = int(input('Введите показания холодной воды:'))
        self.hot_water = int(input('Введите показания горячей воды: '))
        self.electricity  = int(input('Введите показания электричества: '))

        self.fact_water = (self.cold_water + self.hot_water)-(self.get_values()[2]+self.get_values()[3])
        self.fact_electricity = self.electricity - self.get_values()[4]

        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""INSERT INTO {self.name} VALUES(?,?,?,?,?,?,?,?)""", (self.flat_number,
                                                                                   self.date,
                                                                                   self.cold_water,
                                                                                   self.hot_water,
                                                                                   self.electricity,
                                                                                   None,
                                                                                   self.fact_water,
                                                                                   self.fact_electricity,))

    def get_values(self):
        with sqlite3.connect(r'accounting.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""SELECT * FROM {self.name} ORDER BY id DESC LIMIT 1""")
            self.data = cursor.fetchone()
            if self.data == None:
                return [0,'',0,0,0,0,0,0,]
            else:
                return self.data


    def check(self):  # Проверяем есть ли показания за этот месяц
        date_from_the_last_row = self.get_values()[1]  # Получаем дату последней записи
        if date_from_the_last_row[3:] == self.date[3:]:
            print(f'Ты уже делал запись для квартиры-{self.flat_number} в этом месяце')
            return 0
        else:
            print('Такой/их квартиры/показаный еще нет')
            return 1


    def create_database(self): # Создаем таблицу в базе данных для каждой отдельной квартиры
        conn = sqlite3.connect(r'accounting.db')
        cur = conn.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {self.name}
        (
           flat_number TEXT,
           date TEXT UNIQUE,
           cold_water INTEGER,
           hot_water INTEGER,
           electricity INTEGER,
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           fact_water INTEGER,
           fact_electricity INTEGER
           );
        """)

def get_factwater_by_date(date):  # Получаем фактическое показание воды по дате
    with sqlite3.connect(r'accounting.db') as db:
        cursor = db.cursor()
        cursor.execute(f"""SELECT * FROM water_counter WHERE date LIKE '___{date}'""")
        return cursor.fetchone()


def get_factwater_flat_by_date(date, number):
    '''Получаем фактическое использование воды каждой квартиры'''
    with sqlite3.connect(r'accounting.db') as db:
        name = 'flat'+number
        cursor = db.cursor()
        cursor.execute(f"""SELECT * FROM {name} WHERE date LIKE '___{date}'""")
        return cursor.fetchone()[6]


def count_water_overspending():  # Расчитываем кэф перерасхода воды
    date = str(input('Введите дату за которую хотите произвести расчет: '))  # Получаем дату
    date = date[3:]  # Убираем дни недели, оставляем только месяц и год
    sum_values_from_counter_from_flat = 0
    fact_water = get_factwater_by_date(date)
    if fact_water == None:
        print('За этот месяц нет показаний для счетчика воды')
    for i in range(1,14):
        try:
            sum_values_from_counter_from_flat =+ get_factwater_flat_by_date(date, str(i))
        except:
            print(f'В квартире {i} нет показаний воды за этот период')
            break
    rate = (fact_water[2] - sum_values_from_counter_from_flat)/812
    return rate



def get_fact_values(): # Функция для получени
    # 7 - это фактический индекс показателя электричества
    # 6 - это вода fact_water
    flat = Flat()
    flat.name = 'flat' + str(10)
    print(flat.get_values()[7])
#Flat().get_values_from_user()
#workWithGas().count_price()
#workWithElectricity().get_date_from_user()
count_water_overspending()

