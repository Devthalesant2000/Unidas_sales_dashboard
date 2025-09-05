import pandas as pd
import streamlit as st
import requests 
from Functions.treating_datas import *
from Functions.get_reports_api import *
from datetime import timedelta, datetime
import numpy as np
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Dashboard UNIDAS MEDICAL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
