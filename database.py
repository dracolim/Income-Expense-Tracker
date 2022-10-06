import os

import streamlit as st  # pip install streamlit
from deta import Deta  # pip install deta
from dotenv import load_dotenv 

#load the env variable
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

#initialize with a project ket 
deta = Deta(DETA_KEY)

#this is how to create/connect to a database
#database name: monthly_reports
db = deta.Base("monthly_reports")

#-- Insert db
def insert_period(period, incomes, expenses, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    #period is out unique identifier ; thus is the key 
    return db.put({"key": period, "incomes": incomes, "expenses": expenses, "comment": comment})

#-- fetch db
def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items

#-- get all value from a particular period to plot data
def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)