# -*- coding: utf-8 -*-
"""
Created on Tue May 20 12:15:38 2025

@author: Ameli
"""

import streamlit as st
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import root
import LBO_Calculated as lbo

st.set_page_config(
    page_title="LBO Financial Modelling Tool",
    page_icon="🦈",
    layout="wide")

st.title("LBO Financial Modelling")
st.sidebar.title("CashFlow Parameters")

time=st.sidebar.slider('Exit time(in years from now)',
                        value=10,min_value=1,max_value=15,step=1)

current_sales = st.sidebar.number_input('Enter the current sales in $M',100)

sales_growth_rate =st.sidebar.slider('Sales  Growth(in %)',
                        value=5.0,min_value=0.0,max_value=30.0,step=0.5)

sales_growth_rate= sales_growth_rate/100

operating_margin = st.sidebar.slider('Operating Margin (in %)',
                        value=15.0,min_value=0.0,max_value=50.0,step=0.5)

operating_margin= operating_margin/100

depreciation_rate = st.sidebar.slider('Depreciation Rate in % of Sales (in %)',
                        value=5.0,min_value=0.0,max_value=10.0,step=0.5)

depreciation_rate = depreciation_rate /100

capex = st.sidebar.slider('Capex in % of Sales (in %)',
                        value=5.0,min_value=0.0,max_value=10.0,step=0.5)
capex = capex/100

working_capital = st.sidebar.slider('Working Capital (in %)',
                        value=20.0,min_value=0.0,max_value=50.0,step=0.5)

working_capital = working_capital /100

tax_rate = st.sidebar.slider(label='Enter the effective tax rate (in %)',
                        value=35.0,min_value=0.0,max_value=100.0,step=0.5)
tax_rate = tax_rate/100

interest_rate = st.sidebar.slider(label='Enter the interest rate (in %)',
                        value=7.5,min_value=0.0,max_value=20.0,step=0.5)

interest_rate = interest_rate/100

st.header("*Cash Flow Projections*")
table_cf= lbo.generate_cash_flow_table(time=time,
                             curr_sales=current_sales,
                             sales_rate=sales_growth_rate,
                             ebit_sales_rate=operating_margin,
                             tax_rate=tax_rate,
                             depreciation_rate=depreciation_rate,
                             capex_rate=capex,
                             wcr_rate=working_capital
                             )
numeric_cols= table_cf.select_dtypes(include=np.number).columns
table_cf[numeric_cols]=table_cf[numeric_cols].round(decimals=2)
st.dataframe(table_cf)

fcf_array = np.array(table_cf.loc['Free Cash Flows', :])
ebitda_array = np.array(table_cf.loc['EBITDA', :])
#-------------- Debt Optimization ----------------------------------------------------------
st.header("*Debt Modelling*")
st.markdown("Specify Company Value")
deal_value = st.number_input(label='Enter the deal value(in $M)',
                             min_value=0.0,
                             max_value=1500.0,
                             value=None,
                             step=10.0            
                             )

st.markdown("Indicate Current Company's EBIT")
curret_debt = st.number_input(label='Enter Current EBIT (in $M)',
                             min_value=0.0,
                             max_value=1500.0,
                             value=None,
                             step=10.0            
                             )

st.markdown("Select convenants of interest:")

#---------------Prepare Constrains-----------------

initial_guess = np.array([10]*time)
vector_ones=np.ones(time)

list_constraints = list()

list_constraints.append({'type': 'ineq','fun': lbo.positivity_constraint})

convenant_dscr =st.checkbox('Debt Service Coverage Ratio conveant (DSCR)')

if convenant_dscr:
   dscr_cons_value=st.number_input(label='Enter the minmum DSCR Ratio',
                              min_value=0.0,
                              max_value=5.0,
                              value= 1.25,
                              step= 0.01                                    
                                   )
   list_constraints.append({ 'type':'ineq',
                              'fun': lbo.dscr_constraint,
                              'args': [vector_ones,
                                       np.array(table_cf.loc['Free Cash Flows', :]),
                                       interest_rate,
                                       tax_rate,
                                       dscr_cons_value]})
    
interest_coverage_ratio = st.checkbox('Interest Coverage Ratio(EBITDA/Cash Interest)')

if interest_coverage_ratio:
    cov_ratio_value =st.number_input(label='Enter the minmum DSCR Ratio',
                               min_value=0.0,
                               max_value=10.0,
                               value= 4.5,
                               step= 0.01                                   
                                    )
    list_constraints.append({ 'type':'ineq',
                             'fun':  lbo.interest_coverage_constraint,
                             'args': [vector_ones,
                                      np.array(table_cf.loc['EBITDA', :]),
                                      interest_rate,
                                      interest_coverage_ratio]})

max_debt = st.checkbox('Maximum Debt Covenant')

if max_debt:
    max_debt_value = st.number_input(label='Enter the max debt allowed',
                               min_value=0.0,
                               max_value=15000.0,
                               value= deal_value,
                               step= 50.0                                   
                                    )
    list_constraints.append({ 'type':'ineq',
                            'fun':  lbo.max_debt_constraint,
                            'args': [max_debt_value]
                            })    
list_constraints =tuple(list_constraints)
run_option =st.button('Run optimization')

if run_option:
    
    result =minimize(fun=lbo.obj,
                     args=[vector_ones],
                     x0=initial_guess,
                     constraints=list_constraints
                     )
        
    st.write(f'Optimization message result:{result.message}')
    debt_table_recap = lbo.debt_table(fcf_table=np.array(table_cf.loc['Free Cash Flows',:]),
                                      ebitda_table =np.array(table_cf.loc['EBITDA',:]),
                                      repayment_vector=np.array(result.x),
                                      interest_rate=interest_rate,
                                      tax_rate=tax_rate
                                    )
    numeric_cols = debt_table_recap.select_dtypes(include=np.number).columns
    debt_table_recap[numeric_cols]=debt_table_recap[numeric_cols].round(decimals=2)
    
    st.dataframe(debt_table_recap)















