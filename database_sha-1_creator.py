import sqlite3 # Для создания SQL таблицы
import os # Для сичтывания файлов в директории

###
###
###
def SHA_1_hashing(inserting_text):
    def bytemove(a, n):  # битовый сдвиг на n позиций
        return ((a << n) | (a >> (32 - n))) & 0xffffffff
        # 0xffffffff - int 32-й степени двойки, то есть числа меньше 4 294 967 296

    def fill_data(m):  # Заполнение исходного текста в битах до кратности 512 битов
        n = m
        while (len(n)) % 512 != 448:  # Заполняем пустое пространство нулями
            n += '0'
        n += '{0:064b}'.format(len(m) - 1)  # Добавляем начальную длину входящего слова
        return n

    def chunk_create(m, n):  # Создание массива/массивов по n символов в каждом
        lst = []
        slice = ''  # Вставляемая в массив группа элементов
        for i in range(len(m)):
            slice += m[i]
            if len(slice) == n:
                lst.append(slice)
                slice = ''
        return lst

    def TEMP(A, B, C, D, E, f, wt, kt):
        temp = bytemove(A, 5) + f + E + kt + wt & 0xffffffff  # Получаем значение SHA
        return temp

    def main_hash(m):

        h0 = 0x67452301;
        h1 = 0xEFCDAB89;
        h2 = 0x98BADCFE;
        h3 = 0x10325476;
        h4 = 0xC3D2E1F0

        text = ''
        for i in range(len(m)):
            text += '{0:08b}'.format(ord(m[i]))  # Заполняем text символами из m, переведёнными в двоичный код
        text += '1'
        scnd_text = fill_data(text)  # Дополнение до длины, кратной 512
        for chnk in chunk_create(scnd_text, 512):  # Берём блок на 512 символов = chnk
            words = chunk_create(chnk, 32)  # Разбиваем блок на слова по 32 символа
            w = [0] * 80  # Список слов после трансформации (в виде цифр)
            for i in range(16):  # первые 16 слов
                w[i] = int(words[i], 2)  # вставляем значение слова + переводим из двоичного кода
            for i in range(16, 80):  # Оставшиеся слова
                w[i] = bytemove((int(w[i - 3]) ^ int(w[i - 8]) ^ int(w[i - 14]) ^ int(w[i - 16])), 1)  # Танцы с бубном

            A = h0
            B = h1
            C = h2
            D = h3
            E = h4

            for t in range(0, 80):  # циклические обработки всего дела
                if t >= 0 and t <= 19:
                    f = (B & C) | ((~B) & D)
                    kt = 0x5A827999  # 2^30 * sqrt(2)
                elif t >= 20 and t <= 39:
                    f = B ^ C ^ D
                    kt = 0x6ED9EBA1  # 2^30 * sqrt(3)
                elif t >= 40 and t <= 59:
                    f = (B & C) | (B & D) | (C & D)
                    kt = 0x8F1BBCDC  # 2^30 * sqrt(5)
                elif t >= 60 and t <= 79:
                    f = B ^ C ^ D
                    kt = 0xCA62C1D6  # 2^30 * sqrt(10)

                temp = TEMP(A, B, C, D, E, f, w[t], kt)  # Один раунд обработки
                E = D  # Так и не разобрался как внутри функции переназначать переменные, поэтому выдвинул сюда
                D = C
                C = bytemove(B, 30)
                B = A
                A = temp  # Переназначение переменных проводим только после действия

        h0 = str(hex(h0 + A & 0xffffffff)[2:])
        h1 = str(hex(h1 + B & 0xffffffff)[2:])
        h2 = str(hex(h2 + C & 0xffffffff)[2:])
        h3 = str(hex(h3 + D & 0xffffffff)[2:])
        h4 = str(hex(h4 + E & 0xffffffff)[2:])
        # Складываем первоначальный h и полученное значение его буквы в int^32, переводим в hexademical —> получаем 1 из 5-ти элементов финального хеша
        # Если правильно понимаю и помню h0-4 - это элементы финальной части нашего хеша, которые надо просто строками сложить
        fin = h0 + h1 + h2 + h3 + h4
        print(fin)
        return fin
        # print("input text which you wanna hash")
        #m = str(input())  # слово
    m = inserting_text
    return main_hash(m) #
# В представлении не нуждается
###
###
###

