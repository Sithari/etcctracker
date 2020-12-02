#!/usr/bin/env python3
# This code watches a file for new entries to check for reservation spot openings. It then alerts via email if
# any are seen.

# Written by Rakesh Passa
# 11-30-2020


import requests
import json
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
import random

def get_data(date):
    url = 'https://app.rockgympro.com/b/widget/?a=equery'
    headers = {
        'Host': 'app.rockgympro.com',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Language': 'en-us',
        'Accept-Encoding': 'br, gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://app.rockgympro.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
        'Connection': 'keep-alive',
        'Referer': 'https://app.rockgympro.com/b/widget/?a=offering&offering_guid=2923df3b2bfd4c3bb16b14795c569270&random=5fbf48c67e946&iframeid=&mode=p',
        'Content-Length': '1550',
        'Cookie': 'AWSELB=A5EDC1071EB54DEE085FA9BC53DB5910EF75B9C87F1017073E8B0D71F097020F81072E969926CF7FF56E9A38BD28DD45BF4041CDE064EAF6E07C2B6B89192D65362084B355; AWSELBCORS=A5EDC1071EB54DEE085FA9BC53DB5910EF75B9C87F1017073E8B0D71F097020F81072E969926CF7FF56E9A38BD28DD45BF4041CDE064EAF6E07C2B6B89192D65362084B355; BrowserSessionId=5fbf4be65c6f1; RGPPortalSessionID=9crc499vdovmkbi7pk1dbpald7; RGPSessionGUID=3b7bcabfdc8ca0eba91fe3f724248402e5e1ca396e4652b7756912a7de7cbde18c6cf2d2d0288f2e67999a7b5589145a'
    }
    payload = 'PreventChromeAutocomplete=&random=5fbf4be6613c7&iframeid=&mode=p&fctrl_1=offering_guid&offering_guid=2923df3b2bfd4c3bb16b14795c569270&fctrl_2=course_guid&course_guid=&fctrl_3=limited_to_course_guid_for_offering_guid_2923df3b2bfd4c3bb16b14795c569270&limited_to_course_guid_for_offering_guid_2923df3b2bfd4c3bb16b14795c569270=&fctrl_4=show_date&show_date=' + date + '&ftagname_0_pcount-pid-1-316074=pcount&ftagval_0_pcount-pid-1-316074=1&ftagname_1_pcount-pid-1-316074=pid&ftagval_1_pcount-pid-1-316074=316074&fctrl_5=pcount-pid-1-316074&pcount-pid-1-316074=0&ftagname_0_pcount-pid-1-6420306=pcount&ftagval_0_pcount-pid-1-6420306=1&ftagname_1_pcount-pid-1-6420306=pid&ftagval_1_pcount-pid-1-6420306=6420306&fctrl_6=pcount-pid-1-6420306&pcount-pid-1-6420306=0&ftagname_0_pcount-pid-1-6304903=pcount&ftagval_0_pcount-pid-1-6304903=1&ftagname_1_pcount-pid-1-6304903=pid&ftagval_1_pcount-pid-1-6304903=6304903&fctrl_7=pcount-pid-1-6304903&pcount-pid-1-6304903=0&ftagname_0_pcount-pid-1-6304904=pcount&ftagval_0_pcount-pid-1-6304904=1&ftagname_1_pcount-pid-1-6304904=pid&ftagval_1_pcount-pid-1-6304904=6304904&fctrl_8=pcount-pid-1-6304904&pcount-pid-1-6304904=0&ftagname_0_pcount-pid-1-6570973=pcount&ftagval_0_pcount-pid-1-6570973=1&ftagname_1_pcount-pid-1-6570973=pid&ftagval_1_pcount-pid-1-6570973=6570973&fctrl_9=pcount-pid-1-6570973&pcount-pid-1-6570973=0&ftagname_0_pcount-pid-1-6570974=pcount&ftagval_0_pcount-pid-1-6570974=1&ftagname_1_pcount-pid-1-6570974=pid&ftagval_1_pcount-pid-1-6570974=6570974&fctrl_10=pcount-pid-1-6570974&pcount-pid-1-6570974=0'
    r = requests.post(url, data=payload, headers=headers)
    html_data = json.loads(r.content.decode('utf-8'))
    return html_data["event_list_html"]


def parse_data(html_string, input_date):
    tds = []
    soup = BeautifulSoup(html_string, 'html.parser')
    table = soup.findAll('td')
    # print(table)
    for item in table:
        if " PM" in item.text or " AM" in item.text:
            tds.append(input_date + "," + item.text.replace("\n", ""))
        if "space" in item.text or "Full" in item.text:
            if "space" in item.text:
                tds.append((item.text.replace('Availability', '')).replace("\n", ""))
            if "Full" in item.text:
                tds.append("0 spaces")

    output = convert(tds)
    return output


