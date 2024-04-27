import duckdb
import numpy
db = duckdb.connect('m2kdashboard.db')
print(db.sql("SHOW ALL TABLES"))
print(db.sql("SHOW Marketing"))