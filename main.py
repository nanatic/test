import os
import json
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import re

# Папки с JSON-конфигурациями и выходными CSV
TABLES_DIR = 'tables'
OUTPUT_DIR = 'test_data'

# Количество записей для генерации в каждой таблице
NUM_RECORDS = 100

# Создание выходной папки, если её нет
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_json_files(directory):
    """Загружает все JSON-файлы из указанной директории."""
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    tables = []
    for file in json_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            tables.extend(data.get('tables', []))
    return tables


def generate_string(pattern, record, field_index):
    """Генерирует строку на основе шаблона."""
    # Найти все placeholders в формате {placeholder}
    placeholders = re.findall(r'\{([^}]+)\}', pattern)
    result = pattern
    for ph in placeholders:
        if ph in record:
            value = record[ph]
        else:
            # Генерация случайного числа для placeholder, если нет зависимости
            value = random.randint(1, 100)
        result = result.replace(f'{{{ph}}}', str(value))
    return result


def generate_registration_number(pattern):
    """Генерирует регистрационный номер на основе шаблона."""

    # Заменяем {0}, {1}, и т.д. на случайные цифры
    def replacer(match):
        digits = ''.join([str(random.randint(0, 9)) for _ in range(int(match.group(1)))])
        return digits

    return re.sub(r'\{(\d+)\}', replacer, pattern)


def generate_date(min_date, max_date):
    """Генерирует случайную дату между min_date и max_date."""
    min_dt = datetime.strptime(min_date, '%Y-%m-%d')
    max_dt = datetime.strptime(max_date, '%Y-%m-%d')
    delta = max_dt - min_dt
    random_days = random.randint(0, delta.days)
    random_date = min_dt + timedelta(days=random_days)
    return random_date.strftime('%Y-%m-%d')


def generate_field(field_config, record, field_index):
    """Генерирует значение поля на основе его конфигурации."""
    field_type = field_config.get('type')

    # Обработка строковых полей с шаблоном
    if field_type == 'string':
        pattern = field_config.get('pattern', 'Строка{i}')
        value = generate_string(pattern, record, field_index)
        return value

    # Обработка полей типа 'registration_number'
    elif field_type == 'registration_number':
        pattern = field_config.get('pattern', 'GRTN-{0000}-{0000}')
        value = generate_registration_number(pattern)
        return value

    # Обработка числовых полей
    elif field_type in ['integer', 'float']:
        if field_config.get('constant', False):
            return field_config.get('value')
        elif 'default' in field_config and random.choice([True, False]):
            return field_config['default']
        else:
            min_val = field_config.get('min', 0)
            max_val = field_config.get('max', 100)
            distribution = field_config.get('distribution', 'uniform')
            if field_type == 'integer':
                if distribution == 'uniform':
                    return random.randint(min_val, max_val)
                elif distribution == 'gaussian':
                    mean = (min_val + max_val) / 2
                    std = (max_val - min_val) / 6  # 99.7% данные внутри min-max
                    value = int(np.random.normal(mean, std))
                    return max(min_val, min(max_val, value))
            else:  # float
                if distribution == 'uniform':
                    value = random.uniform(min_val, max_val)
                elif distribution == 'gaussian':
                    mean = (min_val + max_val) / 2
                    std = (max_val - min_val) / 6
                    value = np.random.normal(mean, std)
                    value = max(min_val, min(max_val, value))
                round_digits = field_config.get('round', 2)
                return round(value, round_digits)

    # Обработка полей из списка
    elif field_type == 'list':
        options = field_config.get('options', [])
        return random.choice(options)

    # Обработка полей даты
    elif field_type == 'date':
        min_date = field_config.get('min', '2000-01-01')
        max_date = field_config.get('max', '2024-12-31')
        return generate_date(min_date, max_date)

    # Обработка булевых полей
    elif field_type == 'boolean':
        return random.choice([True, False])

    # Обработка сложных строковых полей
    elif field_type == 'complex_string':
        pattern = field_config.get('pattern', '{part1}{part2}')
        generation = field_config.get('generation', {})
        parts = {}
        for key, conf in generation.items():
            parts[key] = generate_field(conf, record, field_index)
        value = generate_string(pattern, parts, field_index)
        return value

    # Обработка полей заметок
    elif field_type == 'note':
        pattern = field_config.get('pattern', 'Примечание {i}')
        value = generate_string(pattern, record, field_index)
        return value

    else:
        return None  # Неизвестный тип поля