def sendEmail(date, email_address):
    # Function to send emails

    # Gmail credentials. You will have to enable " Access for less secure apps" in the account settings if you
    # want to email this way
    gmail_user = '[gmail address]'
    gmail_password = '[gmail password]'

    sent_from = gmail_user
    to = email_address
    subject = "Alert for ETCC reservation slot: " + date
    body = 'There is an openning for the reservation slot: ' + date + '. Please go register soon! \n ' \
            'https://app.rockgympro.com/b/widget/?a=offering&offering_guid=2923df3b2bfd4c3bb16b14795c569270&' \
                                                                      'random=5fc5ed5620d38&iframeid=&mode=p'

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = gmail_user
    message["To"] = email_address

    # convert both parts to MIMEText objects and add them to the MIMEMultipart message
    part1 = MIMEText(body, "plain")
    message.attach(part1)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, message.as_string())
        server.close()
        now1 = datetime.now()
        dt_string1 = now1.strftime("%m/%d/%Y %H:%M:%S")
        logging.info(dt_string1 + ': Email sent to: ' + email_address.replace('\n', '') + ' for date: ' + date)
    except Exception as e:
        # catch any exceptions and log to logger
        now2 = datetime.now()
        dt_string2 = now2.strftime("%m/%d/%Y %H:%M:%S")
        logging.error(dt_string2 + ': There was a problem sending email to: ' + email_address + ' for date: ' + date)


def convert(a):
    # Python3 program to Convert a list to dictionary
    # https://www.geeksforgeeks.org/python-convert-a-list-to-dictionary/

    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


if __name__ == "__main__":
    # Main function where we loop every ~60 seconds to check if a slot has opened up

    # This is a basic logger to log activity from this script to a file
    logging.basicConfig(filename='watcher.log', level=logging.INFO)

    while True:
        write_if_empty_found = False
        # generate random number between 45 and 60 and sleep for that time to look more human
        time.sleep(random.randint(3, 4))
        try:
            f = open("waitlist.txt", "r+")
            my_file_data = [line for line in f.readlines()]
            f.close()
        except:
            now3 = datetime.now()
            dt_string3 = now3.strftime("%m/%d/%Y %H:%M:%S")
            logging.warning(dt_string3 + ': No waitlist file exists. Sleeping...')
            continue

        datestoquery = []

        if not my_file_data:
            now4 = datetime.now()
            dt_string4 = now4.strftime("%m/%d/%Y %H:%M:%S")
            logging.info(dt_string4 + ': File is empty, waiting for data')
            continue
        else:
            now5 = datetime.now()
            dt_string5 = now5.strftime("%m/%d/%Y %H:%M:%S")
            logging.info(dt_string5 + ': File has data. Making queries.')
            for item in my_file_data:
                datestoquery.append(item)

        for item in datestoquery:
            item = item.replace("\n", "")
            if item == "":
                write_if_empty_found = True
                continue
            # check if the current time is past the time in the file if so, delete it (it is past the reservation time)
            # datetime object containing current date and time
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            date_time_obj = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')

            linedate = item.split(",", 1)[0]
            linedatearray = linedate.split("-")
            linetime = item.split(",", 4)[3]
            linetime_hours = linetime.split(" ", 3)

            if linetime_hours[2] == "PM":
                hour = int(linetime_hours[1].split(":")[0]) + 12
            else:
                hour = int(linetime_hours[1].split(":")[0])

            minute = int(linetime_hours[1].split(":")[1])
            d1 = datetime(int(linedatearray[0]), int(linedatearray[1]), int(linedatearray[2]), hour,
                          minute, 00)
            if date_time_obj > d1:
                datestoquery.remove(item)
                print("Deleted: " + item)
                now6 = datetime.now()
                dt_string6 = now6.strftime("%m/%d/%Y %H:%M:%S")
                logging.info(dt_string6 + ': Deleted item because it is past reservation time: ' + item)
                f = open("waitlist.txt", "w")
                for row in datestoquery:
                    f.write("%s\n" % row)
                f.close()

            if datestoquery:
                for item in datestoquery:
                    if item != "" and item != "\n":
                        html_data = get_data(item.split(',', 1)[0])
                        date_table = parse_data(html_data, item.split(',', 1)[0])
                        item_array = item.split(',')
                        date = item_array[0]
                        human_date = item_array[1] + "," + item_array[2] + "," + item_array[3]
                        email = item_array[4]

                        for k, v in date_table.items():
                            k_array = k.split(',')
                            k_date = k_array[1] + "," + k_array[2] + "," + k_array[3]
                            if k_date == human_date:
                                # check if spaces are more than 0
                                if v != "0 spaces":
                                    # call send email function and remove that line from our file
                                    sendEmail(human_date, email)
                                    datestoquery.remove(item)
                                    f = open("waitlist.txt", "w")
                                    for item2 in datestoquery:
                                        f.write("%s\n" % item2)
                                    f.close()
            else:
                print("array is empty!")

        # check our file for empty lines and delete them
        if write_if_empty_found:
            f = open("waitlist.txt", "w")
            for item2 in datestoquery:
                item2 = item2.replace('\n', '').replace('\r', '')
                if item2 != "":
                    f.write("%s\n" % item2)
            f.close()

