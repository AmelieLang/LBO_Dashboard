# -*- coding: utf-8 -*-
"""
Created on Tue May 20 12:15:27 2025

@author: Ameli
"""

import numpy as np
import pandas as pd

def generate_cash_flow_table(time,
                             curr_sales,
                             sales_rate,
                             ebit_sales_rate,
                             tax_rate,
                             depreciation_rate,
                             capex_rate,
                             wcr_rate):
    
     time_table = np.arange(start=1,
                            stop= time + 1, 
                            step=1
                            )
     sales_table = np.ones(time)* curr_sales*(1+sales_rate)**time_table
     ebit_table = sales_table * ebit_sales_rate
     tax_table = -ebit_table * tax_rate
     net_income_table = ebit_table + tax_table
     depreciation_table = sales_table*depreciation_rate
     capex_table = -sales_table*capex_rate
     
     current_wcr = curr_sales * wcr_rate
     
     wcr_table= sales_table* wcr_rate
     
     wcr_table = np.r_[[current_wcr], wcr_table]

     chg_wcr_table = -np.diff(wcr_table)
     
     free_cf_table = net_income_table+depreciation_table+capex_table + chg_wcr_table
     
     ebitda_table = ebit_table + depreciation_table
     df_projection =pd.DataFrame({'Sales Projection': sales_table,
                                  'EBIT': ebit_table,
                                  'Taxes': tax_table,
                                  'Net Income': net_income_table,
                                  'Depreciation':depreciation_table,
                                  'EBITDA': ebitda_table,
                                  'Capex Projections': capex_table,
                                  'Chg in Working Capital': chg_wcr_table,
                                  'Free Cash Flows':free_cf_table}).T
     
     df_projection.columns = ['Year'+str(i) for i in range(1,time+1)]
     
     return df_projection
 
# Calculate the negative somme of the debts    per columns year cumulate
def obj(x, ones):
    return -np.dot(ones,x)

# per linges 
def debt_remaining_vector(x, ones):
    x_cum = np.cumsum(x)
    return np.dot(x,ones) -x_cum+ x 

def dscr_constraint(x,ones,fcf_vector, interest_rate, tax_rate,value):
    vector_debt = debt_remaining_vector(x,ones)
    interest_vector=vector_debt*interest_rate
    tax_shield_vector=interest_vector*tax_rate
    debt_service_vector=x+interest_vector-tax_shield_vector
    
    return fcf_vector/debt_service_vector-value

def interest_coverage_constraint(x,ones,ebitda_vector,interest_rate,value):
    vector_debt= debt_remaining_vector(x,ones)
    interest_vector=vector_debt*interest_rate
    return ebitda_vector / interest_vector - value

def positivity_constraint(x):
    return x

def max_debt_constraint(x,value):
    return value-np.sum(x)


def debt_table(fcf_table,ebitda_table,repayment_vector,interest_rate,tax_rate):
    
    n_year =repayment_vector.shape[0]
    df=pd.DataFrame()
    
    df['Year'] = np.arange(1,n_year+1)
    df=df.set_index('Year')
    
    df['FCF'] =fcf_table
    df['EBITDA'] = ebitda_table
    df['Debt Repayment'] = repayment_vector
    df['Cumulative Repayment']=np.cumsum(repayment_vector)
    df['Debt SoY']=np.sum(repayment_vector)- df['Cumulative Repayment']+df['Debt Repayment']
    df['Debt EoY']=df['Debt SoY'].shift(-1)
    df.loc[n_year,'Debt EoY'] = 0
    
    df['Interest']=df['Debt SoY']*interest_rate
    df['Tax Shield']=df['Interest']*tax_rate
    df['Debt Servicing']=df['Debt Repayment']+df['Interest']-df['Tax Shield']
    df['Cash']=(df['FCF']-df['Debt Servicing']).cumsum()
    
    df['Interest Coverage'] = df['EBITDA']/df['Interest']
    df['DSCR']=df['FCF']/df['Debt Servicing']
    
    df = df[['FCF','EBITDA','Debt SoY','Debt Repayment','Cumulative Repayment','Interest','Tax Shield','Debt Servicing','Cash','Debt EoY','Interest Coverage','DSCR']]
    return df    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 