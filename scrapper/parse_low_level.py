import json
import os 
import re
import pandas as pd
import logging
from typing import Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Ustawienie WebDrivera
driver = webdriver.Chrome()  # lub webdriver.Firefox()

# Wczytanie danych z pliku CSV
df = pd.read_csv("mid_level_all.csv")

# Pobranie unikalnych kursów z kolumny "Kod kursu" i "Link do kursu"
unique_courses = df[['Kod kursu', 'Link do kursu']].drop_duplicates()

# Funkcja pomocnicza do dynamicznego oczekiwania na element
def wait_for_element(driver, by, value, timeout=3):
    """Czeka na pojawienie się elementu na stronie."""
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        logging.error(f"Element {value} nie załadował się w czasie {timeout} sekund.")

# Funkcja do rozpoznania typu karty
def detect_card_type(driver: webdriver.Chrome, course_url: str) -> str:
    """Rozpoznaje typ struktury karty przedmiotu."""
    driver.get(course_url)
    wait_for_element(driver, By.TAG_NAME, 'body')

    # Sprawdź, czy strona zawiera typowe elementy dla struktury standardowej
    standard_elements = driver.find_elements(By.XPATH, '//tr[td[@class="parametr" and text()="Kod przedmiotu"]]')
    if standard_elements:
        return "standard"

    # Sprawdź, czy strona zawiera elementy dla struktury alternatywnej
    alternate_elements = driver.find_elements(By.XPATH, '//td[@class="wartosc"]//a')
    if alternate_elements:
        return "alternate"

    logging.error("Nie rozpoznano struktury karty.")
    return "unknown"

# Funkcja pobierająca dane ze standardowej karty
def fetch_standard_course_data(driver: webdriver.Chrome, course_url: str) -> Dict[str, str]:
    """Pobiera dane z karty przedmiotu o standardowej strukturze."""
    # Otwórz stronę przedmiotu
    driver.get(course_url)

    # Dynamiczne oczekiwanie na załadowanie strony
    wait_for_element(driver, By.XPATH, '//tr[td[@class="parametr" and text()="Kod przedmiotu"]]')

    # Pobierz dane przedmiotu
    data = {
        "Kod przedmiotu": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Kod przedmiotu"]]/td[@class="wartosc"]').text,
        "ECTS": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and contains(text(), "ECTS")]]/td[@class="wartosc"]').text,
        "Nazwa w języku polskim": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Nazwa w języku polskim"]]/td[@class="wartosc"]').text,
        "Nazwa w języku angielskim": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Nazwa w języku angielskim"]]/td[@class="wartosc"]').text,
        "Język prowadzenia zajęć": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Język prowadzenia zajęć"]]/td[@class="wartosc"]').text,
        "Formy zajęć": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Formy zajęć"]]/td[@class="wartosc"]').text,
        "Jednostka prowadząca": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Jednostka prowadząca"]]/td[@class="wartosc"]').text,
        "Kierownik przedmiotu": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Kierownik przedmiotu"]]/td[@class="wartosc"]').text,
        "Realizatorzy przedmiotu": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Realizatorzy przedmiotu"]]/td[@class="wartosc"]').text,
        "Wymagania wstępne": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Wymagania wstępne"]]/td[@class="wartosc"]').text,
        "Przedmiotowe efekty uczenia się": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Przedmiotowe efekty uczenia się"]]/td[@class="wartosc"]').text,
        "Metody weryfikacji przedmiotowych efektów uczenia się": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Metody weryfikacji przedmiotowych efektów uczenia się"]]/td[@class="wartosc"]').text,
        "Kierunkowe efekty uczenia się": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Kierunkowe efekty uczenia się"]]/td[@class="wartosc"]').text,
        "Formy i warunki zaliczenia przedmiotu": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Formy i warunki zaliczenia przedmiotu"]]/td[@class="wartosc"]').text,
        "Szczegółowe treści przedmiotu": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Szczegółowe treści przedmiotu"]]/td[@class="wartosc"]').text,
        "Literatura podstawowa": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Literatura podstawowa"]]/td[@class="wartosc"]').text,
        "Literatura uzupełniająca": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Literatura uzupełniająca"]]/td[@class="wartosc"]').text,
        "Bilans godzin": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and text()="Bilans godzin"]]/td[@class="wartosc"]').text,
        "Data aktualizacja karty": driver.find_element(By.XPATH, '//tr[td[@class="parametr" and contains(text(), "aktualizacja")]]/td[@class="wartosc"]').text
    }
    return data


