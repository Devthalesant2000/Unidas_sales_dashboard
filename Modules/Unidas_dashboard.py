import pandas as pd
import streamlit as st
import requests 
from Functions.treating_datas import treating_data
from Functions.get_reports_api import *

df = main()

st.dataframe(df)