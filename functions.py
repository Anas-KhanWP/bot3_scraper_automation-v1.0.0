from pprint import pprint
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
import os
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup

api_key = "CAP-B5AF60896E5D3460063F4148663FAD01"

def bot_setup(headless: bool = False):
    """_This function is used to setup the bot_

    Args:
        headless (bool, optional): _whether to run the bot in headless mode or not_. Defaults to False.

    Returns:
        _selenium.webdriver_: _returns a selenium.webdriver object to be used_
    """
    user_agents = [
        # Add your list of user agents here
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]

    # select random user agent
    user_agent = random.choice(user_agents)

    # options to be used
    options = webdriver.ChromeOptions()
    prefs = {
        'printing.print_preview_sticky_settings.appState': '{"recentDestinations":[{"id":"Save as PDF","origin":"local","account":"null"}],"selectedDestinationId":"Save as PDF","version":2}',
        'savefile.default_directory': 'F:\\Project Backups\\Backup 12-6-24\\GitHub\\bot3_scraper_automation-v1.0.0',  # Change to your desired save path
    }
    options.add_experimental_option('prefs', prefs)
    options.add_argument('--kiosk-printing')  # Enable kiosk printing mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options.add_argument('--blink-settings=imagesEnabled=false')
    # pass in selected user agent as an argument
    options.add_argument(f'user-agent={user_agent}')

    # Add additional options to avoid Cloudflare detection
    options.add_argument("--disable-web-security")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # if headless==True, make the bot headless
    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(),
        options=options,
    )
    # setup implicit wait
    driver.implicitly_wait(3)
    driver.maximize_window()
    return driver


def get_urls_from_file():
    """Read the URLs from input file and return them as a dictionary."""
    # Get the input file path
    input_file_path = os.path.join(os.getcwd(), "Links.xlsx")

    try:
        # Read the input file
        df = pd.read_excel(input_file_path)
        # Check if "URL" and "mapwise" columns exist
        if "LINK" not in df.columns:
            raise KeyError("Link column not found in Links.xlsx")

        # Modify the URLs and store them in a dictionary
        urls_ = []
        for index, row in df.iterrows():
            if pd.notnull(row["Case Available"]):
                original_url = row["LINK"].strip()
                urls_.append(original_url)

        pprint(urls_)
        return urls_

    except FileNotFoundError:
        print("Links.xlsx file not found")
        exit()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
def scrape_broward_data(driver, url, case_number):
    """
    This function is used to scrape data from the Broward County Court website.
    It navigates to the specified URL, enters the case number, and downloads the PDF of the Notice of Appearance.

    Parameters:
    driver (selenium.webdriver): The Selenium WebDriver object used for browser automation.
    url (str): The URL of the Broward County Court website.
    case_number (str): The case number to search for.

    Returns:
    str: A message indicating the status of the PDF download.
    """
    case_number_search = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space(text())='Case Number' and @data-toggle='tab']")))
    case_number_search.click()
    
    case_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "CaseNumber")))
    case_input.clear()
    case_input.send_keys(case_number, Keys.RETURN)
    
    refined_case_number = case_number.replace('-', '')
    
    case_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space(text())='{refined_case_number}']")))
    case_link.click()
    
    noa = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//b[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='notice of appearance']/ancestor::tr")))
    
    if noa:
        pdf_button = WebDriverWait(noa, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "glyphicon.glyphicon-file")))
        pdf_button.click()
        
        # Wait for the new tab to open (browser handles should now be more than one)
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        handles = driver.window_handles
        print(len(handles))
        driver.switch_to.window(handles[-1])
        print("Switched to the new tab!")
        
        view_all_pages = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='View All Pages']")))
        sleep(1)
        view_all_pages.click()        
        sleep(1)
                
        # Wait for the element with id="plugin" to be present
        plugin_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )

        pdf_url = plugin_element.get_attribute("src")

        # Extract cookies from the Selenium session and pass them to the requests session
        session = requests.Session()

        # Get cookies from the Selenium browser and add them to the requests session
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        response = session.get(pdf_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the PDF file
            with open("downloaded_pdf.pdf", 'wb') as file:
                file.write(response.content)
            print("PDF downloaded successfully!")
            return "PDF Downloaded"
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}")
            return "Error While Download PDF"
        
        
        
