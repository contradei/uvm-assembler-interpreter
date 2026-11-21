# Ассемблер и интерпретатор УВМ — вариант 9

Конфигурационное управление. Практическая работа 3, ИКБО-22-25.
Этап 1: Промежуточное представление.
Основание: методичка, страницы 40–43; общие требования — страницы 4–7.

## Подготовка

Python 3.12 или новее. Сторонние библиотеки для работы не нужны, сборка не требуется.
В PowerShell из папки проекта:

```powershell
python -m venv .venv
.\run.bat --help
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Если доступен только launcher, создайте окружение командой `py -3 -m venv .venv`.
run.bat использует локальную .venv, затем python или py. Активировать .venv не обязательно.
Linux/macOS: вместо `.\run.bat` используйте `python3 -m src.uvm.main`.
Прямой запуск также поддержан: `python src/uvm/main.py --help`.
В PyCharm выберите .venv/Scripts/python.exe; рабочая папка — корень проекта.
Модуль запуска: src.uvm.main. Параметры задаются как в примерах ниже.

## Язык JSON-ассемблера

Программа — JSON-массив команд. Порядок элементов задаёт порядок исполнения.
Имена операций и полей чувствительны к регистру. Все операнды — целые JSON-числа;
строки, true/false, дробные числа, лишние и повторяющиеся поля запрещены.

| Команда | Поля JSON | Поля УВМ | Размер |
| --- | --- | --- | --- |
| load_const | value | A=12, B=value | 5 байт |
| read | address | A=1, B=address | 4 байта |
| write | address | A=2, B=address | 4 байта |
| not | destination, source | A=25, B=destination, C=source | 6 байт |

Константа: 0..4294967295 (32 бита). Адрес: 0..2097151 (21 бит).
Пример всех четырёх команд: examples/specification.json.

```json
[
  {"op": "load_const", "value": 443},
  {"op": "read", "address": 720},
  {"op": "write", "address": 558},
  {"op": "not", "destination": 724, "source": 643}
]
```

## Ассемблер

```powershell
.\run.bat assemble --source examples/specification.json --output generated/spec.bin --test-mode
```

| Параметр | Назначение |
| --- | --- |
| assemble | Подкоманда ассемблирования |
| --source | Обязательный путь к исходному JSON, UTF-8 (BOM допустим) |
| --output | Обязательный путь для двоичного результата |
| --test-mode | Показать диагностическое представление программы |

Ошибки аргументов дают код 2; ошибки чтения, синтаксиса или выполнения — код 1.
Успех — код 0. Ошибки идут в stderr. Исходный файл нельзя использовать как выходной.
Пустая программа [] допустима; неизвестные операции и неверные операнды запрещены.

На этапе 1 двоичный файл ещё не создаётся. Без --test-mode программа только проверяется.
В тестовом режиме выводится промежуточное представление:

```text
A=12, B=443
A=1, B=720
A=2, B=558
A=25, B=724, C=643
```

## Описание функций

### cli.py

- `different_paths`: Prevent output from overwriting the input, including hard links.
- `parse_args`: Parse the assembler source, binary destination and test mode.

### main.py

- `assemble`: Parse all instructions; show fields only when test mode is enabled.
- `main`: Return code 1 for processing errors and leave argparse code 2 intact.

### parser.py

- `unique_object`: Reject duplicate JSON keys instead of silently losing an operand.
- `parse_instruction`: Validate a mnemonic and map named operands to fields a, b and c.
- `parse_program`: Read a JSON array and annotate errors with the instruction number.
- `read_program`: Load UTF-8 JSON; accept an optional BOM from Windows editors.
- `format_fields`: Display field names in the exact A=..., B=..., C=... test notation.

### spec.py

- `check_unsigned`: Reject booleans, non-integers and values outside an unsigned field.

## Проверки качества

Тесты есть в каждом этапе. Проверяются структура репозитория, docstring,
длина строк Python ≤80, функций ≤40, файлов ≤1000 строк, число аргументов ≤7.
Отдельная проверка flake8/pep8-naming и radon контролирует стиль и сложность ≤10.
