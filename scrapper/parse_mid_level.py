import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import logging
import os

from helper import extract_link

DEFAULT_LOAD_TIMEOUT = 2
EMPTY_SPECIALIZATION_CATEGORY = "default"

def parse_specializations(driver):
    specialization_select = driver.find_element(By.NAME, "sp")
    results = []
    specializations = specialization_select.find_elements(By.TAG_NAME, "option")
    for specialization in specializations:
        specialization_name = specialization.text
        results.append(specialization_name)
    return results

def click_specialization(driver, value):
    if value == EMPTY_SPECIALIZATION_CATEGORY:
        return
    specialization_select = driver.find_element(By.NAME, "sp")
    specializations = specialization_select.find_elements(By.TAG_NAME, "option")
    for option in specializations:
        if option.text == value:
            option.click()  # Click the matching option
            time.sleep(DEFAULT_LOAD_TIMEOUT)
            return

# Load the CSV file
df = pd.read_csv("top_level.csv")

# Initialize the WebDriver
try:
    driver = webdriver.Firefox()

    course_matrix = []
    for index, row in df.iterrows():
        link = row["Link"]
        id_value = row["ID"]

        print(f"Opening link with ID: {id_value}, URL: {link}")

        # Open the link in the browser
        driver.get(link)
        time.sleep(DEFAULT_LOAD_TIMEOUT)

        # Retrieve specializations
        specialization_select = driver.find_element(By.NAME, "sp")
        is_specialization_supported = (
            specialization_select.get_attribute("disabled") is None
        )
        if is_specialization_supported:
            specializations = parse_specializations(driver)
        else:
            specializations = [EMPTY_SPECIALIZATION_CATEGORY]
        print(specializations)
        specialization_data = []
        for specialization in specializations:
            click_specialization(driver, specialization)
            semesters_data = []
            semesters = driver.find_elements(
                By.XPATH,
                '//div[@class="iform" and not(descendant::tr[@class="tabela-stopka"])]',
            )
            for semester in semesters:
                sem_name = semester.find_element(By.XPATH, "./h3").text
                print(f"  Przetwarzanie semestru: {sem_name}")

                # Find courses in the semester
                course_rows = semester.find_elements(By.XPATH, './/table[@class="tabela"]//tbody//tr')
                course_data = []
                for course_row in course_rows:
                    # Pobierz nazwę kursu z drugiej kolumny
                    course_name_cell = course_row.find_element(By.XPATH, './td[@class="w4"]')
                    course_name = course_name_cell.text.strip()

                    # Sprawdź, czy to "Mobility Semester" lub inny przypadek bez kodu kursu
                    if course_name == "Mobility Semester (Semestr mobilny)":
                        print("    Znaleziono semestr Mobility - dodawanie domyślnych danych.")
                        course_data.append({
                            "kod": "przedmioty do wyboru z uczelni zagranicznej",
                            "link": "brak informacji",
                            "egzamin": None
                        })
                        continue

                    # Sprawdź, czy link istnieje
                    course_link_elements = course_row.find_elements(By.XPATH, './td//a')
                    if not course_link_elements:
                        print("    Brak linku do kursu - pomijam wiersz.")
                        continue  # Pomijamy wiersz, jeśli link nie istnieje

                    # Pobieramy pierwszy (i jedyny) element linku
                    course_link_element = course_link_elements[0]
                    base_url = driver.current_url
                    link = extract_link(course_link_element.get_attribute("onclick"), base_url)

                    # Sprawdzenie obecności egzaminu
                    exam_elements = course_row.find_elements(By.XPATH, './/td[last()]')
                    has_exam = exam_elements[0].text.strip() == "E" if exam_elements else False

                    print(f"    Przetwarzanie kursu: {course_link_element.text} z linkiem {link}, egzamin: {has_exam}")
                    course_data.append({
                        "kod": course_link_element.text,
                        "link": link,
                        "egzamin": has_exam
                    })

                
                semesters_data.append({"semestr": sem_name, "kursy": course_data})
            specialization_data.append(
                {"specjalizacja": specialization, "semestry": semesters_data}
            )
        course_matrix.append({"id": id_value, "specjalizacje": specialization_data})

    # Postprocessing and saving the data
    def generator():
        for matrix in course_matrix:
            id = matrix["id"]
            for specialization in matrix["specjalizacje"]:
                specialization_name = specialization["specjalizacja"]
                for semester in specialization["semestry"]:
                    semester_name = semester["semestr"]
                    for course in semester["kursy"]:
                        yield (
                            id,
                            specialization_name,
                            semester_name,
                            course["kod"],
                            course["link"],
                            course["egzamin"],
                        )

    g = generator()

    try:
        df = pd.DataFrame(
            g,
            columns=[
                "ID",
                "Specjalizacja",
                "Semestr",
                "Kod kursu",
                "Link do kursu",
                "Egzamin",
            ],
        )
        csv_file = "mid_level.csv"

        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            df_combined = pd.concat([df_existing, df], ignore_index=True)
            df_combined.to_csv(csv_file, index=False)
        else:
            df.to_csv(csv_file, index=False)
    except Exception as e:
        logging.error(f"Error while putting the results into csv: {e}")
        print(df)

finally:
    driver.quit()
    print("[DONE]")