def database_create(base_name): # Создание базы
    data_con = sqlite3.connect(base_name) #Создаём подключение к базе
    cursor = data_con.cursor() # Берём объект cursor
    # print("Connection done")
    try:
        table_create = ("""CREATE TABLE file_list\
                       (path TEXT,
                        filename TEXT,
                        hashes TEXT)""")
        # Задаём параметры таблицы
        cursor.execute(table_create)
        data_con.commit() # Подтверждаем действие в базе
        print("Table and Database created")
    except:
        print("Table is not created or already exist")
    return data_con

def data_insert(path, filename, hash, data_con): # Вставка информации в базу
    cursor = data_con.cursor()
    try:
        sqlite_insert = """INSERT INTO file_list \
                        (path, filename, hashes) 
                        VALUES
                        (?, ?, ?)"""
        inserting_tuple = (path, filename, hash) # Создаём кортеж значений, которые будут вставляться в базу
        cursor.execute(sqlite_insert, inserting_tuple)
        data_con.commit() # !!! НЕ ЗАБЫТЬ ПОДТВЕРДИТЬ ДЕЙСТВИЕ В БАЗЕ
        cursor.close()
    except sqlite3.Error as mistake:
        print("Mistake while adding of information", mistake)

def data_check(data_con, hash, filename): # Проверяет наличие хеша в базе
    cursor = data_con.cursor()
    cursor.execute("SELECT * FROM file_list")
    boolean = False # Булевая переменная для подтверждения наличия/отсутствия хеша в базе
    for chck_hash in cursor.fetchall(): # Перебором сверяется полученный хеш и хеши из базы
        if chck_hash[2] == hash:
            # print("This hash exist:", hash, "for", filename)
            boolean = True
            return False
    if boolean == False:
        return True # boolean = False означает что хеша и файла нет в базе

def file_reader(directory, name):
    filetext = ''
    if os.path.isfile(directory+"\\"+name) == True: # Проверяем файл на тот факт что это файл
        try:
            filetext = open(directory+"\\"+name, "rb") # Открываем в бинарном виде и переводим все внутренности в строку
            filetext = str(filetext.read())
            if len(filetext) < 20000:
                return filetext
            else:
                return name
        except:
            print("error with", name) # На всякий случай, если файл не открылся
            return name # Практика показала что такого не было не разу
    else:
        print("error with", name) # В случае если не файл - пропускаем всё это дело
        return False

def database_filler(dir, files, data, buffer_back, first_dir, wrong, wrong_paths, base_name):
    # dir - директория, в которой мы сейчас находимся
    # files - файлы, находящиеся в директории
    # buffer_back - директория, предыдущая текущей (изначально не существует)
    # first_dir - начальная директория, из которой нельзя выходить во внешний мир
    # wrong - имя файла (директории), к которой нельзя прикасаться
    # wrong_paths - список папок, которые нам нельзя трогать (Они уже пройдены и хешированы)
    # Рекурсивный алгоритм для передвижения по директориям и заполнения базы. Принцип работы объяснять отказываюсь
    for filename in files: # Берём имя файла
        boolean = True
        if filename == wrong or filename == base_name:
            boolean = False
            pass
        else:
            try:
                if (dir+'/'+filename) in wrong_paths: # Встретили знакомый адрес –> пропустили его
                    pass
                else:
                    file = os.listdir(dir + '/' + filename) # Создаём новый адрес каталога
                    buffer_back = dir # Создаём буфферное значение чтобы потом можно было вернуться
                    return database_filler(dir + '/' + filename, file, data, buffer_back, first_dir, wrong, wrong_paths, base_name)
                    # Рекурсия запускает сама себя с новыми параметрами (Войдя в более глубокую папку)
            except:
                if boolean == True:
                    firstname = filename
                    filename = file_reader(dir, filename)
                    hash_summ = SHA_1_hashing(filename) # Берём хеш от файла
                    if data_check(data, hash_summ, firstname) == True: # Проверяем наличие в базе
                        data_insert(dir, firstname, hash_summ, data) # При отсутствии вставляем

    if dir == first_dir: # Проверяем совпадение текущей директории с начальной
        return 0
    file = os.listdir(buffer_back) # Берём список файлов в buffer_back, то есть в предыдущей папке
    rev_dir = dir[::-1]
    wrong = ''
    for i in rev_dir: # Записываем в конец wrong название папки, в которую не надо входить
        if i == '/':
            break
        wrong += i
    pathlen = ''
    for i in buffer_back[::-1]: # Записываем имя директории, которой не должно быть внутри в предшествующей buffer_back директории
        pathlen += i
        if i == '/': break
    buffer_back_back = ''
    for i in range(len(buffer_back)-len(pathlen)): # Создаём buffer_back для buffer_back
        buffer_back_back += buffer_back[i]
    if dir not in wrong_paths: # Добавляем ненужный адрес в wrong_paths
        wrong_paths.append(dir)
    return database_filler(buffer_back, file, data, buffer_back_back, first_dir, wrong[::-1], wrong_paths, base_name) # Прогоняем тот же самый алгоритм, но в предыдущей папке


