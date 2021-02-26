import numpy as np
import pandas as pd
import json
import datetime
from ps_wd import pswd

import sqlalchemy
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from flask import Flask, render_template

# pswd = 'postgres'

engine = create_engine('postgresql://postgres:' +
                       pswd + '@localhost:5432/sfbusiness_db')
connection = engine.connect()

# Flask Setup
app = Flask(__name__)

# Flask Routes


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/charts')
def charts():
    return render_template('charts.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/data')
def data():
    return render_template('data.html')


@app.route('/map')
def map():
    return render_template('map.html')


# ***************************************************************
# ***************************************************************
@app.route("/original_data")
def original_sf():

    # Establish connection with the database
    engine = create_engine('postgresql://postgres:' +
                           pswd + '@localhost:5432/original_db')
    connection = engine.connect()

    original_results = pd.read_sql(
        'SELECT * FROM original_table limit 10', connection)

    return jsonify((original_results).to_dict("record"))

# *****************************************************************************************
# *****************************************************************************************


@app.route("/get_data")
def data_sf():
    print('Working')
    # Establish connection with the database
    engine = create_engine('postgresql://postgres:' +
                           pswd + '@localhost:5432/sfbusiness_db')
    connection = engine.connect()

    results = pd.read_sql('SELECT * FROM sf_business limit 100', connection)

    return jsonify((results).to_dict("record"))

# *********************************************************************************************
# *****************************************************************************************


@app.route("/busi_bar")
def busi_bar_t():
    # Establish connection with the database
    # engine = create_engine('postgresql://postgres:' +
    #                        pswd + '@localhost:5432/sfbusiness_db')
    # connection = engine.connect()

    results1 = pd.read_sql('SELECT * FROM sf_business', connection)

    # Business type by location end date
    business_end = results1.groupby(['busi_type'])['loc_end_dt'].apply(pd.Series.value_counts)
    loc_end_frame=business_end.to_frame().reset_index().rename(columns={"level_1":"location_end_date","loc_end_dt":"loc_end_count"})

    #Split year from date
    fix01 = list(loc_end_frame["location_end_date"])
    fix02 = [x.split("/") for x in fix01]
    loc_end_busi = [x[2] for x in fix02]
    loc_end_busitype = pd.DataFrame(loc_end_busi)

    year_loc_busitype = pd.concat([loc_end_frame, loc_end_busitype], axis=1)
    year_loc_busitype = year_loc_busitype.rename(columns={0:"locBusi_end_year"})

    locBusi_end_final_1 = year_loc_busitype.groupby(['locBusi_end_year'])['busi_type'].apply(pd.Series.value_counts)
    locBusi_end_final = locBusi_end_final_1.to_frame().reset_index().rename(columns={"level_1":"busi_type","busi_type":"locbusi_end_count"})
    locBusi_end_final = locBusi_end_final[ locBusi_end_final['locBusi_end_year'] >'2009' ]

    # # Merge location start and end dates
    # combined_loc_start_end = pd.merge(busitype_final, locBusi_end_final, on='busi_type')


    return jsonify((locBusi_end_final).to_dict("record"))

# ************************************************************************************************************
# *****************************************************************************************


@app.route("/neigh_bar")
def neigh_bar_t():
    # Establish connection with the database
    # engine = create_engine('postgresql://postgres:' +
    #                        pswd + '@localhost:5432/sfbusiness_db')
    # connection = engine.connect()

    results2 = pd.read_sql('SELECT * FROM sf_business', connection)

    # Groupby neighborhood
    neighborhood_group = results2.groupby(['neighborhood'])[
        'loc_start_dt'].apply(pd.Series.value_counts)
    neighborhood_frame = neighborhood_group.to_frame().reset_index().rename(
        columns={"level_1": "loc_start_dt", "loc_start_dt": "busi_count"})

    # Split year from date
    fix_n = list(neighborhood_frame["loc_start_dt"])
    fix_n2 = [x.split("/") for x in fix_n]
    busi_start_year_neighborhood = [x[2] for x in fix_n2]
    newcol_n = pd.DataFrame(busi_start_year_neighborhood)

    # Concat split year df
    year_n_df = pd.concat([neighborhood_frame, newcol_n], axis=1)
    year_n_df = year_n_df.rename(columns={0: "busi_start_year"})

    # Group by neighborhood
    neighborhood_final1 = year_n_df.groupby(['busi_start_year'])[
        'neighborhood'].apply(pd.Series.value_counts)
    neighborhood_final = neighborhood_final1.to_frame().reset_index().rename(
        columns={"level_1": "neighborhood", "neighborhood": "busi_count"})
    neighborhood_final = neighborhood_final[neighborhood_final['busi_start_year'] > '2009']

    # return jsonify((neighborhood_final).to_dict("record"))

    return jsonify((neighborhood_final).to_dict("record"))

# *****************************************************************************************************
# *****************************************************************************************


@app.route("/combined_data")
def combined_neigh_bt():
    # Establish connection with the database
    engine = create_engine('postgresql://postgres:' +
                           pswd + '@localhost:5432/sfbusiness_db')
    connection = engine.connect()

    results3 = pd.read_sql('SELECT * FROM sf_business', connection)
    combined_n_bt = results3.groupby(['neighborhood'])[
        'busi_type'].apply(pd.Series.value_counts)

    combined_n_bt = combined_n_bt.to_frame().reset_index().rename(
        columns={" ": "business_type", " ": "busi_count"})
    combined_n_bt = combined_n_bt.rename(
        columns={"level_1": "busi_type", "busi_type": "busi_count"})

    return jsonify((combined_n_bt).to_dict("record"))


# *****************************************************************************************
# ************************************************************************************************************
    # #Convert columns to array
    # busistart_year_arr = busitype_final['busi_start_year'].to_list()
    # busiype_arr = busitype_final['busi_type'].to_list()
    # busicount_arr = busitype_final['busi_count'].to_list()

    # busitype_dict = {'busistart_year':busistart_year_arr,
    #                 'busitype': busiype_arr,
    #                 'busicount': busicount_arr }

    # json_data = json.dumps(busitype_dict)
    # return(json_data)

    # return jsonify((results).to_dict("record"))


if __name__ == '__main__':
    app.run(debug=True)
