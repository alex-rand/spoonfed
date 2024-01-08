# Load the necessary libraries
library(DBI)
library(RSQLite)
library(dbplyr)
library(tibble)

# Connect to the SQLite file
con <- dbConnect(RSQLite::SQLite(), "database.db")

# Write your SQL query
query <- "SELECT * FROM gpt_responses;"
query <- "SELECT * FROM runs;"
query <- "SELECT * FROM users;"
query <- "SELECT * FROM language_configurations;"

# Use dbGetQuery to execute the query and store the result in a data frame
dbListTables(con)
df <- dbGetQuery(con, query)
df |> view()
# Convert the data frame to a tibble
tibble_df <- as_tibble(df)

### Delete a table if you want...
#delete_query <- "DROP TABLE IF EXISTS language_configurations;"
#dbExecute(con, delete_query)

# Close the connection
dbDisconnect(con)

# Don't forget to close the connection when you're done
dbDisconnect(con)

# Print the tibble
tibble_df %>% view()