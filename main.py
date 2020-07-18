import cv2
import numpy as np
from mss import mss
from PIL import Image
import time
import pytesseract
import sqlite3
from sqlite3 import Error

#sets 64 bit windows 10 path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TABLE_NAME = "zoomdata"

#sql 

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_table(conn, table_name):
    create_table_sql = """ CREATE TABLE IF NOT EXISTS """ + table_name + """ (
                                    time integer PRIMARY KEY,
                                    count integer NOT NULL
                                ); """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_record(conn, info, table_name):
    sql = ''' INSERT OR IGNORE INTO ''' + table_name+'''(time, count)
              VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(sql, info)
    return cur.lastrowid

def select_all(conn, table_name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table_name)
    rows = cur.fetchall()
    return rows

def get_table_name():
    return TABLE_NAME
    
if __name__ == '__main__':
    conn = create_connection("sqlite.db")
    if conn:
        create_table(conn, TABLE_NAME)
    mon = {'top': 1000, 'left': 1000, 'width': 30, 'height': 30}
    sct = mss()
    curtime = 0
    while 1:
        #Due to resolution and scaling, YMMV (a lot)
        sct_img = sct.grab(mon)
        img = cv2.resize(np.array(sct_img), dsize=(120, 120), interpolation=cv2.INTER_LINEAR)
        ret, thresh = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY) 
        kernel = np.ones((2,2),np.uint8)
        img = cv2.erode(thresh,kernel,iterations = 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        cv2.namedWindow('input', cv2.WINDOW_NORMAL)
        cv2.imshow('input', inverted)
        num_members = pytesseract.image_to_string(inverted, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
        print(num_members)
        if(num_members == ''):
            num_members = 0
        create_record(conn, (curtime, num_members), TABLE_NAME)
        curtime += 1
        print("------")
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    if conn:
        conn.commit()
        conn.close()