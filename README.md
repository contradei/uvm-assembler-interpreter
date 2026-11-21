# Ассемблер и интерпретатор УВМ — вариант 9

Конфигурационное управление. Практическая работа 3, ИКБО-22-25.
Этап 4: Побитовое НЕ.
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

Начиная с этапа 2 создаётся бинарный файл и выводится число команд.
В --test-mode печатаются байты каждой команды, а не промежуточные поля этапа 1:

```text
Instructions: 4
0x6C, 0x37, 0x00, 0x00, 0x00
0x01, 0x5A, 0x00, 0x00
0xC2, 0x45, 0x00, 0x00
0x99, 0x5A, 0x00, 0x0C, 0x0A, 0x00
```

Порядок байтов little-endian следует из примеров спецификации.
A занимает биты 0–4; B начинается с бита 5; C в not — с бита 26.
Неиспользуемые старшие биты равны нулю. Заголовков и разделителей между командами нет.
Папки результата создаются автоматически. Файл заменяется только после успешной трансляции.
Бинарные файлы и дампы generated не входят в Git.

## Интерпретатор

```powershell
.\run.bat assemble --source examples/copy_array.json --output generated/copy.bin
.\run.bat interpret --binary generated/copy.bin --dump generated/copy.xml --start 10 --end 22
Get-Content generated/copy.xml
```

| Параметр | Назначение |
| --- | --- |
| interpret | Подкоманда выполнения |
| --binary | Обязательный путь к бинарной программе |
| --dump | Обязательный путь к выходному XML |
| --start | Первый адрес дампа (включительно) |
| --end | Последний адрес дампа (включительно), не меньше start |

Память команд — неизменяемые байты; память данных — отдельный разреженный словарь.
Адресное пространство содержит 2^21 ячеек; неприсвоенные ячейки равны 0.
Аккумулятор изначально равен 0. load_const и read изменяют аккумулятор;
write сохраняет его в указанную ячейку. Исполнение завершается на конце файла.
Обрезанная команда, неизвестный opcode и ненулевые резервные биты дают ошибку.
При ошибке выполнения прежний XML-дамп сохраняется.

В методичке не указаны знаковость памяти и ширина результата НЕ.
Здесь явно принята модель беззнаковых 32-битных слов, согласованная с размером константы.
Это выбранное соглашение реализации, а не дополнительное условие методички.

copy_array.json сначала записывает [7, 0, 4294967295] по адресам 10..12,
затем копирует их командами read/write по адресам 20..22.
Дамп содержит исходный и скопированный массивы; остальные ячейки равны 0.
XML имеет корень memory с атрибутами start/end; элементы cell — address/value.

## Побитовое НЕ

Команда not вычисляет memory[destination] = (~memory[source]) & 0xFFFFFFFF.
Аккумулятор не меняется. Совпадение адресов допустимо.
Проверяются ноль, максимальное слово, старший бит и чередующиеся биты.

```powershell
.\run.bat assemble --source examples/not_cases.json --output generated/not.bin
.\run.bat interpret --binary generated/not.bin --dump generated/not.xml --start 0 --end 13
Get-Content generated/not.xml
```

Исходные ячейки 0..3: [0, 4294967295, 2147483648, 2863311530].
Результаты в ячейках 10..13: [4294967295, 0, 2147483647, 1431655765].

## Описание функций

### cli.py

- `different_paths`: Prevent output from overwriting the input, including hard links.
- `add_assembler`: Describe the source, binary output and diagnostic flag.
- `add_interpreter`: Describe the binary input and inclusive XML dump range.
- `validate_paths`: Validate subcommand-specific paths and dump endpoints.
- `parse_args`: Return validated options, reporting argument errors with code 2.

### codec.py

- `encode_instruction`: Pack validated A/B/C fields with zero-filled unused high bits.
- `encode_program`: Translate every instruction before any output file is changed.
- `format_bytes`: Format an instruction like the hexadecimal tests in the PDF.
- `decode_instruction`: Decode one instruction and reject truncation, opcodes and padding.

### dump.py

- `validate_range`: Require ordered inclusive endpoints in the 21-bit address space.
- `memory_xml`: Include each requested cell, including zeros, with explicit addresses.

### files.py

- `atomic_write`: Write beside the destination and atomically replace it on success.

### machine.py

- `__init__`: Start with no assigned cells.
- `read`: Read a valid address without allocating unwritten cells.
- `write`: Store a word after validating both the address and its value.
- `__init__`: Initialize a zero accumulator and independent data memory.
- `execute`: Dispatch memory operations and the bitwise NOT instruction.
- `load_constant`: Copy B into the accumulator.
- `read`: Copy data memory at B into the accumulator.
- `write`: Copy the accumulator into data memory at B.
- `bitwise_not`: Invert the word at C into B without changing the accumulator.
- `run`: Read, decode and execute complete instructions in byte order.

### main.py

- `assemble`: Write the machine code, report count and optionally print each byte.
- `main`: Return code 1 for processing errors and leave argparse code 2 intact.
- `interpret`: Run a binary program and publish an XML dump only after success.

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
