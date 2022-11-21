import csv
import re
from collections import namedtuple
from datetime import datetime

import prettytable
from prettytable import PrettyTable


class CleanLines:

    @staticmethod
    def format_data_for_table_row(data):
        return data if len(data) < 100 else data[:100] + "..."

    @staticmethod
    def get_clean_date(date):
        return datetime.strptime(date[:10], "%Y-%m-%d") \
            .strftime("%d.%m.%Y")

    @staticmethod
    def get_line_without_double_spaces_and_tags(string):
        string = re.sub(r'<[^>]*>', '', string)
        string = re.sub("\s+", " ", string)
        string = string.strip()
        return string

    @staticmethod
    def get_formatted_salary_info(vacancy, russian_currency):
        salary_info = f"{'{0:,}'.format(int(float(vacancy.salary.salary_from))).replace(',', ' ')} - " \
                      f'{"{0:,}".format(int(float(vacancy.salary.salary_to))).replace(",", " ")} ' \
                      f'({russian_currency[vacancy.salary.salary_currency]}) ' \
                      f'({"С вычетом налогов" if vacancy.salary.salary_gross == "False" else "Без вычета налогов"})'
        return salary_info


class RussianWords:

    @staticmethod
    def get_russian_names():
        return {'name': 'Название',
                'description': 'Описание',
                'key_skills': 'Навыки',
                'experience_id': 'Опыт работы',
                'premium': 'Премиум-вакансия',
                'employer_name': 'Компания',
                'salary_from': 'Нижняя граница вилки оклада',
                'salary_to': 'Верхняя граница вилки оклада',
                'salary_gross': 'Оклад указан до вычета налогов',
                'salary_currency': 'Идентификатор валюты оклада',
                'area_name': 'Название региона',
                'published_at': 'Дата публикации вакансии',
                'salary': 'Оклад'}

    @staticmethod
    def get_russian_yes_no():
        return {'True': 'Да',
                'False': 'Нет'}

    @staticmethod
    def get_russian_work_experience():
        return {'noExperience': 'Нет опыта',
                'between1And3': 'От 1 года до 3 лет',
                'between3And6': 'От 3 до 6 лет',
                'moreThan6': 'Более 6 лет'}

    @staticmethod
    def get_russian_currency():
        return {'AZN': 'Манаты',
                'BYR': 'Белорусские рубли',
                'EUR': 'Евро',
                'GEL': 'Грузинский лари',
                'KGS': 'Киргизский сом',
                'KZT': 'Тенге',
                'RUR': 'Рубли',
                'UAH': 'Гривны',
                'USD': 'Доллары',
                'UZS': 'Узбекский сум'}


class InputConnect:

    def __init__(self):
        self.error_message = None

        self.file_name = self.__get_file_name()
        self.filter_param = input("Введите параметр фильтрации: ")
        self.sort_param = self.__get_sort_param()
        self.reversed_sort = self.__get_reversed_sort_param()
        self.output_range = self.__get_output_range()
        self.columns = self.__get_columns()

    def __get_columns(self):
        columns = input("Введите требуемые столбцы: ").split(", ")
        columns.insert(0, "№")
        return columns

    def __get_file_name(self):
        file_name = input("Введите название файла: ")
        if file_name == '':
            self.error_message = 'Название файла не может быть пустым'
        else:
            return file_name

    def __get_filter_param(self):
        pass

    def __get_sort_param(self):
        sort_param = input("Введите параметр сортировки: ")
        if sort_param not in RussianWords.get_russian_names().values():
            self.error_message = 'Параметр сортировки некорректен'
        return sort_param

    def __get_reversed_sort_param(self):
        reversed_sort = input("Обратный порядок сортировки (Да / Нет): ")
        if reversed_sort not in ['', 'Да', 'Нет']:
            self.error_message = 'Порядок сортировки задан некорректно'
        return False \
            if reversed_sort == 'Нет' \
            else True

    def __get_output_range(self):
        output_range = input("Введите диапазон вывода: ")
        return list(map(int, output_range.split(' '))) \
            if output_range != '' and ' ' in output_range \
            else ''

    def __get_vacancies(self):
        data_set = DataSet(self.file_name)
        data_set.add_vacancies()
        return data_set.vacancies_objects

    def get_vacancies_table(self):
        vacancies = self.__get_vacancies()
        table = PrettyTable()

        yes_no = RussianWords.get_russian_yes_no()
        currency = RussianWords.get_russian_currency()
        work_experience = RussianWords.get_russian_work_experience()

        table_names = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                       'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']

        table.field_names = table_names
        table.hrules = prettytable.ALL
        table.align = 'l'
        table.max_width = 20

        count = 1
        for vacancy in vacancies:
            row = [count,
                   CleanLines.format_data_for_table_row(vacancy.name),
                   CleanLines.format_data_for_table_row(vacancy.description),
                   CleanLines.format_data_for_table_row("\n".join(vacancy.key_skills)
                                                        if isinstance(vacancy.key_skills, list)
                                                        else vacancy.key_skills),
                   work_experience[vacancy.experience_id],
                   yes_no[vacancy.premium],
                   CleanLines.format_data_for_table_row(vacancy.employer_name),
                   CleanLines.get_formatted_salary_info(vacancy, currency),
                   vacancy.area_name,
                   CleanLines.get_clean_date(vacancy.published_at)]
            table.add_row(row)
            count += 1
        return table


