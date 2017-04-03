# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 22:22:16 2017

@author: Kozmik
"""

from datetime import datetime

MONTHS_NUM_TO_ABR = {"01":"Jan", "02":"Feb", "03":"Mar", "04":"Apr", 
"05":"May", "06":"Jun", "07":"Jul", "08":"Aug", 
"09":"Sep", "10":"Oct", "11":"Nov", "12":"Dec"}

MONTHS_ABR_TO_NUM = {'Dec': '12', 'Oct': '10', 'Feb': '02', 'Nov': '11', 
'Apr': '04', 'Jun': '06', 'Sep': '09', 'Jul': '07', 
'Jan': '01', 'May': '05', 'Aug': '08', 'Mar': '03'}


def getCurrentDate():
    """Returns a datetime object"""
    return datetime.today()
        
def getDateGUIFormat(date):
    """Takes a datetime object and returns a string in the format Month Day, Year, H:M:S"""
    return datetime.strftime(date, '%B %d, %Y %H:%M:%S')