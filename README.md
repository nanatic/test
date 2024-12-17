# Документация по Формированию JSON Конфигурации для Генерации Тестовых Данных

Эта документация описывает структуру JSON-конфигурационного файла, используемого для генерации тестовых данных по формам сбора информации о газораспределительных станциях ПАО «Газпром». Конфигурация включает описание таблиц (форм) и их полей с указанием методов генерации данных.

## Общая Структура JSON

JSON-конфигурация состоит из списка таблиц, каждая из которых содержит название и описание её полей. Для некоторых форм могут присутствовать подформы.

```json
{
    "tables": [
        {
            "name": "Название Таблицы",
            "fields": {
                "Имя Поля": { /* Описание поля */ },
                ...
            },
            "sub_forms": [
                {
                    "name": "Название Подформы",
                    "fields": { /* Описание полей подформы */ },
                    ...
                },
                ...
            ]
        },
        ...
    ]
}
```

## Типы Полей и Их Параметры

Каждое поле в таблице описывается объектом с определёнными параметрами в зависимости от типа данных. Ниже представлены все возможные типы полей и их параметры.

### 1. Строковые Поля (`string`)

**Описание:** Используются для текстовых данных, таких как названия организаций, филиалов, наименования ГРС и прочее.

**Параметры:**
- `type`: `"string"`
- `pattern`: Шаблон для генерации строки. Может включать индекс `{i}`, `{j}`, `{k}`, и т.д.
- `count` (опционально): Количество уникальных значений. Если указано, используется для генерации с индексом.

**Пример:**
```json
{
    "type": "string",
    "pattern": "Организация{i}",
    "count": 20
}
```

### 2. Числовые Поля (`integer`, `float`)

**Описание:** Используются для количественных данных, таких как номера, расстояния, давления и производительности.

**Параметры:**
- `type`: `"integer"` или `"float"`
- `min`: Минимальное значение.
- `max`: Максимальное значение.
- `distribution`: Тип распределения (`"uniform"`, `"gaussian"`).
- `round`: Количество знаков после запятой (для `float`).
- `constant` (опционально): Фиксированное значение.
- `value` (только для `constant`): Значение поля.

**Примеры:**

*Целое число:*
```json
{
    "type": "integer",
    "min": 1,
    "max": 100,
    "distribution": "uniform",
    "round": 0
}
```

*Число с плавающей точкой:*
```json
{
    "type": "float",
    "min": 0.5,
    "max": 15.0,
    "distribution": "gaussian",
    "round": 2
}
```

*Постоянное значение:*
```json
{
    "type": "float",
    "value": 90.0,
    "constant": true
}
```

### 3. Поля из Списка (`list`)

**Описание:** Используются для выбора значения из заранее определённого списка, например, "Форма обслуживания".

**Параметры:**
- `type`: `"list"`
- `options`: Массив возможных значений.

**Пример:**
```json
{
    "type": "list",
    "options": ["Дневная", "Ночная", "Круглосуточная"]
}
```

### 4. Дата (`date`)

**Описание:** Используются для указания дат ввода в эксплуатацию, проведения технических осмотров и других событий.

**Параметры:**
- `type`: `"date"`
- `min`: Минимальная дата в формате `"YYYY-MM-DD"`.
- `max`: Максимальная дата в формате `"YYYY-MM-DD"`.

**Пример:**
```json
{
    "type": "date",
    "min": "2000-01-01",
    "max": "2024-12-31"
}
```

### 5. Регистрационный Номер (`registration_number`)

**Описание:** Используется для уникальных идентификаторов, таких как инвентарные номера или регистрационные номера ГГТН.

**Параметры:**
- `type`: `"registration_number"`
- `pattern`: Шаблон номера с фиксированными и переменными частями. Переменные части обозначаются `{0}`, `{1}`, и т.д.

**Пример:**
```json
{
    "type": "registration_number",
    "pattern": "GRTN-{0000}-{0000}"
}
```

### 6. Примечание (`note`)

**Описание:** Текстовое поле для дополнительных комментариев или пояснений.

**Параметры:**
- `type`: `"string"`
- `pattern`: Шаблон для генерации примечаний, может включать индекс.

**Пример:**
```json
{
    "type": "string",
    "pattern": "Примечание {i}"
}
```

### 7. Логические Поля (`boolean`)

**Описание:** Используются для отметки выполнения требований (`true` — выполнено, `false` — не выполнено).

**Параметры:**
- `type`: `"boolean"`

**Пример:**
```json
{
    "type": "boolean"
}
```

### 8. Сложные Строковые Поля (`complex_string`)

**Описание:** Поля, состоящие из нескольких частей, требующих независимой генерации, например, "Dн x t".

**Параметры:**
- `type`: `"string"`
- `pattern`: Общий шаблон с вложенными полями.
- `generation`: Объект с описанием подполей.

