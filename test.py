import unittest
import datetime
from unittest.mock import patch
from shell import ShellEmulator

class ShellEmulatorTests(unittest.TestCase):

    def setUp(self):
        self.emulator = ShellEmulator('user', 'hostname', 'filesystem.tar')

    def test_load_virtual_fs(self):
        # Убеждаемся, что файл test.tar загружен
        self.assertTrue('filesystem/test/test.txt' in self.emulator.fs)
        self.assertTrue('filesystem/C' in self.emulator.fs)
        self.assertTrue('filesystem/D' in self.emulator.fs)

    def test_ls(self):
        # Проверяем вывод команды ls
        with patch('builtins.print') as mock_print:
            self.emulator.ls()
            mock_print.assert_any_call('test/')
            mock_print.assert_any_call('D/')
            mock_print.assert_any_call('C/')

        # Проверяем вывод ls из поддиректории
        self.emulator.cd('C')
        with patch('builtins.print') as mock_print:
            self.emulator.ls()
            mock_print.assert_any_call('users/')

    def test_cd(self):
        # Проверяем переход в поддиректорию
        self.emulator.cd('D')
        self.assertEqual(self.emulator.current_dir, 'filesystem/D')

        # Проверяем переход на уровень вверх
        self.emulator.cd('..')
        self.assertEqual(self.emulator.current_dir, 'filesystem')

        # Проверяем попытку перехода в несуществующую директорию
        with patch('builtins.print') as mock_print:
            self.emulator.cd('nonexistent_dir')
            mock_print.assert_any_call("Каталог nonexistent_dir не найден.")

    def test_uptime(self):
        # Тестируем вывод uptime
        with patch('psutil.boot_time') as mock_boot_time:
            mock_boot_time.return_value = 1678899200  # произвольное время загрузки
            with patch('builtins.print') as mock_print:
                self.emulator.uptime()
                # Проверяем, что вызваны функции print с ожидаемыми значениями
                mock_print.assert_any_call(f"Система была включена: {datetime.datetime.fromtimestamp(1678899200)}")

    def test_changeOwner(self):
        # Тестируем изменение владельца
        with patch('builtins.print') as mock_print:
            self.emulator.changeOwner('filesystem/test/test.txt', 'new_owner')
            mock_print.assert_any_call("Владелец для 'filesystem/test/test.txt' изменён на 'new_owner'.")

        # Тестируем изменение владельца для несуществующего файла
        with patch('builtins.print') as mock_print:
            self.emulator.changeOwner('nonexistent_file', 'new_owner')
            mock_print.assert_any_call("Файл или директория 'nonexistent_file' не найдены.")

    def test_reverse(self):
        # Тестируем вывод перевернутого содержимого файла
        with patch('builtins.print') as mock_print:
            self.emulator.reverse('filesystem/test.txt')
            mock_print.assert_any_call("54321")
            mock_print.assert_any_call("09876")

        # Тестируем вывод для директории
        with patch('builtins.print') as mock_print:
            self.emulator.reverse('filesystem/D')
            mock_print.assert_any_call("'filesystem/D' - это директория.")

        # Тестируем вывод для несуществующего файла
        with patch('builtins.print') as mock_print:
            self.emulator.reverse('nonexistent_file')
            mock_print.assert_any_call("Файл или директория 'nonexistent_file' не найдены.")

if __name__ == '__main__':
    unittest.main()