def scrape_Hillsborough_data(driver, url, case_number):
    """ 
    Function to scrape Hillsborough court case data using the case number.
    
    Sample Case Number Breakdown:
       - County Designator: 29 (First 2 digits of the case number)
       - Year: 23 (Last 2 digits of 2023 - after County Designator)
       - Court Type: CA (2 letters after Year)
       - Case Number: 001143 (6 digits after Court Type)
       - Party Designator: 001HC (Last digits of the case number)
    
    Args:
        driver: Selenium WebDriver instance.
        url: The URL to visit.
        case_number: The full case number as a string.
    
    Sample Case Number: 292023CA001143A001HC
    """
    
    # Split case number into components
    county_designator = case_number[:2]
    year = case_number[4:6]
    court_type = case_number[6:8]
    case_num = case_number[8:14]
    party_designator = case_number[15:]
    
    print(f"County Designator: {county_designator}")
    print(f"Year: {year}")
    print(f"Court Type: {court_type}")
    print(f"Case Number: {case_num}")
    print(f"Party Designator: {party_designator}")
    
    year_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "txtYear")))
    year_input.clear()
    year_input.send_keys(year)
    
    court_type_div = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ddlCourtType")))
    dropdown = Select(court_type_div)
    dropdown.select_by_value(court_type.upper())
    
    case_num_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "txtNumber")))
    case_num_input.clear()
    case_num_input.send_keys(case_num)
    
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "btnSubmitCaseSearch"))).click()
    
    details_button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "details")))
    details_button.click()
    
    # Wait for the new tab to open (browser handles should now be more than one)
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
    handles = driver.window_handles
    print(len(handles))
    driver.switch_to.window(handles[-1])
    print("Switched to the new tab!")
    
    events_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-bs-target='#nav-CaseEvents' and @data-bs-toggle='tab']")))
    
    events_tab.click()
    
    noa = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//td[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='notice of appearance']/ancestor::tr")))
    if noa:
        docimg = WebDriverWait(noa, 10).until(EC.presence_of_element_located((By.XPATH, ".//button[@class='docimg']")))
        sleep(1)
        docimg.click()
        
        try:
            # Wait for the new tab to open (browser handles should now be more than one)
            WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 2)
            handles = driver.window_handles
            print(f"Number of open windows/tabs: {len(handles)}")
            new_tab_handle = handles[-1]
            driver.switch_to.window(new_tab_handle)
            print(f"Switched to the new tab with handle: {new_tab_handle}")
            print(f"Title of the new tab: {driver.title}")
            
            sleep(5)
        except:
            print("do it!")
            sleep(100)
            
        driver.execute_script('window.print();')
        return "PDF Downloaded"
    
    else:
        # print("No NOA found.")
        return "No NOA Found"

def solve_captcha(url):
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": '0x4AAAAAAAR0Af-5MfzdbO3p',
            "websiteURL": url,
            "metadata": {
                "action": ""  # optional
            }
        }
    }
    # Step 1: Send the captcha to CapSolver
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    pprint(resp)
    task_id = resp.get("taskId")
    
    # Step 2: Wait for the captcha to be solved
    while True:
        sleep(5)  # Wait a few seconds before checking again
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        print("==========================")
        pprint(resp)
        print("==========================")
        status = resp.get("status")
        
        if status == 'ready':
            return resp.get("solution", {}).get('token')
        
        if status == 'failed':
            raise Exception("Failed to solve captcha: " + resp.get('errorCode'))