print("Insert absolute way into directory (it has to look like 'C:\ Users\ admin\Downloads'")
director = str(input()) + '<' # Абсолютный путь к исследуемой папке
directory = ""
for i in range(len(director)): #Защита(Возможно) от неправильных слешей
    if director[i] == '<':
        break
    if director[i]+director[i+1] == "\ ":
        directory += "/"
        i += 1
    if director[i] == ' ' and director[i] == '\ ':
        pass
    else:
        directory += director[i]

files = os.listdir(directory) # Получаем список файлов внутри директории
print("insert name of database:")
name_of_base = str(input())
data = database_create(name_of_base) # Создаём базу с именем name_of_base
print("You wanna hash directories inside your? (Write Yes(Y) or No(N))") # Выбор – хеширование с углублением в директории или нет
comand = str(input().lower())
if (comand == 'yes') or (comand == 'y'): # Хеширование всего внутри и внутри того, что внутри
    wrong_paths = []
    database_filler(directory, files, data, '', directory, '', wrong_paths, name_of_base) # Заполнение базы данных в отдельной функции
    print('Directory', director, 'has been hashed')
elif (comand == 'no') or (comand == 'n'): # ХЕширование без углубления в каталоги
    for filename in files:
        if filename == name_of_base:
            pass
        else:
            firstname = filename
            filename = file_reader(directory, filename)
            if filename != False:
                hash_summ = SHA_1_hashing(filename) # Хеширование имени файла
                if data_check(data, hash_summ, firstname) == True: # Проверка на существование в базе
                    data_insert(directory, firstname, hash_summ, data) # Вставка в базу
    print('Directory', director, 'has been hashed')
else:
    print('wrong command')

