import re
from typing import Tuple

import pandas as pd


# Задача 1
def filter_fsuir_students(data: pd.DataFrame) -> Tuple[int, int, pd.DataFrame]:
    """
    Создает подвыборку студентов факультета систем управления и робототехники (ФСУиР).
    Возвращает количество таких студентов, количество уникальных групп и отфильтрованный датасет.
    """
    data_fsuir = data[data["факультет"] == "факультет систем управления и робототехники"]
    num_of_students = data_fsuir.shape[0]
    num_of_groups = data_fsuir["группа"].nunique()
    return num_of_students, num_of_groups, data_fsuir


# Задача 2
def find_homonymous_students(df: pd.DataFrame) -> Tuple[bool, int, pd.Series, str]:
    """
    Проверяет наличие однофамильцев на ФСУиР, их количество, распределение по курсам
    и определяет группу с наибольшим числом однофамильцев.
    Возвращает:
     - логическое значение (наличие однофамильцев)
     - общее количество однофамильцев
     - серию с числом однофамильцев по курсам
     - группу с максимальным числом однофамильцев
    """
    is_homonymous_students = df["surname"].duplicated().any()

    surnames = df["surname"].value_counts()
    duplicates = surnames[surnames > 1]
    num_of_homonymous_students = duplicates.sum()

    course_surname_count = df.groupby(["курс", "surname"]).size().reset_index(name="Count")
    course_duplicates = course_surname_count[course_surname_count["Count"] > 1]
    surname_course_duplicates = course_duplicates.groupby("курс")["Count"].sum()

    group_surname_count = df.groupby(["группа", "surname"]).size().reset_index(name="Count")
    group_duplicates = group_surname_count[group_surname_count["Count"] > 1]
    group_duplicates_sum = group_duplicates.groupby("группа")["Count"].sum()

    group_with_max_duplicates = str(group_duplicates_sum.idxmax())

    return is_homonymous_students, num_of_homonymous_students, surname_course_duplicates, group_with_max_duplicates


# Задача 3
def gender_identification(patronym: str) -> str:
    """
    Определяет пол по отчеству. Возвращает пол: female/male/unknown.
    """
    male_patronymic_pattern = re.compile(r".*(ович|евич|ич)$")
    female_patronymic_pattern = re.compile(r".*(овна|евна|ична|инична)$")

    if female_patronymic_pattern.match(patronym):
        return "female"
    if male_patronymic_pattern.match(patronym):
        return "male"
    return "unknown"


def analyze_patronyms(df: pd.DataFrame) -> Tuple[int, pd.Series]:
    """
    Определяет количество студентов без отчества и распределение студентов по полу на основе отчества.
    Возвращает:
     - количество студентов без отчества
     - серию с распределением студентов по полу
    """
    num_without_patronym = (df["patronim"] == "").sum()

    df["пол"] = df["patronim"].apply(gender_identification)
    gender_distribution = df["пол"].value_counts()

    return num_without_patronym, gender_distribution


# Задача 4
def faculty_statistics(data: pd.DataFrame) -> Tuple[pd.DataFrame, Tuple[str, int], Tuple[str, int]]:
    """
    Подсчитывает количество студентов на каждом факультете,
    а также определяет факультеты с максимальным и минимальным числом студентов.
    """
    faculties = data["факультет"].value_counts()

    faculty_with_max_students = str(faculties.idxmax())
    max_students = int(faculties.max())

    faculty_with_min_students = str(faculties.idxmin())
    min_students = int(faculties.min())

    return faculties.to_frame(), (faculty_with_max_students, max_students), (faculty_with_min_students, min_students)


