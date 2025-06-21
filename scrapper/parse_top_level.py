from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
import time
import pandas as pd
import logging

import hashlib
import os
from helper import extract_link

# Set up the Firefox driver using webdriver-manager for easy driver management
driver = webdriver.Firefox()

supported_programs = ["Programy 2024/25", "Programy 2023/24", "Programy 2022/23", "Programy 2021/22", "Programy 2020/21"]

DEFAULT_LOAD_TIMEOUT = 2


def parse_programs(driver, supported_programs: list[str]):
    buttons = driver.find_elements(By.XPATH, '//div[@id="divMenu"]/ul//button/a')
    return [
        {"text": button.text, "button": button}
        for button in buttons
        if button.text in supported_programs
    ]


def click_into_program(driver, program: str):
    button = driver.find_element(
        By.XPATH, f'//div[@id="divMenu"]/ul//button/a[text()="{program}"]'
    )
    button.click()
    time.sleep(DEFAULT_LOAD_TIMEOUT)


def parse_fields(driver):
    # Pobiera wszystkie linki do kierunków na stronie bez ograniczeń
    fields_links = driver.find_elements(By.XPATH, '//div[@id="divMenu"]//ul//div//ul//a')
    return [
        {"text": field.text, "link": field.get_attribute("href")}
        for field in fields_links
    ]


def click_field(driver, field):
    driver.get(field["link"])
    time.sleep(DEFAULT_LOAD_TIMEOUT)


def generate_id(row):
    # Concatenate all column values in the row
    concat_str = "".join(row.values)
    # Compute the hash of the concatenated string
    return hashlib.md5(concat_str.encode()).hexdigest()  # Using md5 for brevity


def parse_table_rows(driver):
    table_rows_handles = driver.find_elements(
        By.XPATH, '//div[@class="info"]/table/tbody/tr'
    )
    items = []
    for table_row_handle in table_rows_handles:
        if table_row_handle.get_attribute("class") == "bez_ramki":
            degree_text = table_row_handle.find_element(By.XPATH, "th/p").text
            items.append({"degree": degree_text})
        else:
            wydzial = table_row_handle.find_element(
                By.XPATH, './/td[@class="programWydzial"]/h2/a'
            ).get_attribute("title")
            items[-1]["wydzial"] = wydzial
            # parsujemy reszta
            other_datas = table_row_handle.find_elements(
                By.XPATH,
                './/tr[td[@class="programWydzial"]]/td[@class="p"]/table/tbody/tr',
            )
            other = []
            base_url = driver.current_url
            for other_data in other_datas:
                form_of_studies = other_data.find_element(By.XPATH, "./td[1]/p").text
                course = other_data.find_element(
                    By.XPATH, "./td[position() = 2]//a"
                ).text
                onclick = other_data.find_element(
                    By.XPATH, "./td[position() = 2]//a"
                ).get_attribute("onclick")
                other.append(
                    {
                        "form_of_studies": form_of_studies,
                        "course": course,
                        "link": extract_link(onclick, base_url),
                    }
                )

            items[-1]["other"] = other
    return items


try:
    # Otwieranie strony
    driver.get("https://programy.p.lodz.pl/ectslabel-web/")
    time.sleep(DEFAULT_LOAD_TIMEOUT)  # Czekanie na załadowanie strony

    # Znalezienie i kliknięcie przycisku z linkiem do programu roku
    programs = parse_programs(driver, supported_programs)
    for program in programs:
        click_into_program(driver, program["text"])

        program["fields"] = parse_fields(driver)
        for field in program["fields"]:
            try:  # some fields are empty
                click_field(driver, field)
                field["items"] = parse_table_rows(driver)
            except Exception as e:
                logging.error(f"Error while parsing field {field['text']}: {e}")

    def generator():
        for program in programs:
            # Check if 'fields' key is present in the program
            if "fields" not in program:
                logging.warning("Missing 'fields' in program")
                continue

            for field in program["fields"]:
                # Check if 'items' key is present in the field
                if "items" not in field:
                    logging.warning("Missing 'items' in field")
                    continue

                for item in field["items"]:
                    # Check if 'other' key is present in the item
                    if "other" not in item:
                        logging.warning("Missing 'other' in item")
                        continue

                    for other in item["other"]:
                        # Check for each field individually before yielding
                        if (
                            "text" in program
                            and "text" in field
                            and "degree" in item
                            and "wydzial" in item
                            and "form_of_studies" in other
                            and "course" in other
                            and "link" in other
                        ):
                            yield (
                                program["text"],
                                field["text"],
                                item["degree"],
                                item["wydzial"],
                                other["form_of_studies"],
                                other["course"],
                                other["link"],
                            )
                        else:
                            # Log a warning if any field is missing
                            logging.warning(
                                "Missing required fields in nested structure"
                            )

    g = generator()

    try:
        df = pd.DataFrame(
            g,
            columns=[
                "Program",
                "Kierunek",
                "Stopień",
                "Wydział",
                "Forma studiów",
                "Kierunek studiów",
                "Link",
            ],
        )  # Use the first tuple as column names
        df["ID"] = df.apply(generate_id, axis=1)
        # File path
        csv_file = "top_level.csv"

        # Check if the file exists
        if os.path.exists(csv_file):
            # Read the existing CSV data
            df_existing = pd.read_csv(csv_file)

            # Concatenate the new data with the existing data
            df_combined = pd.concat([df_existing, df], ignore_index=True)

            # Drop duplicate rows based on the 'ID' column, keeping the latest occurrence
            df_combined = df_combined.drop_duplicates(subset="ID", keep="last")
            # Write the combined DataFrame back to the CSV, overwriting the existing file
            df_combined.to_csv(csv_file, index=False)
        else:
            # If the file doesn't exist, write the new data to the CSV directly
            df.to_csv(csv_file, index=False)
    except Exception as e:
        logging.error(f"Error while putting the results into csv: {e}")
        print(df)

finally:
    # Close the browser after a delay to see the result
    print("We are shutting down the webbrowser...")
    driver.quit()
