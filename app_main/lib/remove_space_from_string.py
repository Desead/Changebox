def remove_space_from_string(check_string: str) -> str:

    check_string = list(check_string)

    while True:
        if ' ' in check_string:
            check_string.remove(' ')
        else:
            break

    return ''.join(check_string)


if __name__ == '__main__':
    a = ' 1       23 45690.567 4 1 9 234 5 '
    print(remove_space_from_string(a))
