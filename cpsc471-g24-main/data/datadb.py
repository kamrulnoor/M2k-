import duckdb as ddb

con = ddb.connect("m2kdashboard.db")
con.read_csv("data/*.csv")
con.sql("CREATE OR REPLACE TABLE Users AS SELECT * FROM 'data/USERS.csv';")
con.sql("CREATE OR REPLACE TABLE MarketingInstances AS SELECT * FROM 'data/INSTANCES.csv';")
con.sql("CREATE OR REPLACE TABLE Marketing AS SELECT * FROM 'data/MARKETING.csv';")
con.sql("CREATE OR REPLACE TABLE Techniques AS SELECT * FROM 'data/TECHNIQUES.csv';")
con.sql("CREATE OR REPLACE TABLE Foods AS SELECT * FROM 'data/FOODS.csv';")
con.sql("CREATE OR REPLACE TABLE Healthy AS SELECT * FROM 'data/HEALTHY.csv';")
