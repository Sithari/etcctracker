#!/usr/bin/env python3
# This code queries Earth Trek gym's reservation system to see if time slots are open and to sign up for
# on a waitlist to be alerted via email when a full slot opens.

# Written by Rakesh Passa
# 11-30-2020


import requests
import json
from bs4 import BeautifulSoup
import re
from flask import Flask, request, render_template, redirect

# create the flask app
app = Flask(__name__)

# create global variables to be shared between functions
user_date_choice = ""
user_time_choice = ""


# default html page to serve
@app.route("/")
def index():
    return render_template('index.html')


# page to serve when user enters a date
@app.route("/getschedule", methods=['POST'])
def getschedule():
    # get input from html form into python variable
    input_date = request.form['date']
    # check if input matches a format we accept (2020-11-30) using regex
    if not (re.match("^(2020|2021)-(0[1-9]|1[1-2])-[0-3][0-9]$", input_date)):
        return error()
    else:
        # set global variable of the users input for use later
        global user_date_choice
        user_date_choice = input_date
        # query the app server for the data
        html_data = get_data(input_date)
        # parse the html data returned
        date_table = parse_data(html_data, input_date)
        return selecttime(date_table)


# page to return with the gyms time slots
@app.route("/selecttime", methods=['POST'])
def selecttime(data):
    # new dict is a dictionary that holds the time slot options
    newdict = {}
    for k, v in data.items():
        newdict[k.split(',', 1)[1]] = v

    return render_template('selecttime.html', mydata=newdict)


# page to ask for user to enter an email
@app.route("/email", methods=['POST'])
def emailsetup():
    # save users email into a variable
    user_email = request.form['email']
    # do some sanity check to see if they entered a valid email
    if len(user_email) < 4:
        return error()
    if "@" not in user_email:
        return error()
    # we now have all the data to write to a text file what the user chose to monitor
    f = open("waitlist.txt", "a")
    f.write(user_date_choice + "," + user_time_choice + "," + user_email + "\n")
    f.close()
    return render_template('thanks.html', email=user_email)


# page to ask user to select the time slot to monitor
@app.route("/signup", methods=['POST'])
def selectedtime():
    try:
        time = request.form['time']
    except:
        return error()
    global user_time_choice
    user_time_choice = time
    return render_template('registeremail.html', time=time)


# page to allow users to unsubscribe from the montioring system (if registered)
@app.route("/unsub", methods=['POST'])
def unsub():
    email = request.form['unsub']
    if len(email) < 4:
        return error()
    if "@" not in email:
        return error()
    f = open("waitlist.txt", "r+")
    my_file_data = [line for line in f.readlines()]
    f.close()
    confirmation_string = ""

    # if the file is empty respond with no email found
    if not my_file_data:
        confirmation_string = "We did not find your email in the watchlist! Sorry!"
    for line in my_file_data:
        print("checking the line: " + line)
        if email in line:
            # if the email is registered then delete it from the array
            my_file_data.remove(line)
            f = open("waitlist.txt", "w")
            for line2 in my_file_data:
                f.write(line2)
            f.close()
            confirmation_string = "Your email has been removed from the watchlist!"
        else:
            # if the email is not registered then return an error message
            confirmation_string = "We did not find your email in the watchlist! Sorry!"
    return render_template('unsubconfirmation.html', confirmation=confirmation_string)


# generic error page to return if we do not understand any user inputs
@app.route("/error", methods=['GET'])
def error():
    return render_template('error.html')


def convert(a):
    # Python3 program to Convert a list to dictionary
    # https://www.geeksforgeeks.org/python-convert-a-list-to-dictionary/

    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


def get_data(date):
    # Function to query the app url to get html data about the space availability

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
    # Function to read the html data from the server and pull out date and space details using beautiful soup library
    tds = []
    soup = BeautifulSoup(html_string, 'html.parser')
    # find all the table data tags and store them in "table"
    table = soup.findAll('td')
    for item in table:
        # check if table data item has pm or am in it, if so then it is the time slot string
        if " PM" in item.text or " AM" in item.text:
            tds.append(input_date + "," + item.text.replace("\n", ""))
        # check if the table data has the word "space" or "full" in it. If so then it is the spaces open field
        if "space" in item.text or "Full" in item.text:
            if "space" in item.text:
                tds.append((item.text.replace('Availability', '')).replace("\n", ""))
            if "Full" in item.text:
                tds.append("0 spaces")

    # test data!
    # testdata = '{"2020-11-30,Mon, November 30, 4 PM to  6:15 PM": "0 spaces", "2020-11-30,Mon, November 30, 6:30 PM to  8:30 PM": "32 spaces"}'
    # output = json.loads(testdata)

    output = convert(tds)
    return output


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug='False', port=80)
