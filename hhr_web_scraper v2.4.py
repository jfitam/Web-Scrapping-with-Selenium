#!/usr/bin/env python
# coding: utf-8

# In[1]:


# v2.1 remove the deletion of all table before start. will delete, instead each day before inserting with new information
# v2.2 add many tries to avoid unnecessary timeout errors
# v2.3 it is possible to take the trains information without the prices and solve the problem of sold out trains
# v2.4 recharge the website at the end of every day
print("HHR Scraper version 2.4")


# In[2]:


#!pip install selenium
#!pip install pandas
#!pip install webdriver-manager


# In[3]:


# connection to the database
print("Connecting to the database...")
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import text

# Create an engine instance
alchemyEngine = create_engine("postgresql+psycopg2://postgres:Renfe2022@172.19.28.174:5433/SalesSystem", pool_recycle=5);

# Connect to PostgreSQL server
conn = alchemyEngine.connect();

#Setting auto commit false
conn.autocommit = True


# In[4]:


# set the environment
print("Loading dependencies...")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import date
from datetime import datetime
import time
import os

# constants for the web search
HHR_URL = "https://sar.hhr.sa/#"
STATIONS = ['Makkah', 'Al-Sulimaniyah - JEDDAH', 'AIRPORT - JEDDAH', 'KAEC', 'Madinah']


# paths for the next screens
XPATH_RESULT_GRID = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:dtSearchResult_data\"]"

# set the browser
print("Opening the browser...")
ChromeDriverManager().install()
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
actions = ActionChains(driver)


# In[5]:


# function to convert select the desired date in the control of the website
def pick_date(driver, date, is_home_page=False):
    from dateutil.parser import parse
    import datetime
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select
    
    # parameters
    XPATH_DATE = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:calendar\"]"
    CLASS_CALENDAR_POPUP = "calendars-popup"
    CLASS_SELECTS_MONTH_YEAR = "calendars-month-year"
    wait = WebDriverWait(driver, 20)
    if is_home_page:
        XPATH_DATE = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_departureDate\"]"
    
    # open the popup
    date_field = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_DATE)))
    wait.until(EC.element_to_be_clickable(date_field))
    actions.move_to_element(date_field).click().perform()
    
    # select the elements
    calendar_popup = wait.until(EC.presence_of_element_located((By.CLASS_NAME, CLASS_CALENDAR_POPUP)))
    selects_month_year = calendar_popup.find_elements(By.CLASS_NAME, CLASS_SELECTS_MONTH_YEAR)
    month_select = Select(selects_month_year[0])
    year_select = Select(selects_month_year[1])
    
    # parse date
    if(isinstance(date, str)):
        selected_date = parse(date)
    elif(isinstance(date, datetime.date)):
        selected_date = date
    else:
        raise Exception("The parameter it is not a date or a date representative")
        
    #select the date
    year_select.select_by_visible_text(str(selected_date.year))
    month_select.select_by_value("{}/{}".format(selected_date.month, selected_date.year))
    calendar_popup.find_element(By.XPATH,"//a[text()='{}']".format(selected_date.day)).click()


# In[6]:


def load_page(driver, station_from, station_to, day, is_home_page=False):
    # xpaths for the elements
    XPATH_FORM = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel\"]"
    XPATH_STATION_FROM = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:comboStationFrom\"]"
    XPATH_STATION_TO = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:comboStationTo\"]"
    XPATH_SUBMIT = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:search\"]"
    
    if is_home_page:
        # paths for the first screen (only used as default values the first time)
        XPATH_FORM = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_ticketSearchForm\"]"
        XPATH_STATION_FROM = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_fromStation\"]"
        XPATH_STATION_TO = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_toStation\"]"
        XPATH_SUBMIT = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_ticketSearchForm\"]/div[1]/div[5]/button"
        #XPATH_CAPTCHA_IMG = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_captcha\"]"
        #XPATH_CAPTCHA_TEXT = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_captchaText\"]"
        #XPATH_CAPTCHA_REFRESH = "//*[@id=\"_FlatHhrTicketSearch_INSTANCE_skyYrGajl2I9_refreshCaptcha\"]"
    
    # call for the services
    Select(wait.until(EC.presence_of_element_located((By.XPATH, XPATH_STATION_FROM)))).select_by_visible_text(station_from)
    time.sleep(0.2)
    Select(wait.until(EC.presence_of_element_located((By.XPATH, XPATH_STATION_TO)))).select_by_visible_text(station_to)
    pick_date(driver, day, is_home_page)
    time.sleep(0.2)
    wait.until(EC.presence_of_element_located((By.XPATH, XPATH_SUBMIT))).click()