def scrape_Marion_data(driver, url, case_number):
    """ 
    Function to scrape Marion court case data using the case number.
    
    Args:
        driver: Selenium WebDriver instance.
        url: The URL to visit.
        case_number: The full case number as a string.
        api_key: Your CapSolver API key.
        
        422022CA000497CAAXXX
        
        2:5 [2022] = Year
    """
    
    # Split case number into components
    year = case_number[2:6]
    case_num = case_number[8:14]
    
    print(f"Year: {year}")
    print(f"Case Number: {case_num}")
    
    go_to_pub = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_idt47:j_idt50")))
    go_to_pub.click()
    
    agree = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_idt42:j_idt44")))
    agree.click()
    
    case_search = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Case Search']")))
    case_search.click()
    
    # Wait for captcha to appear and solve it
    sleep(5)  # Wait for the page to load
    current_url = driver.current_url
    print(f"Current URL: {current_url}")
    
    captcha_response = solve_captcha(current_url)
    
    # Here, you will need to set the captcha response in the relevant input field
    captcha_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "cf-turnstile-response")))
    driver.execute_script(f"arguments[0].value='{captcha_response}'", captcha_input)
    
    print("executed")
    
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'form:search_tab:year'))).send_keys(year)
    
    selector = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'form:search_tab:cs_court1')))
    selector.click()
    
    ca_sel = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'form:search_tab:cs_court1_2')))
    ca_sel.click()
    
    seq_sel = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "form:search_tab:seq")))
    seq_sel.clear()
    seq_sel.send_keys(case_num, Keys.RETURN)
    
    court_type_div = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "form:docketDataTable1:j_id3")))
    dropdown = Select(court_type_div)
    dropdown.select_by_value('15000')
    
    # Find the <td> containing "notice of appearance" (ignoring case)
    notice_td = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH, "//td[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'notice of appearance')]//ancestor::tr"
        ))
    )
    
    if notice_td:
        print(notice_td.get_attribute('outerHTML'))  # Debugging: print the outer HTML of the found <td>
        
        print("FOUND!!!!!!!!!!!!!!!!!!!!!!")
        
        # Extract the numeric part from the last <td> in the same <tr>
        last_td = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//td[last()]"))
        )
        page_count = last_td.text.strip().split('s')[1]  # Get the text from the last <td> and strip any whitespace
        print(f"Page Count = {page_count}")
        numeric_part = re.search(r'\d+', page_count)  # Extract the numeric part
        
        # Now, find the <a> element with title 'docketImage' within the same <tr> as the <td> found
        pdf_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ".//a[@title='docketImage']"))
        )
        
        # Click the link
        pdf_link.click()
        
        # Wait for the new tab to open (browser handles should now be more than one)
        WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)
        handles = driver.window_handles
        print(f"Number of open windows/tabs: {len(handles)}")
        new_tab_handle = handles[-1]
        driver.switch_to.window(new_tab_handle)
        print(f"Switched to the new tab with handle: {new_tab_handle}")
        print(f"Title of the new tab: {driver.title}")
    
        # Extract cookies from the Selenium session and pass them to the requests session
        session = requests.Session()

        # Get cookies from the Selenium browser and add them to the requests session
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        pdf_url = driver.current_url
        print(pdf_url)

        if numeric_part:
            # Replace anything after "pages=" in pdf_url with the numeric part
            new_pdf_url = re.sub(r'(pages=)\d+', r'\1' + numeric_part.group(), pdf_url)
            print(f"Updated PDF URL: {new_pdf_url}")
        else:
            print("No numeric part found in the last <td>.")
        
        response = session.get(new_pdf_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the PDF file
            with open("downloaded_pdf2.pdf", 'wb') as file:
                file.write(response.content)
            print("PDF downloaded successfully!")
            return "PDF Downloaded"
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}")
            return "Error While Download PDF"
            
        driver.execute_script('window.print();')
        return "PDF Downloaded"


    
    # sleep(10)

    # driver.execute_script("arguments[0].style.display = 'block';", captcha_input)  # Make it visible
    # captcha_input.send_keys(captcha_response)
    
    # Submit the form or continue with your scraping logic
    # submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit-button-id")))  # Replace with actual ID
    # submit_button.click()

    # Continue with the rest of your scraping logic...

        
        
        
        

if __name__ == '__main__':
    driver = bot_setup()
    urls_dict = get_urls_from_file()
    
    for url in urls_dict:
        # if 'broward' in url:
        #     driver.get(url)
        #     pdf_status = scrape_broward_data(driver, url, "CACE-22-005167")
        # if 'hillsclerk' in url:
        #     driver.get(url)
        #     pdf_status = scrape_Hillsborough_data(driver, url, "292023CC114679A001HC")
        if 'civitekflorida' in url:
            driver.get(url)
            pdf_status = scrape_Marion_data(driver, url, "422022CA000497CAAXXX")
        