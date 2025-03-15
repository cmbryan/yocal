#!/bin/env sh

python -m pip install -r requirements.txt
rm -f *.db

python ./1_fixed_tables_create_populate.py
python ./2_year_tables_create.py 2020 2035
python ./3_insert_ID_date.py
python ./4_paschalion_cycle.py
python ./5_menaion_cycle.py
python ./6_fast_codes.py
python ./7_tone_eoth.py
python ./8_master_main_create.py
python ./9_master_lection_create.py
python ./10_master_main_tbl_pop.py 2020 2035
python ./11_master_lection_pop.py Y
python ./12_master_lection_correct.py