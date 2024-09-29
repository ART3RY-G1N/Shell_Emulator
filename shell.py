import os
import tarfile
import argparse
import psutil
import datetime


class ShellEmulator:
    def __init__(self, user, hostname, tar_path):
        self.user = user
        self.hostname = hostname
        self.fs = {}
        self.current_dir = 'filesystem' #указываем корвневую директорию
        self.load_virtual_fs(tar_path)

    def load_virtual_fs(self, tar_path):
        """Загружает виртуальную файловую систему из tar-архива."""
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                if member.isfile():  # Проверяем, является ли член архива файлом
                    with tar.extractfile(member) as file:
                        file_content = file.read()
                        self.fs[member.name] = file_content
                else:
                    # добавить директории в self.fs
                    if member.isdir():
                        self.fs[member.name] = None

        print(f"Файловая система загружена. {len(self.fs)} файлов и директорий.")

    def ls(self):
        """Выводит содержимое текущей директории."""
        current_dir_files = []
        for file in self.fs:
            # Проверяем, является ли файл в текущей директории или в её поддиректориях
            if file.startswith(self.current_dir):
                # Если путь не равен текущему каталогу (это файл или подкаталог)
                if file != self.current_dir:
                    # Проверяем, является ли это файл или директория в текущей директории
                    if os.path.dirname(file) == self.current_dir:
                        # Получаем значение по ключу (содержимое файла)
                        content = self.fs[file]
                        if content is not None:
                            # Вывод имени файла без пути
                            current_dir_files.append(os.path.basename(file))
                        else:
                            # Вывод имени директории
                            current_dir_files.append(f"{os.path.basename(file)}")

        # Выводим только файлы текущей директории
        for file in current_dir_files:
            print(file)

    def cd(self, path):
        """Изменяет текущий каталог."""
        if path == '..':
            # Переход на уровень вверх
            parent_dir = os.path.split(self.current_dir)[0]
            if parent_dir in self.fs:
                self.current_dir = parent_dir
            else:
                print("Невозможно перейти на уровень вверх.")
        else:
            # Объединение текущей директории с переданным путем
            path = '/'+path
            full_path = (self.current_dir + path)
            if full_path in self.fs:
                self.current_dir = full_path
            else:
                print(f"Каталог {path} не найден.")

    def uptime(self):
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        current_time = datetime.datetime.now()
        uptime = current_time - boot_time
        print(f"Время работы системы: {uptime}")
        print(f"Система была включена: {boot_time}")
        uptime_seconds = uptime.total_seconds()
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Время работы в формате ЧЧ:ММ:СС - {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

    def changeOwner(self, path, new_owner):
        """Изменяет владельца файла или директории."""
        if path in self.fs:
            print(f"Владелец для '{path}' изменён на '{new_owner}'.")
        else:
            print(f"Файл или директория '{path}' не найдены.")

    def reverse(self, path):
        if path in self.fs:
            content = self.fs[path]
            if content is not None:
                print(content[::-1].decode('utf-8'))
            else:
                print(f"'{path}' - это директория.")
        else:
            print(f"Файл или директория '{path}' не найдены.")


    def run(self):
        """Запускает эмулятор в режиме командной строки."""
        while True:
            if self.current_dir == 'filesystem':
                command = input(f"{self.user}@{self.hostname}:~$ ").split()
            else:
                command = input(f"{self.user}@{self.hostname}:{self.current_dir[10::]}$ ").split()
            if command[0] == 'ls':
                self.ls()
            elif command[0] == 'cd':
                if len(command) > 1:
                    self.cd(command[1])
                else:
                    print("Укажите путь.")
            elif command[0] == 'uptime':
                self.uptime()
            elif command[0] == 'rev':
                if len(command) == 1:
                    print(input()[::-1])
                else:
                    self.reverse(command[1])
            elif command[0] == 'chown':
                if len(command) == 3:
                    path = command[1]
                    uid = command[2]
                    self.changeOwner(path, uid)
                else:
                    print("Неправильное количество аргументов для chown.")
            elif command[0] == 'exit':
                break
            else:
                print(f"Команда {command[0]} не найдена.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор оболочки UNIX.")
    parser.add_argument('--user', required=True, help='Имя пользователя')
    parser.add_argument('--hostname', required=True, help='Имя компьютера')
    parser.add_argument('--tar', required=True, help='Путь к tar архиву виртуальной файловой системы')
    args = parser.parse_args()

    emulator = ShellEmulator(args.user, args.hostname, args.tar)
    emulator.run()