def generate_complex_subform(subform_config, record, field_index):
    """Генерирует данные для сложных подформ."""
    subform_type = subform_config.get('type')
    if subform_type == 'array':
        items_config = subform_config.get('items', {})
        num_items = random.randint(1, 5)  # Количество записей в массиве
        items = []
        for _ in range(num_items):
            item = {}
            for field_name, field_conf in items_config.get('properties', {}).items():
                item[field_name] = generate_field(field_conf, item, field_index)
            items.append(item)
        return items
    elif subform_type == 'object':
        item = {}
        for field_name, field_conf in subform_config.get('properties', {}).items():
            item[field_name] = generate_field(field_conf, record, field_index)
        return item
    else:
        return None


def generate_records(tables, num_records=100):
    """Генерирует тестовые записи для всех таблиц."""
    for table in tables:
        table_name = table.get('name', 'Unnamed_Table')
        print(f'Генерация данных для таблицы: {table_name}')
        records = []
        for i in range(1, num_records + 1):
            record = {}
            # Генерация основных полей
            fields = table.get('fields', {})
            for field_name, field_conf in fields.items():
                record[field_name] = generate_field(field_conf, record, i)
            # Генерация подформ
            sub_forms = table.get('sub_forms', [])
            for sub_form in sub_forms:
                sub_form_name = sub_form.get('name', 'Unnamed_Subform')
                sub_form_type = sub_form.get('type', 'object')  # По умолчанию объект
                sub_form_fields = sub_form.get('fields', {})
                if sub_form_type == 'array':
                    # Генерация массива объектов
                    record[sub_form_name] = []
                    num_items = random.randint(1, 5)  # Количество записей в массиве
                    for j in range(1, num_items + 1):
                        sub_record = {}
                        for sub_field, sub_conf in sub_form_fields.items():
                            if isinstance(sub_conf, dict):
                                sub_record[sub_field] = generate_field(sub_conf, sub_record, j)
                            else:
                                # Если поле не является словарём конфигурации
                                sub_record[sub_field] = sub_conf
                        record[sub_form_name].append(sub_record)
                elif sub_form_type == 'object':
                    # Генерация одного объекта подформы
                    sub_record = {}
                    for sub_field, sub_conf in sub_form_fields.items():
                        sub_record[sub_field] = generate_field(sub_conf, sub_record, i)
                    record[sub_form_name] = sub_record
                else:
                    # Другие типы подформ, если есть
                    record[sub_form_name] = None
            records.append(record)

        # Преобразование записей в DataFrame
        df = pd.json_normalize(records, sep='_')

        # Сериализация массивов как JSON строк
        for sub_form in sub_forms:
            sub_form_name = sub_form.get('name', 'Unnamed_Subform')
            if sub_form_name in df.columns:
                df[sub_form_name] = df[sub_form_name].apply(lambda x: json.dumps(x, ensure_ascii=False))

        # Сохранение в CSV
        # Замена недопустимых символов в имени файла
        safe_table_name = re.sub(r'[\\/*?:"<>|]', "_", table_name)
        output_path = os.path.join(OUTPUT_DIR, f'{safe_table_name}.csv')
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f'Данные сохранены в {output_path}\n')


def main():
    tables = load_json_files(TABLES_DIR)
    if not tables:
        print('Нет таблиц для генерации.')
        return
    generate_records(tables, NUM_RECORDS)


if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