**Пример:**
```json
{
    "type": "string",
    "pattern": "{Dн}x{t}",
    "generation": {
        "Dн": {
            "type": "float",
            "min": 100.0,
            "max": 1000.0,
            "distribution": "uniform",
            "round": 1
        },
        "t": {
            "type": "float",
            "min": 5.0,
            "max": 100.0,
            "distribution": "uniform",
            "round": 1
        }
    }
}
```

## Примеры Описания Полей

### Пример для Таблицы A.1

```json
{
    "name": "A.1 Форма сбора общих сведений о газораспределительной станции",
    "fields": {
        "Организация": {
            "type": "string",
            "pattern": "Организация{i}",
            "count": 20
        },
        "Филиал": {
            "type": "string",
            "pattern": "Филиал{i}",
            "count": 20
        },
        "Наименование ГРС": {
            "type": "string",
            "pattern": "ГРС{i}"
        },
        "Инвентарный номер": {
            "type": "integer",
            "min": 1000,
            "max": 9999,
            "distribution": "uniform",
            "round": 0
        },
        "Проектная организация": {
            "type": "string",
            "pattern": "ПроектнаяОрганизация{i}"
        },
        "Тип ГРС по проекту": {
            "type": "list",
            "options": ["Тип1", "Тип2", "Тип3"]
        },
        "Тип ГРС после капремонта": {
            "type": "list",
            "options": ["ТипA", "ТипB", "ТипC"]
        },
        "Дата ввода в эксплуатацию по проекту": {
            "type": "date",
            "min": "2000-01-01",
            "max": "2024-12-31"
        },
        "Дата ввода в эксплуатацию после капремонта": {
            "type": "date",
            "min": "2000-01-01",
            "max": "2024-12-31"
        },
        "Расстояние от ГРС до Филиала эксплуатирующей организации по автомобильной дороге (км)": {
            "type": "float",
            "min": 1.0,
            "max": 100.0,
            "distribution": "uniform",
            "round": 2
        },
        "Форма обслуживания": {
            "type": "list",
            "options": ["Дневная", "Ночная", "Круглосуточная"]
        },
        "Количество операторов": {
            "type": "integer",
            "min": 1,
            "max": 50,
            "distribution": "uniform",
            "round": 0
        },
        "Диаметр входного газопровода (Dн x t)": {
            "type": "complex_string",
            "pattern": "{Dн}x{t}",
            "generation": {
                "Dн": {
                    "type": "float",
                    "min": 100.0,
                    "max": 1000.0,
                    "distribution": "uniform",
                    "round": 1
                },
                "t": {
                    "type": "float",
                    "min": 5.0,
                    "max": 100.0,
                    "distribution": "uniform",
                    "round": 1
                }
            }
        },
        "Проектное давление газа на входе ГРС Pвх.проект (МПа)": {
            "type": "float",
            "min": 0.5,
            "max": 10.0,
            "distribution": "gaussian",
            "round": 2
        },
        "Максимальное достигнутое давление газа на входе ГРС в течение года Pвх.макс.факт./год (МПа)": {
            "type": "float",
            "min": 0.5,
            "max": 15.0,
            "distribution": "gaussian",
            "round": 2
        },
        "Разрешенное рабочее давление газа на входе ГРС Pвх.разр.рабочее (МПа)": {
            "type": "float",
            "min": 0.5,
            "max": 12.0,
            "distribution": "uniform",
            "round": 2
        },
        "Проектное давление газа на выходе ГРС Pвых.проектное (МПа)": {
            "type": "float",
            "min": 0.5,
            "max": 10.0,
            "distribution": "uniform",
            "round": 2
        },
        "Рабочее давление газа на выходе ГРС Pвых.рабочее(МПа)": {
            "type": "float",
            "min": 0.5,
            "max": 12.0,
            "distribution": "uniform",
            "round": 2
        },
        "Максимальное достигнутое давление газа на выходе ГРС в течение года Pвых.макс.факт./год (МПа)": {
            "type": "float",
            "min": 0.5,
            "max": 15.0,
            "distribution": "gaussian",
            "round": 2
        },
        "Проектная производительность ГРС Qпроект. (тыс. м3/ч)": {
            "type": "float",
            "min": 10.0,
            "max": 1000.0,
            "distribution": "uniform",
            "round": 1
        },
        "Максимальная фактическая производительность ГРС Qмакс.факт. (тыс. м3/ч)": {
            "type": "float",
            "min": 10.0,
            "max": 1200.0,
            "distribution": "gaussian",
            "round": 1
        },
        "Разрешенная пропускная способность ГРС Qразр. (тыс. м3/ч)": {
            "type": "float",
            "min": 10.0,
            "max": 1000.0,
            "distribution": "uniform",
            "round": 1
        },
        "Примечание": {
            "type": "string",
            "pattern": "Примечание {i}"
        }
    }
}
```

