"""
Guan Chen
EPPS 6317.051
Final Project: Expedia Webscraper
July 2, 2024
"""

from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, date, timedelta
from time import sleep
import pandas as pd

# Collection Parameters
length_of_travel = 9  # Duration of Vacation
collection_length = 5  # Days to collect
start_date = date.today() + timedelta(1) # Starting date
return_date = start_date + timedelta(length_of_travel)  # Returning Date
initial_dates = [start_date, return_date]  # Initial date range

# Starting Parameters
website = "https://www.expedia.com/Flights"
driver = Driver(browser='chrome', headless=False, uc=True)
driver.open(website)
wait = WebDriverWait(driver, timeout=20)


def click_on(xpath):
    # clicks on a button
    return wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def look_for(xpath):
    # finds a single element
    return driver.find_element(By.XPATH, xpath)


if __name__ == '__main__':

    print("I'm in")

    # departure input
    print("Inputting departure...")
    leaving_from_xpath = '//button[@aria-label="Leaving from"]'
    click_on(leaving_from_xpath)
    leaving_from_field_xpath = "//input[@id='origin_select']"
    look_for(leaving_from_field_xpath).send_keys("DFW" + Keys.ENTER)

    # arrival input
    print("Inputting arrival...")
    going_to_xpath = '//button[@aria-label="Going to"]'
    click_on(going_to_xpath)
    going_to_field_xpath = "//input[@id='destination_select']"
    look_for(going_to_field_xpath).send_keys("TPE" + Keys.ENTER)

    # Open the date picker
    print("Setting dates....")
    dates_button = driver.find_element(By.XPATH, '//button[@data-stid="uitk-date-selector-input1-default"]')
    dates_button.click()

    # Initial dates

    # Finding dates
    for date in initial_dates:
        month_year = date.strftime("%B %Y")
        day = date.day
        max_attempts = 12

        for attempt in range(max_attempts):
            try:
                # Find the month table containing the target date
                month_table_xpath = f"//div[contains(@class, 'uitk-date-picker-month')][.//h2[contains(text(), '{month_year}')]]"
                month_table = wait.until(
                    EC.presence_of_element_located((By.XPATH, month_table_xpath))
                )
                # Find and click the specific day within the month table
                date_xpath = f".//button[contains(@class, 'uitk-date-picker-day') and @data-day='{day}']"
                date_element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, date_xpath))
                )
                date_element.click()
                break  # Successfully selected the date, move to next target_date

            except (TimeoutException, NoSuchElementException):
                try:
                    # If the month is not visible, try to navigate to the next month
                    next_button_xpath = "//button[@data-stid='date-picker-paging'][.//svg[@aria-label='Next month']]"
                    next_button = driver.find_element(By.XPATH, next_button_xpath)
                    next_button.click()

                    # Wait for the date picker to update
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(
                            driver.find_element(By.XPATH, "//div[contains(@class, 'uitk-date-picker-month')]"))
                    )
                except (TimeoutException, NoSuchElementException):
                    try:
                        # If next month navigation fails, try to navigate to the previous month
                        prev_button_xpath = "//button[@data-stid='date-picker-paging'][.//svg[@aria-label='Previous month']]"
                        prev_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, prev_button_xpath))
                        )
                        prev_button.click()

                        # Wait for the date picker to update
                        WebDriverWait(driver, 10).until(
                            EC.staleness_of(
                                driver.find_element(By.XPATH, "//div[contains(@class, 'uitk-date-picker-month')]"))
                        )
                    except (TimeoutException, NoSuchElementException):
                        print(f"Cannot navigate to month: {month_year}")
                        break
        else:
            print(f"Could not find or select the date {date} after {max_attempts} attempts")

    apply_date_xpath = "//button[@data-stid='apply-date-picker']"
    apply_date_button = driver.find_element(By.XPATH, apply_date_xpath)
    apply_date_button.click()

    # Search button
    search_xpath = "//button[@id='search_button']"
    search_button = driver.find_element(By.XPATH, search_xpath)
    search_button.click()
    print("Ba da bing, ba da boom!")

    collection_date = date.today()
    date_tracker = start_date

    flights_list = []  # initialize flight data storage

    for i in range(collection_length):

        print("Waiting for data to load...")
        try:
            first_flight_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@stid='FLIGHTS_DETAILS_AND_FARES-index-25-leg-0-fsr-FlightsActionButton']")))

            flight_buttons = driver.find_elements(By.XPATH, "//button[@data-test-id='select-link' and @type='button']")

            for button in flight_buttons:
                try:
                    # Extract the text containing hidden information
                    text = button.find_element(By.CSS_SELECTOR, "span.is-visually-hidden").text

                    airline = text.split("for ")[1].split(" flight")[0]  # Extract airline name
                    departure = text.split("departing at ")[1].split(" from")[0]  # Extract departure time
                    arrival = text.split("arriving at ")[1].split(" in")[0]  # Extract arrival time
                    price = text.split("Priced at ")[1].split(" Roundtrip")[0]  # Extract price
                    ttt = text.split("later. ")[1].split(" total travel time")[0]  # Extract total travel time
                    stops = text.split("total travel time, ")[1].split(" stop")[0]  # Extract number of stops

                    if stops == 'One':
                        layover_time = text.split("Layover for ")[1].split(" in ")[0]
                        layover_city = text.split("Layover for ")[1].split("in ")[1].split('.')[0]
                    elif stops == 'Two':
                        time_1 = text.split("Layover for ")[1].split("minute")[0] + 'minutes'
                        city_1 = text.split("Layover for ")[1].split(" in ")[1].split(" • ")[0]
                        time_2 = text.split(" • Layover for ")[1].split(" in ")[0]
                        city_2 = text.split(" • Layover for ")[1].split(" in ")[1].split(".")[0]

                        layover_city = f"{city_1}, {city_2}"
                        layover_time = f"{time_1}, {time_2}"
                    elif stops > 2:
                        layover_city = "Multiple Cities"
                        layover_time = "Multiple Times"
                    elif stops == 0:
                        layover_city = "None"
                        layover_time = "Zero Thousand Hours"
                    else:
                        layover_city = "IDK"
                        layover_time = "IDK"

                    flight_data = {
                        "Airline": airline,
                        "Travel Date": date_tracker,
                        "Return Date": date_tracker + timedelta(length_of_travel),
                        "Departure": departure,
                        "Arrival": arrival,
                        "Price": price,
                        "Total Travel Time": ttt,
                        "Stops": stops,
                        "Layover City": layover_city,
                        "Layover Time": layover_time,
                        "Collection Date": collection_date
                    }
                    flights_list.append(flight_data)

                    # Print to see if the scraper is working
                    print(f"--- Flight Information ---")
                    for key, value in flight_data.items():
                        print(f"{key}: {value}")

                except IndexError:
                    print("Yikes, IndexError!")

                except NoSuchElementException:
                    print("Can't find the element!")

            # Check which button is equal to the next date and click
            date_tracker += timedelta(1)
            tracker_str = f"{date_tracker.strftime('%a, %b ')}{date_tracker.day}"
            next_day_xpath = f'//button[contains(@class, "uitk-date-range-button") and .//span[@class="uitk-date-range-button-date-text" and text()="{tracker_str}"]]'
            next_day_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, next_day_xpath))
            )

            if i == collection_length - 1:
                break
            if next_day_button:
                # Click the button if it's today's date
                next_day_button.click()
                print(f"\n{i + 1}/{collection_length} Complete")
                print(f"Now proceeding to next page...\n\n")
                print(
                    f"Now Processing: DEPARTURES on {date_tracker} and RETURNS on {date_tracker + timedelta(length_of_travel)}")
            else:
                print(f"Button for {tracker_str} not found!")

        except TimeoutException:
            print("Well, this is takin a while... Let's get outta here!\nError: Timeout")
        except StaleElementReferenceException:
            print("Do you taste that too?\nError: StaleElementReference")

    flights_df = pd.DataFrame(flights_list)
    print("--- Flights Dataframe ---")
    print(flights_df)

    flights_df.to_csv(
        f"/Users/guan/Documents/Expedia Scraper/scraped/EXPEDIA_DATA_{date.today().strftime("%Y_%m_%d")}.csv",
        index=False)
    print("All Done!")
    driver.quit()
