from app_main.lib.remove_space_from_string import remove_space_from_string


def number_2_str(number_for_slice, comma: str = '.') -> str:
    '''
    переводим полученное число в строку разбив целую часть на разряды.
    обрезаем число до 8 знаков после запятой
    '''

    number_for_slice = str(number_for_slice)

    if comma in number_for_slice:
        int_part, fract_part, = number_for_slice.split(comma)
    else:
        int_part = number_for_slice
        fract_part = ''

    temp = ''

    while True:
        temp = ' ' + int_part[-3:] + temp
        int_part = int_part[:-3]
        if not int_part:
            if fract_part:
                temp = temp + comma + fract_part[:8]

            if float(remove_space_from_string(temp)) == 0:
                return '0.00'

            return temp.strip()


if __name__ == '__main__':
    temp = '12345678.1234567890123'
    print(number_2_str(temp))