# Задача 5
def course_statistics(data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Вычисляет среднее и медианное число студентов на каждом курсе.
    Возвращает две серии с результатами: сначала средние, потом медиана.
    """
    faculty_course_counts = data.groupby(["факультет", "курс"]).size().reset_index(name="count")

    course_mean_students = faculty_course_counts.groupby("курс")["count"].mean()
    course_median_students = faculty_course_counts.groupby("курс")["count"].median()

    return course_mean_students, course_median_students


# Задача 6
def most_popular_name(data: pd.DataFrame) -> Tuple[str, str, str, int, float]:
    """
    Определяет самое популярное имя, группу с наибольшим количеством студентов с этим именем,
    факультет, курс и долю таких студентов в общем числе.
    Возвращает результат в следующем порядке:
     1. самое частое имя
     2. группа
     3. факультет
     4. доля
    """
    the_most_popular_name = str(data["name"].value_counts().idxmax())

    filtered_data = data[data["name"] == the_most_popular_name]
    most_popular_group = str(filtered_data["группа"].value_counts().idxmax())

    filtered_data = filtered_data[filtered_data["группа"] == most_popular_group]
    most_popular_faculty = str(filtered_data["факультет"].iloc[0])

    most_popular_course = filtered_data["курс"].iloc[0]

    proportion = round(data["name"].value_counts().max() / data.shape[0], 2)

    return the_most_popular_name, most_popular_group, most_popular_faculty, most_popular_course, proportion


# Задача 7
def find_students_with_name_starting_P(data: pd.DataFrame) -> pd.DataFrame:
    """
    Находит студентов, чье имя встречается ровно один раз и начинается на "П". Выводит их ФИО, факультет и курс.
    """
    name_counts = data["name"].value_counts()
    names = name_counts[name_counts == 1].index

    names_starting_with_P = names[names.str.startswith("П")]

    new_data = data[data["name"].isin(names_starting_with_P)]

    return new_data[["фио", "факультет", "курс"]]


# Задача 8
def highest_avg_grade_faculty(data: pd.DataFrame) -> Tuple[str, str, int]:
    """
    Находит факультет, на котором средний балл студентов третьего курса самый высокий.
    Определяет пол, средний балл котого выше.
    Сначала возвращает факультет, затем пол, затем балл.
    """
    data = data[data["курс"] == "3-й"]
    data["пол"] = data["patronim"].apply(gender_identification)
    data = data[data["пол"].isin(["male", "female"])]

    grouped_data = data.groupby(["факультет", "пол"])["средний_балл"].mean().reset_index()

    max_avg_faculty = grouped_data.loc[grouped_data["средний_балл"].idxmax()]

    return str(max_avg_faculty["факультет"]), str(max_avg_faculty["пол"]), int(round(max_avg_faculty["средний_балл"]))


# Задача 9
def find_consecutive_students(data: pd.DataFrame) -> pd.DataFrame:
    """
    Находит первых 5 студентов, которым номера были присвоены подряд.
    Выводит их ФИО, факультет, курс и номер группы.
    """
    data = data.sort_values(by=["ису"]).reset_index(drop=True)

    five_students: pd.DataFrame = pd.DataFrame()

    for i in range(len(data) - 4):
        if (
            data["ису"].iloc[i + 1] - data["ису"].iloc[i] == 1
            and data["ису"].iloc[i + 2] - data["ису"].iloc[i + 1] == 1
            and data["ису"].iloc[i + 3] - data["ису"].iloc[i + 2] == 1
            and data["ису"].iloc[i + 4] - data["ису"].iloc[i + 3] == 1
        ):
            five_students = data.iloc[i : i + 5]
            break

    return five_students[["surname", "name", "patronim", "факультет", "курс", "группа", "ису"]]


if __name__ == "__main__":
    data = pd.read_csv("isu_fake_data.csv")
    data["surname"] = data["фио"].str.split().str[0]
    data["name"] = data["фио"].str.split().str[1]
    data["patronim"] = data["фио"].apply(lambda x: x.split()[2] if len(x.split()) > 2 else "")

    # Задача 1
    num_students, num_groups, fsuir = filter_fsuir_students(data)
    print(f"Студентов на ФСУиР: {num_students}, Групп: {num_groups}")

    # Задача 2
    has_homonyms, total_homonyms, homonyms_per_course, max_homonym_group = find_homonymous_students(fsuir)
    print(f"Есть однофамильцы: {has_homonyms}, Всего: {total_homonyms}, Группа с максимумом: {max_homonym_group}")
    print(f"На каждом курсе: {homonyms_per_course}")

    # Задача 3
    students_without_patronym, gender_counts = analyze_patronyms(fsuir)
    print(f"Студентов без отчества: {students_without_patronym}")
    print("Распределение по полу:", gender_counts)

    # Задача 4
    faculty_counts, max_faculty, min_faculty = faculty_statistics(data)
    print(f"Факультет с наибольшим числом студентов: {max_faculty}")
    print(f"Факультет с наименьшим числом студентов: {min_faculty}")

    # Задача 5
    mean_students, median_students = course_statistics(data)
    print("Среднее число студентов на курсах:", mean_students)
    print("Медианное число студентов на курсах:", median_students)

    # Задача 6
    popular_name, name_group, faculty, course, name_ratio = most_popular_name(data)
    print(f"Самое популярное имя: {popular_name}, Группа: {name_group}, Факультет: {faculty}, Курс: {course}")
    print(f"Доля студентов с этим именем: {name_ratio}")

    # Задача 7
    result_7 = find_students_with_name_starting_P(data)
    print("Студенты с именем, начинающимся на П и встречающимся ровно один раз:")
    print(result_7)

    # Задача 8
    fac, best_gender, best_grade = highest_avg_grade_faculty(data)
    print(f"Факультет с высоким средним баллом 3-го курса: {fac}")
    print(f"Пол с наивысшим средним баллом: {best_gender}, Средний балл: {best_grade}")

    # Задача 9
    result_9 = find_consecutive_students(data)
    print("Первые 5 студентов с подряд идущими табельными номерами:")
    print(result_9)