# Funkcja obsługująca strukturę alternatywną
def fetch_alternate_structure(driver: webdriver.Chrome, course_url: str) -> Dict[str, Dict]:
    """Obsługuje strukturę alternatywną kart."""
    hierarchical_data = {}

    # Otwórz stronę kursu
    driver.get(course_url)
    wait_for_element(driver, By.XPATH, '//td[@class="wartosc"]//a')

    # Pobierz listę języków
    language_elements = driver.find_elements(By.XPATH, '//td[@class="wartosc"]//a')
    languages = [{"name": lang.text, "link": lang.get_attribute('href')} for lang in language_elements]

    for language in languages:
        language_name = language['name']
        language_link = language['link']

        # Otwórz stronę języka
        driver.get(language_link)
        wait_for_element(driver, By.XPATH, '//td[@class="w2 doSrodka"]//a')

        # Pobierz poziomy
        level_elements = driver.find_elements(By.XPATH, '//td[@class="w2 doSrodka"]//a')
        if not level_elements:
            logging.warning(f"Nie znaleziono poziomów dla {language_name}. Pomijam.")
            continue

        levels = [{"name": level.text, "link": level.get_attribute('href')} for level in level_elements]
        level_data = {}

        for level in levels:
            level_name = level['name']
            level_link = level['link']

            # Otwórz stronę poziomu
            driver.get(level_link)
            wait_for_element(driver, By.XPATH, '//tr[td[@class="parametr" and text()="Kod przedmiotu"]]')
                

            # Pobierz dane z poziomu
            try:
                card_data = fetch_standard_course_data(driver, level_link)
                level_data[level_name] = card_data
            except NoSuchElementException:
                logging.error(f"Nie udało się pobrać danych dla poziomu {level_name}.")
                continue

        hierarchical_data[language_name] = level_data

    return hierarchical_data



# Funkcja główna przetwarzania kursów
def process_course(driver: webdriver.Chrome, course_code: str, course_url: str):
    """Przetwarza dane kursu w zależności od struktury karty."""
    card_type = detect_card_type(driver, course_url)

    if card_type == "standard":
        # Obsługa struktury standardowej
        card_data = None
        try:
            card_data = fetch_standard_course_data(driver, course_url)
        except NoSuchElementException as e:
            logging.error(f"Nie udało się pobrać danych dla kursu {course_code}: {e}")
        if card_data:
            json_filename = f"{course_code}.json"
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(card_data, json_file, ensure_ascii=False, indent=4)
    elif card_type == "alternate":
        # Obsługa struktury alternatywnej
        hierarchical_data = fetch_alternate_structure(driver, course_url)  # Przekazujemy driver i URL
        for language, levels in hierarchical_data.items():
            for level, data in levels.items():
                json_filename = f"{course_code}_{level}.json"
                with open(json_filename, "w", encoding="utf-8") as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
    else:
        logging.warning(f"Nie rozpoznano struktury dla kursu {course_code}. Pomijam kurs.")



# Główna pętla
try:
    for _, row in unique_courses.iterrows():
        course_code = row['Kod kursu']
        course_url = row['Link do kursu']
        
        # Pomijamy wiersze, w których brakuje kodu kursu, linku lub "Kod kursu" zawiera "brak informacji"
        if course_code.strip().lower() == "przedmioty do wyboru z uczelni zagranicznej":
            logging.warning(f"Pominięto wiersz z brakującymi danymi: {course_code}, Link do kursu: {course_url}")
            continue
        
        # Utwórz wyrażenie regularne do sprawdzenia obu przypadków nazw plików
        json_pattern = re.compile(rf"^{re.escape(course_code)}([^.]*)?\.json$")
        
        # Sprawdź, czy istnieje plik pasujący do wzorca
        json_files = [f for f in os.listdir() if json_pattern.match(f)]
        
        if json_files:
            print(f"Plik dla kursu {course_code} już istnieje ({', '.join(json_files)}), pomijanie...")
            continue  # Pomijamy, jeśli istnieje plik pasujący do wzorca
        
        # Przetwarzaj kurs, jeśli plik nie istnieje
        process_course(driver, course_code, course_url)
finally:
    driver.quit()

