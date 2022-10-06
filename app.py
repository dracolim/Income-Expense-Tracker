import calendar
from datetime import datetime
import streamlit as st #pip install streamlit
from streamlit_option_menu import option_menu #pip install streamlit-option-menu
import plotly.graph_objects as go #pip install plotly
import database as db #local import

# Settings 
incomes = ['Salary' , 'Blog' , 'Other Income']
expenses = ['Rent' , 'Utilities' , 'Groceries' , 'Car' , 'Other Exepenses' , 'Saving']
currency = "USD"
page_title = "Income and Expense Tracker"
page_icon = ":money_with_wings:" #emojis from https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered" #wide

#page configuration
st.set_page_config(page_title = page_title , page_icon = page_icon, layout = layout)
st.title(page_title + " " + page_icon)

# drop down values for period 
years = [datetime.today().year , datetime.today().year + 1]
months = list(calendar.month_name[1:])

# -- Interacting with database 
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods


# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---- Navigation NAVBAR
#variable: selected
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

#--- input and save periods 
if selected == "Data Entry":
    st.header(f'Data Entry in {currency}')
    #create form
    #clear_on_submit: after submitting, clear the form
    with st.form("entry_form" , clear_on_submit = True):
        col1 , col2 = st.columns(2)
        #create a selectbox to allow user to select month
        #with key argument 
        col1.selectbox("Select Month:" , months , key="month")
        #create a selectbox to allow user to select year
        col1.selectbox("Select Year:" , years , key="year")

        "---" #this is a divider line
        #exapnder: DROPDOWN
        with st.expander("Income"):
            for income in incomes:
                #key: must be a unique value
                #step: increase by how much
                st.number_input(f"{income}:" , min_value = 0, format = "%i" , step=10, key=income)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:" , min_value = 0, format = "%i" , step=10, key=expense)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder = 'Enter a comment here...')

        "---"
        submitted = st.form_submit_button('Save Data')
        if submitted:
            #sent to database
            #get values from each input view 
            #format: 2022_march
            #LIKE A DICTIONARY
            period = str(st.session_state["year"]) + '_' + str(st.session_state["month"])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            db.insert_period(period , incomes, expenses , comment)
            st.success("Data Saved") #bootstraop green success message 

#---- plot GRAPH
if selected == 'Data Visualization':
    st.header("Data Visualisation")
    with st.form("saved_periods"):
        # Get periods from database 
        period = st.selectbox("Select Period:" , get_all_periods())
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            #get data from database
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            expenses = period_data.get("expenses")
            incomes = period_data.get("incomes")

            #create metrics
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {currency}")
            col2.metric("Total Expense", f"{total_expense} {currency}")
            col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
            st.text(f"Comment: {comment}")

            # Create sankey chart
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())

            # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color="#E694FF")
            data = go.Sankey(link=link, node=node)

            # Plot it!
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)