'''import sqlite3 # Для создания SQL таблицы
import os # Для сичтывания файлов в директории
# import subprocess # Для запуска алгоритма хеширования
# import pexpect

###
###
###
def SHA_1_hashing(inserting_text):
    def bytemove(a, n):  # битовый сдвиг на n позиций
        return ((a << n) | (a >> (32 - n))) & 0xffffffff
        # 0xffffffff - int 32-й степени двойки, то есть числа меньше 4 294 967 296

    def fill_data(m):  # Заполнение исходного текста в битах до кратности 512 битов
        n = m
        while (len(n)) % 512 != 448:  # Заполняем пустое пространство нулями
            n += '0'
        n += '{0:064b}'.format(len(m) - 1)  # Добавляем начальную длину входящего слова
        return n

    def chunk_create(m, n):  # Создание массива/массивов по n символов в каждом
        lst = []
        slice = ''  # Вставляемая в массив группа элементов
        for i in range(len(m)):
            slice += m[i]
            if len(slice) == n:
                lst.append(slice)
                slice = ''
        return lst

    def TEMP(A, B, C, D, E, f, wt, kt):
        temp = bytemove(A, 5) + f + E + kt + wt & 0xffffffff  # Получаем значение SHA
        return temp

    def main_hash(m):

        h0 = 0x67452301;
        h1 = 0xEFCDAB89;
        h2 = 0x98BADCFE;
        h3 = 0x10325476;
        h4 = 0xC3D2E1F0

        text = ''
        for i in range(len(m)):
            text += '{0:08b}'.format(ord(m[i]))  # Заполняем text символами из m, переведёнными в двоичный код
        text += '1'
        scnd_text = fill_data(text)  # Дополнение до длины, кратной 512
        for chnk in chunk_create(scnd_text, 512):  # Берём блок на 512 символов = chnk
            words = chunk_create(chnk, 32)  # Разбиваем блок на слова по 32 символа
            w = [0] * 80  # Список слов после трансформации (в виде цифр)
            for i in range(16):  # первые 16 слов
                w[i] = int(words[i], 2)  # вставляем значение слова + переводим из двоичного кода
            for i in range(16, 80):  # Оставшиеся слова
                w[i] = bytemove((int(w[i - 3]) ^ int(w[i - 8]) ^ int(w[i - 14]) ^ int(w[i - 16])), 1)  # Танцы с бубном

            A = h0
            B = h1
            C = h2
            D = h3
            E = h4

            for t in range(0, 80):  # циклические обработки всего дела
                if t >= 0 and t <= 19:
                    f = (B & C) | ((~B) & D)
                    kt = 0x5A827999  # 2^30 * sqrt(2)
                elif t >= 20 and t <= 39:
                    f = B ^ C ^ D
                    kt = 0x6ED9EBA1  # 2^30 * sqrt(3)
                elif t >= 40 and t <= 59:
                    f = (B & C) | (B & D) | (C & D)
                    kt = 0x8F1BBCDC  # 2^30 * sqrt(5)
                elif t >= 60 and t <= 79:
                    f = B ^ C ^ D
                    kt = 0xCA62C1D6  # 2^30 * sqrt(10)

                temp = TEMP(A, B, C, D, E, f, w[t], kt)  # Один раунд обработки
                E = D  # Так и не разобрался как внутри функции переназначать переменные, поэтому выдвинул сюда
                D = C
                C = bytemove(B, 30)
                B = A
                A = temp  # Переназначение переменных проводим только после действия

        h0 = str(hex(h0 + A & 0xffffffff)[2:])
        h1 = str(hex(h1 + B & 0xffffffff)[2:])
        h2 = str(hex(h2 + C & 0xffffffff)[2:])
        h3 = str(hex(h3 + D & 0xffffffff)[2:])
        h4 = str(hex(h4 + E & 0xffffffff)[2:])
        # Складываем первоначальный h и полученное значение его буквы в int^32, переводим в hexademical —> получаем 1 из 5-ти элементов финального хеша
        # Если правильно понимаю и помню h0-4 - это элементы финальной части нашего хеша, которые надо просто строками сложить
        fin = h0 + h1 + h2 + h3 + h4
        print(fin)
        return fin
        # print("input text which you wanna hash")
        #m = str(input())  # слово
    m = inserting_text
    return main_hash(m) #
# В представлении не нуждается
###
###
###

def database_create(base_name): # Создание базы
    data_con = sqlite3.connect(base_name) #Создаём подключение к базе
    cursor = data_con.cursor() # Берём объект cursor
    # print("Connection done")
    try:
        table_create = ("""CREATE TABLE file_list\
                       (path TEXT,
                        filename TEXT,
                        hashes TEXT)""")
        # Задаём параметры таблицы
        cursor.execute(table_create)
        data_con.commit() # Подтверждаем действие в базе
        print("Table and Database created")
    except:
        print("Table is not created or already exist")
    return data_con

def data_insert(path, filename, hash, data_con): # Вставка информации в базу
    cursor = data_con.cursor()
    try:
        sqlite_insert = """INSERT INTO file_list \
                        (path, filename, hashes) 
                        VALUES
                        (?, ?, ?)"""
        inserting_tuple = (path, filename, hash) # Создаём кортеж значений, которые будут вставляться в базу
        cursor.execute(sqlite_insert, inserting_tuple)
        data_con.commit() # !!! НЕ ЗАБЫТЬ ПОДТВЕРДИТЬ ДЕЙСТВИЕ В БАЗЕ
        cursor.close()
    except sqlite3.Error as mistake:
        print("Mistake while adding of information", mistake)

def data_check(data_con, hash): # Проверяет наличие хеша в базе
    cursor = data_con.cursor()
    cursor.execute("SELECT * FROM file_list")
    boolean = False # Булевая переменная для подтверждения наличия/отсутствия хеша в базе
    for chck_hash in cursor.fetchall(): # Перебором сверяется полученный хеш и хеши из базы
        if chck_hash[2] == hash:
            # print("This hash exist:", hash, "for", filename)
            boolean = True
            return False
            break
    if boolean == False:
        return True # boolean = False означает что хеша и файла нет в базе

def file_reader(directory, name):
    filetext = ''
    if os.path.isfile(directory+"\\"+name) == True: # Проверяем файл на тот факт что это файл
        try:
            filetext = open(directory+"\\"+name, "rb") # Открываем в бинарном виде и переводим все внутренности в строку
            filetext = str(filetext.read())

        except:
            print("error with", name) # На всякий случай, если файл не открылся
            return name # Практика показала что такого не было не разу
    else:
        print("error with", name) # В случае если не файл - пропускаем всё это дело
        return False

def database_filler(dir, files, data, buffer_back, first_dir, wrong, wrong_paths, base_name):
    # dir - директория, в которой мы сейчас находимся
    # files - файлы, находящиеся в директории
    # buffer_back - директория, предыдущая текущей (изначально не существует)
    # first_dir - начальная директория, из которой нельзя выходить во внешний мир
    # wrong - имя файла (директории), к которой нельзя прикасаться
    # wrong_paths - список папок, которые нам нельзя трогать (Они уже пройдены и хешированы)
    # Рекурсивный алгоритм для передвижения по директориям и заполнения базы. Принцип работы объяснять отказываюсь
    for filename in files: # Берём имя файла
        boolean = True
        if filename == wrong or filename == base_name:
            boolean = False
            pass
        else:
            try:
                if (dir+'/'+filename) in wrong_paths: # Встретили знакомый адрес –> пропустили его
                    pass
                else:
                    file = os.listdir(dir + '/' + filename) # Создаём новый адрес каталога
                    buffer_back = dir # Создаём буфферное значение чтобы потом можно было вернуться
                    return database_filler(dir + '/' + filename, file, data, buffer_back, first_dir, wrong, wrong_paths, base_name)
                    # Рекурсия запускает сама себя с новыми параметрами (Войдя в более глубокую папку)
            except:
                if boolean == True:
                    firstname = filename
                    filename = file_reader(dir, filename)
                    hash_summ = SHA_1_hashing(filename) # Берём хеш от файла
                    if data_check(data, hash_summ) == True: # Проверяем наличие в базе
                        data_insert(dir, firstname, hash_summ, data) # При отсутствии вставляем

    if dir == first_dir: # Проверяем совпадение текущей директории с начальной
        return 0
    file = os.listdir(buffer_back) # Берём список файлов в buffer_back, то есть в предыдущей папке
    rev_dir = dir[::-1]
    wrong = ''
    for i in rev_dir: # Записываем в конец wrong название папки, в которую не надо входить
        if i == '/':
            break
        wrong += i
    pathlen = ''
    for i in buffer_back[::-1]: # Записываем имя директории, которой не должно быть внутри в предшествующей buffer_back директории
        pathlen += i
        if i == '/': break
    buffer_back_back = ''
    for i in range(len(buffer_back)-len(pathlen)): # Создаём buffer_back для buffer_back
        buffer_back_back += buffer_back[i]
    if dir not in wrong_paths: # Добавляем ненужный адрес в wrong_paths
        wrong_paths.append(dir)
    return database_filler(buffer_back, file, data, buffer_back_back, first_dir, wrong[::-1], wrong_paths, base_name) # Прогоняем тот же самый алгоритм, но в предыдущей папке


print("Insert absolute way into directory (it has to look like 'C:\ Users\ admin\Downloads'")
director = str(input()) + '<' # Абсолютный путь к исследуемой папке
directory = ""
for i in range(len(director)): #Защита(Возможно) от неправильных слешей
    if director[i] == '<':
        break
    if director[i]+director[i+1] == "\ ":
        directory += "/"
        i += 1
    if director[i] == ' ' and director[i] == '\ ':
        pass
    else:
        directory += director[i]

files = os.listdir(directory) # Получаем список файлов внутри директории
print("insert name of database:")
name_of_base = str(input())
data = database_create(name_of_base) # Создаём базу с именем name_of_base
print("You wanna hash directories inside your? (Write Yes(Y) or No(N))") # Выбор – хеширование с углублением в директории или нет
comand = str(input().lower())
if (comand == 'yes') or (comand == 'y'): # Хеширование всего внутри и внутри того, что внутри
    wrong_paths = []
    database_filler(directory, files, data, '', directory, '', wrong_paths, name_of_base) # Заполнение базы данных в отдельной функции
    print('Directory', director[0:-1], 'has been hashed')
elif (comand == 'no') or (comand == 'n'): # ХЕширование без углубления в каталоги
    for filename in files:
        if filename == name_of_base:
            pass
        else:
            firstname = filename
            filename = file_reader(directory, filename)
            if filename != False:
                hash_summ = SHA_1_hashing(filename) # Хеширование имени файла
                if data_check(data, hash_summ) == True: # Проверка на существование в базе
                    data_insert(directory, firstname, hash_summ, data) # Вставка в базу
    print('Directory', director, 'has been hashed')
else:
    print('wrong command')'''