class Vacancy:

    def __init__(self, name, description, key_skills, experience_id,
                 premium, employer_name, salary_from, salary_to,
                 salary_gross, salary_currency, area_name, published_at):
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = Salary(salary_from, salary_to, salary_gross, salary_currency)
        self.area_name = area_name
        self.published_at = published_at


class Salary:

    def __init__(self, salary_from, salary_to,
                 salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def to_string(self):
        return f"{self.salary_from} - {self.salary_to} " \
               f"({self.salary_currency}) " \
               f"({'С вычетом налогов' if not self.salary_gross == 'False' else 'Без вычета налогов'})"


class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = []

    def add_vacancies(self):
        data = self.__get_data_from_csv()
        if data is None:
            return
        data_names = data.names
        data_values = data.data
        for line in data_values:
            vacancy_params = []
            for i in range(0, len(data_names)):
                value = line[i]
                if "\n" in value:
                    value = list(value.split("\n"))
                else:
                    value = CleanLines.get_line_without_double_spaces_and_tags(value)
                vacancy_params.append(value)
            self.vacancies_objects.append(Vacancy(name=vacancy_params[0],
                                                  description=vacancy_params[1],
                                                  key_skills=vacancy_params[2],
                                                  experience_id=vacancy_params[3],
                                                  premium=vacancy_params[4],
                                                  employer_name=vacancy_params[5],
                                                  salary_from=vacancy_params[6],
                                                  salary_to=vacancy_params[7],
                                                  salary_gross=vacancy_params[8],
                                                  salary_currency=vacancy_params[9],
                                                  area_name=vacancy_params[10],
                                                  published_at=vacancy_params[11]))

    def __get_data_from_csv(self):
        with open(self.file_name, encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file)
            names = reader.__next__()
            data = []
            for line in reader:
                if "" not in line and len(line) == len(names):
                    data.append(line)
            Data = namedtuple("Data", "names data")
        return Data(names, data)


if __name__ == "__main__":
    inputConnect = InputConnect()
    if inputConnect.error_message is not None:
        print(inputConnect.error_message)
    else:
        table = inputConnect.get_vacancies_table()

        start = inputConnect.output_range[0] if len(inputConnect.output_range) >= 1 else 0
        end = inputConnect.output_range[1] if len(inputConnect.output_range) == 2 else table.__getattr__('rowcount')
        fields = inputConnect.columns
        reversesort = inputConnect.reversed_sort
        sort_key = lambda x: inputConnect.sort_param[1] in x if inputConnect.sort_param != '' else lambda x: x

        print(table.get_string(sortby=inputConnect.sort_param,
                               reversesort=reversesort,
                               start=start,
                               end=end,
                               fields=fields))
