
import os
import json
import pandas as pd
from datetime import datetime
from itertools import chain
from pprint import pprint
from decimal import *
# from shroomdk import ShroomDK

from flipside import Flipside




SHROOM_SDK_API = os.environ['FLIPSIDE_API_KEY']

flipside = Flipside(SHROOM_SDK_API)

def querying_pagination(query_string, API_KEY=SHROOM_SDK_API):
    """
    This function queries the Flipside database using the Shroom SDK and returns a pandas dataframe

    :param query_string: SQL query string
    :param API_KEY: API key for Shroom SDK
    :return: pandas dataframe

    """

    print("query_string", query_string)
    sdk = ShroomDK(API_KEY)

    # Query results page by page and saves the results in a list
    # If nothing is returned then just stop the loop and start adding the data to the dataframe
    result_list = []
    for i in range(1,11): # max is a million rows @ 100k per page
        data=sdk.query(query_string,page_size=100000,page_number=i)
        if data.run_stats.record_count == 0:
            break
        else:
            result_list.append(data.records)

    # Loops through the returned results and adds into a pandas dataframe
    result_df=pd.DataFrame()
    for idx, each_list in enumerate(result_list):
        if idx == 0:
            result_df=pd.json_normalize(each_list)
        else:
            result_df=pd.concat([result_df, pd.json_normalize(each_list)])

    return result_df


def get_widget_names():

    sql_statement = """
    SELECT WIDGET_NAME, COUNT(*) as COUNT
    FROM near.social.fact_widget_deployments
    GROUP BY WIDGET_NAME;
    """
    snowflake_data = flipside.query(sql_statement)
    return snowflake_data.records

def get_all_widget():
    """
    This function queries transactions received by address and returns the top n addresses

    :param top_n: number of top addresses to return
    :param time_period: time period to query
    :return: pandas dataframe

    """

    sql_statement =f"""
    select * from
    near.social.fact_widget_deployments
    where WIDGET_NAME = 'app__frame'
    """

    snowflake_data = flipside.query(sql_statement)
    return snowflake_data.records


def get_dev_info(dev_name):


    sql_statement = f"""

    select * from
    near.social.fact_profile_changes
    where signer_id = '{dev_name}'
    and profile_section = 'linktree'
    order by BLOCK_TIMESTAMP asc
    limit 1
    """

    snowflake_data = flipside.query(sql_statement)
    return snowflake_data.records


def get_list_of_all_devs():

    sql_statement = f"""
    SELECT signer_id, COUNT(*) as COUNT
    FROM near.social.fact_widget_deployments
    GROUP BY signer_id;

    """

    snowflake_data = flipside.query(sql_statement)
    snowflake_data = snowflake_data.records
    signer_ids = [row['signer_id'] for row in snowflake_data]

    data = set(signer_ids)
    return data


def get_widget_updates(widget_name, signer_id, timestamp=None):

    widget_name = widget_name.replace("'", "\\'")

    if timestamp:
        sql_statement = f"""
        SELECT *
        FROM near.social.fact_widget_deployments
        WHERE WIDGET_NAME = '{widget_name}'
        AND BLOCK_TIMESTAMP > '{timestamp}';
        """
    else:

        sql_statement =f"""
        select * from
        near.social.fact_widget_deployments
        where WIDGET_NAME = '{widget_name}'
        and SIGNER_ID = '{signer_id}'
        """