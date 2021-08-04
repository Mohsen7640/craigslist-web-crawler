from selenium import webdriver

PATH = r'chromium.chromedriver'

auth = {
    'email': '',
    'password': ''
}


def get_cookie():
    with webdriver.Chrome(executable_path=PATH) as driver:
        driver.implicitly_wait(50)
        driver.get("https://dubai.dubizzle.com/")

        login_popup = driver.find_element_by_xpath(
            '//*[@id="page-wrapper"]/div[1]/div[2]/div[1]/div/div[2]/button[3]'
        )
        login_popup.click()

        login_by_email = driver.find_element_by_xpath(
            '//*[@id="popup_login_link"]')
        login_by_email.click()

        email = driver.find_element_by_xpath('//*[@id="popup_email"]')
        email.clear()
        email.send_keys(auth['email'])

        password = driver.find_element_by_xpath('//*[@id="popup_password"]')
        password.clear()
        password.send_keys(auth['password'])

        login_button = driver.find_element_by_xpath(
            '//*[@id="popup_login_btn"]')
        login_button.click()

        cookie = driver.get_cookies()

    return cookie


if __name__ == '__main__':
    print(get_cookie())
