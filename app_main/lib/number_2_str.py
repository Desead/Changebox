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

                fract_part = list(fract_part)[:8]
                while True:  # убираем последние 0, кроме первого, после .
                    n = len(fract_part) - 1
                    if n <= 0:
                        break
                    if fract_part[n] == '0':
                        fract_part.pop(n)
                    else:
                        break
                temp = temp + comma + ''.join(fract_part)

            else:
                return (temp + comma + '0').strip()

            if float(remove_space_from_string(temp)) == 0:
                return '0.0'

            return temp.strip()


if __name__ == '__main__':
    temp = '12345678.1234567890123'
    print(number_2_str(temp))
