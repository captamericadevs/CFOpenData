#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
This script merges the two csv files created by the AffiliateCalculator.py with the Affiliate_list.csv. 
Goal is to append columns to the end of each affiliate row. Columns are:
total number of male athletes to participate in the open, top finishing male, their percentile, 
total females, top female, and their percentile (6x columns appended). 
Merged on Affiliate_id. 
"""
import pandas
import logging

def main():
    """
    main entry point into program
    """

    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
    
    affiliate = pandas.read_csv('Data\\Affiliate_list.csv')
    affiliate['Affiliate_id'] = affiliate['Affiliate_id'].astype(str) 
    men = pandas.read_csv('Men_Counts.csv')
    women = pandas.read_csv('Women_Counts.csv')

    affiliate.merge(men.merge(women, how='outer', on='Affiliate_id'), how='outer', on='Affiliate_id').to_csv('Affiliate_Detail.csv', index=False)

if __name__ == '__main__':
    main()