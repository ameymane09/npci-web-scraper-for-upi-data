import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select


def selenium_setup():
    global driver
    options = webdriver.ChromeOptions()

    # To stop NPCI website from detecting Selenium use and blocking us For more info,
    # visit: https://newbedev.com/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detection
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def upi_total_transactions(url):
    driver.get(url)

    try:
        # Wait till the table is loaded
        WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.XPATH, "/html/body/section[3]/div/div/div[2]/div/table")))

    except TimeoutError:
        print("Took more than 15 secs to load")

    else:
        # Using BS4, get the table, convert to pandas DF and csv format.
        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find_all('table', class_="table table-bordered")

        upi_stats = pd.read_html(str(table))
        upi_data = pd.DataFrame(upi_stats[0])
        upi_data.to_csv("latest_upi_transaction_stats.csv")
        print("\n\nCSV file with UPI transactions data saved to drive.")


def total_uptime_stats(url):
    driver.get(url)

    try:
        # Wait till the table is loaded
        WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.ID, "yearDD")))

    except TimeoutException:
        print("Took more than 15 secs to load")

    else:
        # Get a list of available months from the dropdown menu
        soup = BeautifulSoup(driver.page_source, 'lxml')
        months = soup.find_all("select", class_="floatlabel filled")
        month_list = [month.text.strip().split("\n") for month in months]
        month_list = month_list[0]

        uptime_list = []

        # Select a month in the dropdown and get data from it
        for month in month_list:
            month_dropdown = Select(driver.find_element(By.ID, "yearDD"))
            month_dropdown.select_by_visible_text(month)

            WebDriverWait(driver, 5).until(
                ec.presence_of_element_located((By.CLASS_NAME, "table-responsive")))

            npci_uptime = driver.find_element(By.XPATH,
                                              "//*[@class='hideDD'][@style='']/div[1]/table/tbody/tr/td[2]"). \
                get_attribute("textContent").strip()

            uptime_dict = {
                "Month": month,
                "Uptime_Percent": npci_uptime
            }

            try:
                downtime = driver.find_element(By.XPATH,
                                               "//*[@class='hideDD'][@style='']/div[2]/table/thead/tr[3]/td[2]"). \
                    get_attribute("textContent").strip()
                incidents = driver.find_element(By.XPATH,
                                                "//*[@class='hideDD'][@style='']/div[2]/table/thead/tr[3]/td[3]"). \
                    get_attribute("textContent").strip()

                uptime_dict["Downtime_mins"] = downtime
                uptime_dict["Incidents"] = incidents

            except NoSuchElementException:
                pass

            finally:
                uptime_list.append(uptime_dict)

    finally:
        driver.quit()

    uptime_df = pd.DataFrame.from_dict(uptime_list)
    uptime_df.to_csv("upi_uptime_stats.csv")
    print("\n\nCSV file with UPI uptime data saved to drive.")


if __name__ == '__main__':
    start = time.time()

    selenium_setup()
    upi_total_transactions("https://www.npci.org.in/what-we-do/upi/product-statistics")
    total_uptime_stats("https://www.npci.org.in/what-we-do/upi/uptime-upi-month-wise")

    end = time.time()
    print(f"\n\nTotal time for the program to execute: {round(end - start, 2)}s")
