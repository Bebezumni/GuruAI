def count_tokens(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        tokens = content.split()  # Простое разделение по пробелам, может не учитывать некоторые тонкости языка

    return len(tokens)

def clear_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('')  # Очищаем файл, записывая пустую строку

def main():


if __name__ == '__main__':
    main()