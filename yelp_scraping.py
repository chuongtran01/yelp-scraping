from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd


def find_num_pages(element):
    pages = WebDriverWait(element, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@role, "navigation")]')))

    num_of_pages = pages.find_element_by_xpath(
        './div[2]').text.split()[-1]

    return int(num_of_pages)


def find_review_section(element):
    user_names = []
    user_locations = []
    user_ratings = []
    user_dates = []
    user_reviews = []

    review_section = element.find_element_by_xpath(
        '//section[contains(@aria-label, "Recommended Reviews")]')

    reviews_list_container = review_section.find_element_by_xpath(
        './/ul[contains(@class, " list__09f24__ynIEd")]')

    reviews = reviews_list_container.find_elements_by_xpath('.//li')

    for review in reviews:
        inner_container = review.find_element_by_xpath("./div")

        user_information = inner_container.find_element_by_xpath(
            './/div[contains(@class,"css-1w3ky6t")]')

        # Fetching name and location
        user_name = user_information.find_element_by_xpath(
            ".//span/a[@href]").text

        user_location = user_information.find_element_by_xpath(
            './/span[contains(@class, " css-qgunke")]').text

        review_date = inner_container.find_element_by_xpath(
            './/span[contains(@class, " css-chan6m")]').text

        review_rating = inner_container.find_element_by_xpath(
            './/div[contains(@role, "img")]').get_attribute('aria-label')

        user_review_text = inner_container.find_element_by_xpath(
            './/p[contains(@class, "comment__09f24__D0cxf css-qgunke")]').text

        user_names.append(user_name)
        user_locations.append(user_location)
        user_dates.append(review_date)
        user_reviews.append(" ".join((user_review_text).split()))
        user_ratings.append(review_rating.split()[0])

    return user_names, user_dates, user_locations, user_reviews, user_ratings


def launchBrower():
    options = Options()
    options.headless = False
    # options.add_argument('window-size=1920x1080')
    options.add_experimental_option("detach", True)

    website = "https://www.yelp.com/biz/san-dong-noodle-house-%E5%B1%B1%E6%9D%B1%E9%BA%B5%E9%A4%A8-houston"
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(website)
    driver.maximize_window()  # Don't work well with headless = True

    return driver


def main():
    driver = launchBrower()

    time.sleep(5)

    num_of_pages = find_num_pages(driver)

    cur_page = 1

    user_names = []
    user_dates = []
    user_locations = []
    user_reviews = []
    user_ratings = []

    while cur_page <= 2:
        time.sleep((5))

        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "biz-details-page-container-outer__09f24__pZBzx css-1qn0b6x")]')))

        review_details = find_review_section(container)

        user_names.extend(review_details[0])
        user_dates.extend(review_details[1])
        user_locations.extend(review_details[2])
        user_reviews.extend(review_details[3])
        user_ratings.extend(review_details[4])

        cur_page += 1

        try:
            next_page_button = driver.find_element_by_xpath(
                '//a[contains(@aria-label, "Next")]')
            next_page_button.click()
        except:
            pass

    df_books = pd.DataFrame(
        {'user': user_names, 'location': user_locations, 'date': user_dates, 'rating': user_ratings, 'review': user_reviews})
    df_books.to_json('yelp_review.json', orient='records')


if __name__ == '__main__':
    main()