# In[7]:


XPATH_LUGGAGE_ACCEPTANCE = "//button[contains(@id, 'dialogFormInfoBaggage')]"

# load the website
print("Loading the website...")
driver.get(url=HHR_URL)
try:
    load_page(driver,STATIONS[0],STATIONS[1],date.today(),True)
except:
    pass
input("Please, continue to the second screen and press enter to continue...")
alert_window = driver.find_elements(By.XPATH, XPATH_LUGGAGE_ACCEPTANCE)
if alert_window:
    alert_window[0].click()


# In[ ]:


## retrieve the info

# set the last date to check
date_start = input("Indicate the first date to check (format yyyy/mm/dd):")
date_end = input("Indicate the last date to check (format yyyy/mm/dd):")

# asking if the prices should be scraped (with prices, much slower)
answer_prices = input("Do you want to get the prices?(y/n)")
with_prices = answer_prices.lower() == 'y' or answer_prices.lower() == 'yes'

# scrap
print("[{}] Beginning the scrapping... ".format(datetime.now().strftime("%H:%M:%S")))

for day in pd.date_range(start=date_start, end=date_end):
   
    # restart the lists
    timestamps = []
    hours_from = []
    hours_to = []
    stations_from = []
    stations_to = []
    train_numbers = []
    dep_dates = []
    classes = []
    tariff_names = []
    tariff_prices = []
    
    
    for station_from in STATIONS:
        for station_to in STATIONS:
            
            # skip the combination if the station from and the station to are the same
            if station_from == station_to:
                continue
                                       
            # get the main grid
            for attempt in range(10):
                try:
                    load_page(driver, station_from, station_to, day)

                    #wait for the results
                    result_grid = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_RESULT_GRID)))

                    # get the elements
                    services = result_grid.find_elements(By.XPATH, "./tr[@role='row']")
                        
                except:
                    time.sleep(5)
                    if(attempt == 9):
                        attempt == 0
                    else:
                        time.sleep(1)
                    continue
                else:
                    break

            # take the basic information about the trains
            for i in range(len(services)):
                for attempt in range(10):
                    try:
                        # locate the row in the DOM
                        xpath_row = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:dtSearchResult_data\"]/tr[@data-ri={}]".format(str(i))
                        tr = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_row)))
                        childs = tr.find_elements(By.XPATH, "./td")

                        # take the common info
                        train_number = childs[4].find_element(By.CLASS_NAME, "train-code").text
                        sold_out_text = childs[4].find_element(By.CLASS_NAME, "train-code").find_element(By.XPATH, 'following-sibling::*[1]').text
                        is_sold_out = sold_out_text == 'SOLD OUT'
                        hour_from = childs[1].text[0:5]
                        hour_to = childs[2].text[0:5]
                        
                        # detect if the train is sold out
                        
                        
                    except:
                        if(attempt == 9):
                            attempt == 0
                        else:
                            time.sleep(5)
                        continue
                    else:
                        break
            
                
                for class_num in range(2):
                    # save the basic information about the train
                    timestamps.append(datetime.now())
                    dep_dates.append(day)
                    train_numbers.append(train_number)
                    stations_from.append(station_from)
                    stations_to.append(station_to)
                    hours_from.append(hour_from)
                    hours_to.append(hour_to)

                    # if the prices won't be appended later, won't repeat the insertion of train data
                    if(not with_prices or is_sold_out):
                        classes.append('Undefined')
                        break
                    # end if(!with_prices)
                # end for(2)

                if (with_prices and not is_sold_out):
                    # open the fares to take the prices (if requested)
                    for attempt in range(10):     
                        try:
                            # open the fare
                            driver.execute_script("window.scrollBy(0 , 175 );")
                            tr.click()
                            
                            # get the tabs
                            xpath_to_fare_selection = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:dtSearchResult:{row}:tabViewTariff\"]".format(row=str(i))
                            tr_fare_selection = wait.until(EC.presence_of_element_located((By.XPATH, xpath_to_fare_selection)))
                            tariff_name_fields = tr_fare_selection.find_elements(By.XPATH, ".//td[contains(@class,'tariff-name')]")
                            tariff_price_fields = tr_fare_selection.find_elements(By.XPATH, ".//td[contains(@class,'tariff-price')]")
                            
                            # retrieve the tabs
                            for j in range(2):
                                # get the fare info
                                xpath_to_class_selection = "//*[@id=\"_ossportlet_WAR_ossliferay_:formSearchTravel:dtSearchResult:{row}:tabViewTariff\"]/ul/li[{tab}]".format(row=str(i), tab=str(j+1))
                                class_tab = wait.until(EC.presence_of_element_located((By.XPATH, xpath_to_class_selection)))
                                #class_tab.click()
                                class_name = class_tab.text.capitalize()
                                tariff_name = tariff_name_fields[j].get_attribute("textContent")
                                tariff_price = tariff_price_fields[j].get_attribute("textContent")[:-4]
                                
                                # save the information in the lists
                                classes.append(class_name)
                                tariff_names.append(tariff_name)
                                tariff_prices.append(tariff_price)
                                if tariff_prices[-1] == '':
                                    tariff_prices[-1] = '0'
                            # end for fares
                        except:
                            if(attempt == 9):
                                attempt == 0
                            else:
                                time.sleep(5)
                            continue
                        else:
                            break
                    # end for attempt(10)
                elif (with_prices and is_sold_out):
                    #generate empty prices and fares
                    tariff_names.append('undefined')
                    tariff_prices.append(0)
                
                # end if(with_prices or not is_sold_out)
                
            # end for len(services) 

            # scroll back at the beginning
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # click the refresh link
            xpath_refresh = "//a[contains(@class, 'alert-link')]"
            alert_link = driver.find_elements(By.XPATH, xpath_refresh)
            if alert_link:
                alert_link[0].click()
                    
    
    
    # at the end of the day, insert the info in the database
    if(with_prices):
        df = pd.DataFrame({'timestamp':timestamps, 'departure_date_short':dep_dates, 'train_number':train_numbers,'station_from':stations_from,'station_to':stations_to,'class_fare':classes,'departure_hour':hours_from,'arrival_hour':hours_to,'fare_name':tariff_names,'price':tariff_prices})
    else:
        df = pd.DataFrame({'timestamp':timestamps, 'departure_date_short':dep_dates, 'train_number':train_numbers,'station_from':stations_from,'station_to':stations_to,'class_fare':classes,'departure_hour':hours_from,'arrival_hour':hours_to})
        df['fare_name'] = 'undefined'
        df['price'] = 0
    
    # change empty prices per 0
    if(with_prices):
        df.loc[df['price']=='', 'price'] = '0'
    
    # truncate the info in the database
    query = "DELETE FROM \"AFC\".trains_on_sale WHERE departure_date_short = '{}'".format(day.strftime("%Y-%m-%d"))
    conn.execute(text(query))
    
    # export
    for ind in df.index:
        values = ', '.join(f"'{value}'" for value in df.iloc(0)[ind].values)
        columns = ', '.join(df.keys())
        query = f"INSERT INTO \"AFC\".trains_on_sale ({columns}) VALUES ({values})"
        conn.execute(text(query))
    conn.commit()
    print("[{}] Day {} succesfully inserted in the database".format(datetime.now().strftime("%H:%M:%S"),day.strftime("%Y-%m-%d")))
        
    # refresh the website to extend the link
    # driver.refresh()
    
    
print("[{}] Finished".format(datetime.now().strftime("%H:%M:%S")))
input("Press enter to finish the program")


# In[ ]:


# closing connection
driver.quit()
conn.close()


# In[ ]:


#query = f"ROLLBACK"
#conn.execute(text(query))

