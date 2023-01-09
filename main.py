def main():
    import pandas as pd
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as ec

    options = webdriver.ChromeOptions()

    # To stop NPCI website from detecting Selenium use and blocking us For more info,
    # visit: https://newbedev.com/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detection
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://www.npci.org.in/what-we-do/upi/product-statistics"
    driver.get(url)

    try:
        # Wait till the table is loaded
        wait_to_load = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.XPATH, "/html/body/section[3]/div/div/div[2]/div/table")))

    except:
        print("Took more than 15 secs to load")

    else:
        # Using BS4, get the table, convert to pandas DF and csv format.
        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find_all('table', class_="table table-bordered")

        upi_stats = pd.read_html(str(table))
        upi_data = pd.DataFrame(upi_stats[0])
        print(upi_data)
        upi_data.to_csv("latest_upi_data.csv")

    finally:
        driver.quit()


if __name__ == '__main__':
    main()
