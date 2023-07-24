def bytemove(a, n):  # битовый сдвиг на n позиций
    return ((a << n) | (a >> (32 - n))) & 0xffffffff
    # 0xffffffff - int 32-й степени двойки, то есть числа меньше 4 294 967 296

def fill_data(m): # Заполнение исходного текста в битах до кратности 512 битов
    n = m
    while (len(n)) % 512 != 448: # Заполняем пустое пространство нулями
        n += '0'
    n += '{0:064b}'.format(len(m)-1) # Добавляем начальную длину входящего слова
    return n

def chunk_create(m, n): # Создание массива/массивов по n символов в каждом
    lst = []
    slice = '' # Вставляемая в массив группа элементов
    for i in range(len(m)):
        slice += m[i]
        if len(slice) == n:
            lst.append(slice)
            slice = ''
    return lst

def TEMP(A, B, C, D, E, f, wt, kt):
    temp = bytemove(A, 5) + f + E + kt + wt & 0xffffffff # Получаем значение SHA
    return temp

print("input text which you wanna hash")
m = str(input()) # слово

h0 = 0x67452301; h1 = 0xEFCDAB89; h2 = 0x98BADCFE; h3 = 0x10325476; h4 = 0xC3D2E1F0

text = ''
for i in range(len(m)):
    text += '{0:08b}'.format(ord(m[i])) # Заполняем text символами из m, переведёнными в двоичный код
text += '1'
scnd_text = fill_data(text) # Дополнение до длины, кратной 512
for chnk in chunk_create(scnd_text, 512): # Берём блок на 512 символов = chnk
    words = chunk_create(chnk, 32) # Разбиваем блок на слова по 32 символа
    w = [0]*80 # Список слов после трансформации (в виде цифр)
    for i in range(16): # первые 16 слов
        w[i] = int(words[i], 2) # вставляем значение слова + переводим из двоичного кода
    for i in range(16, 80): # Оставшиеся слова
        w[i] = bytemove( (int(w[i-3]) ^ int(w[i-8]) ^ int(w[i-14]) ^ int(w[i-16])), 1 ) # Танцы с бубном

    A = h0
    B = h1
    C = h2
    D = h3
    E = h4

    for t in range(0, 80): # циклические обработки всего дела
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

        temp = TEMP(A, B, C, D, E, f, w[t], kt) # Один раунд обработки
        E = D # Так и не разобрался как внутри функции переназначать переменные, поэтому выдвинул сюда
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