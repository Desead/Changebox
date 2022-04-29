def remove_space_from_string(check_string: str) -> str:
    return ''.join(check_string.split())


if __name__ == '__main__':
    a = ' 1       23 45690.567 4 1 9 234 5 '
    print(remove_space_from_string(a))
