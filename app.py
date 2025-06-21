import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title = "Budget Tracker", layout = 'centered')

st.title("Budget Tracker")
st.write("Welcome! Let's help you track your budget.")

income = st.number_input("Enter your total income in the past two weeks:", min_value = 0.0, step = 50.0)

if "expenses" not in st.session_state:
    st.session_state.expenses = []

if income <=0:
    st.warning("Please enter a positive number for your income.")  
else:
    st.success(f"Your 14-day income is: ${income:,.2f}")

    start_date = datetime.today()
    end_date = start_date + timedelta(days = 13)

    st.write(f"Budget Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    with st.form("expense_form", clear_on_submit = True):
        expense_date = st.date_input("Expense date", min_value = start_date.date(), max_value = end_date.date(), value = start_date.date())
        category = st.selectbox("Category", ['Food', 'Rent', 'Transportation', 'Entertainment', 'Other'])
        description = st.text_input("Description (optional)")
        amount = st.number_input("Amount", min_value = 0.0, step = 1.0)

        submitted = st.form_submit_button("Add Expense")

    if submitted:
        if amount <= 0:
            st.error("Please enter a positive amount.")
        else:
            st.session_state.expenses.append({"Date": expense_date.strftime("%Y-%m-%d"), "Category": category, "Description": description, "Amount": amount})
            st.success("Expense added!")
        
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        st.subheader("Expenses so far:")
        st.dataframe(df)

        total_spent = df['Amount'].sum()
        remaining = income - total_spent

        st.write(f"**Total spent:** ${total_spent:,.2f}")
        st.write(f"**Remaining Budget:** ${remaining:,.2f}")

        if remaining < 0:
            st.error("You are over budget!")

        delete_index = st.selectbox("Select an expense to delete (by row number):", options = range(len(df)), format_func = lambda x: f"{x}: {df.iloc[x]['Date']} - {df.iloc[x]['Category']} - {df.iloc[x]['Amount']:,.2f} ")
        
        if st.button("Deleted selected expense"):
            st.session_state.expenses.pop(delete_index)
            st.success("Expense deleted!")
            st.rerun()

        if not df.empty:
            category_totals = df.groupby('Category')['Amount'].sum()
            st.subheader("Spending by Category")

            fig, ax = plt.subplots()
            ax.pie(category_totals, labels = category_totals.index, autopct = '%1.1f%%', startangle = 90)
            ax.axis('equal')
            st.pyplot(fig)

            top_category = category_totals.idxmax()
            st.write(f"You'll be spending the most on **{top_category}** during this period.")

            st.download_button(label = "Download as CSV", data = df.to_csv(index = False), file_name = "my_budget.csv", mime = "text/csv")
            
        if st.button("Reset Budget"):
            st.session_state.expenses = []
            st.success("All expenses are cleared! You can start fresh.")