### Пример для Подформы A.11.2

```json
{
    "name": "A.11.2 Форма выполнения критериев нормативной документации",
    "fields": {
        "Международные НПА выполнено": {
            "type": "boolean"
        },
        "Федеральные законы и НПА высших органов власти выполнено": {
            "type": "boolean"
        },
        "Подзаконные акты и НД федеральных органов исполнительной власти выполнено": {
            "type": "boolean"
        },
        "Иные подзаконные акты и НД федеральных органов исполнительной власти выполнено": {
            "type": "boolean"
        },
        "Корпоративные НД уровня ПАО Газпром выполнено": {
            "type": "boolean"
        },
        "Рекомендации ПАО Газпром и корпоративные НД уровня дочерних обществ выполнено": {
            "type": "boolean"
        }
    }
}
```

## Поля с Вложенной Генерацией

Для полей, требующих генерации нескольких связанных значений (например, "Dн x t"), используется тип `complex_string` с описанием подполей в разделе `generation`.

**Пример:**
```json
{
    "type": "complex_string",
    "pattern": "{Dн}x{t}",
    "generation": {
        "Dн": {
            "type": "float",
            "min": 100.0,
            "max": 1000.0,
            "distribution": "uniform",
            "round": 1
        },
        "t": {
            "type": "float",
            "min": 5.0,
            "max": 100.0,
            "distribution": "uniform",
            "round": 1
        }
    }
}
```

## Специальные Типы Полей

### 1. Регистрационный Номер (`registration_number`)

Используется для уникальных идентификаторов с определённым форматом.

**Параметры:**
- `type`: `"registration_number"`
- `pattern`: Шаблон номера, где `{0}`, `{1}` и т.д. обозначают места для генерации цифр.

**Пример:**
```json
{
    "type": "registration_number",
    "pattern": "GGTN-{0000}-{0000}"
}
```

### 2. Постоянные Значения (`constant`)

Используются для полей с фиксированными значениями.

**Параметры:**
- `type`: Соответствующий тип (`"integer"`, `"float"`, и т.д.)
- `constant`: `true`
- `value`: Фиксированное значение.

**Пример:**
```json
{
    "type": "float",
    "value": 90.0,
    "constant": true
}
```

## Вложенные Формы (`sub_forms`)

Некоторые формы содержат подформы, которые описываются как вложенные объекты внутри основной формы.

**Пример:**
```json
{
    "name": "A.11 Форма сбора сведений для формирования интегрально балльного показателя",
    "sub_forms": [
        {
            "name": "A.11.1 Форма для расчёта балльного показателя риска аварии на ГРС",
            "fields": { /* Описание полей подформы */ }
        },
        {
            "name": "A.11.2 Форма выполнения критериев нормативной документации",
            "fields": { /* Описание полей подформы */ }
        },
        {
            "name": "A.11.3 Форма по итогам проверок надзорных органов",
            "fields": { /* Описание полей подформы */ }
        }
    ]
}
```

## Рекомендации по Формированию JSON

1. **Чёткое Название Таблиц и Полей:** Убедитесь, что названия таблиц и полей совпадают с теми, что используются в формах сбора данных.

2. **Определение Типов Полей:** Правильно указывайте тип данных каждого поля (`string`, `integer`, `float`, `list`, `date`, `boolean`, `registration_number`, `complex_string`).

3. **Использование Шаблонов:** Для строковых полей с повторяющимися или уникальными значениями используйте шаблоны с индексами `{i}`, `{j}`, и т.д.

4. **Диапазоны и Распределения:** Указывайте реалистичные диапазоны значений и соответствующие распределения для числовых полей.

5. **Округление:** Для чисел с плавающей точкой укажите количество знаков после запятой, если это необходимо.

6. **Списки Опций:** Для полей типа `list` предоставьте полный список допустимых значений.

7. **Вложенные Поля:** Для сложных строковых полей используйте `complex_string` с описанием подполей в `generation`.

8. **Постоянные Значения:** Для полей с фиксированными значениями используйте `constant` и `value`.

9. **Подформы:** Для форм, содержащих подформы, используйте раздел `sub_forms` внутри основной таблицы.

10. **Валидация:** После создания JSON-конфигурации рекомендуется провести её валидацию с помощью JSON-валидаторов и инструментов для генерации тестовых данных.

## Заключение

Эта документация предоставляет полный набор инструкций для формирования JSON-конфигурации, необходимой для генерации тестовых данных по формам газораспределительных станций ПАО «Газпром». Следуя представленным рекомендациям и примерам, вы сможете создать структурированный и гибкий конфигурационный файл, удовлетворяющий всем требованиям тестирования.

Если возникают вопросы или требуется дополнительная помощь, обращайтесь к разработчикам или специалистам по данным для уточнения специфических деталей.