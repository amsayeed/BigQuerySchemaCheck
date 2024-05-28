
This Python script validates a BigQuery table's schema against a configuration file. It compares column names, data types, nullability, and modes (REQUIRED, NULLABLE, REPEATED) between the configuration and the actual BigQuery table schema.

## Features

- Validates column names, data types, nullability, and modes
- Supports custom data type mappings
- Provides detailed validation output
- Generates BigQuery DDL statements based on the configuration file
- Validates the configuration file for duplicates and invalid data types

## Requirements

- Python 3.6+
- `google-cloud-bigquery` library
- Google Cloud SDK (for authentication)

## Setup

1. Clone the repository within any directory:

```
git clone https://github.com/amsayeed/BigQuerySchemaCheck
```

2. Prepare a Python virtual environment:

### Windows

1. Open a command prompt or PowerShell.
2. Navigate to the project directory:

```
cd /path/to/your/project
```

3. Create a new virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

This will create a new virtual environment named `venv` in your project directory.

4. Activate the virtual environment:

```
venv\Scripts\activate
```

You should see `(venv)` prepended to your command prompt, indicating that the virtual environment is active.

### Mac

1. Open a terminal.
2. Navigate to the project directory:

```
cd /path/to/your/project
```

3. Create a new virtual environment:
```
python3 -m venv venv
```

This will create a new virtual environment named `venv` in your project directory.

You should see `(venv)` prepended to your terminal prompt, indicating that the virtual environment is active.

4. Activate the virtual environment:

```
source venv/bin/activate
```

Once the virtual environment is active, you can install the required libraries and run the script within the isolated environment.

To deactivate the virtual environment when you're done, simply run:

```
deactivate
```

3. Install the required library:

```
pip install google-cloud-bigquery
```

4. Authenticate with Google Cloud:

- Install the Google Cloud SDK by following the instructions [here](https://cloud.google.com/sdk/docs/install).
- Initialize the SDK:
```
gcloud init
```

Authenticate your account:
```
gcloud auth application-default login
```

This will open a browser window for you to log in with your Google Cloud account.
### Usage

1. **Schema File:** Use the text file (e.g., `schema.txt`) defining your schema:

```
column_name, data_type, constraint1, constraint2, ...
```

Example

```
datetime,datetime,NULLABLE  
store_code,str,REQUIRED  
country_iso2,str,REQUIRED  
total_entries,int,REQUIRED  
passers_by,int,NULLABLE  
entrance,list,REPEATED
```

you can use Silver relational model: Schema documentation to extract information

[Here](https://gymshark.sharepoint.com/:x:/r/sites/PMO/_layouts/15/Doc.aspx?sourcedoc=%7BE0EE949B-8ADF-4426-9A4B-FE17BE257C74%7D&file=Silver%20Relational%20Model%20Schema%20Documentation.xlsx&action=default&mobileredirect=truehttps://gymshark.sharepoint.com/:x:/r/sites/PMO/_layouts/15/Doc.aspx?sourcedoc=%7BE0EE949B-8ADF-4426-9A4B-FE17BE257C74%7D&file=Silver%20Relational%20Model%20Schema%20Documentation.xlsx&action=default&mobileredirect=true)

- `column_name`: The name of the column
- `data_type`: The data type (e.g., `str`, `int`, `datetime`, `list`)
- `constraint1`, `constraint2`, ...: constraints (`REQUIRED`, `NULLABLE`, `REPEATED`,`PK` , `FK`)

2 . **Configuration file:**

```python
project_id = "project-id"  
dataset_id = "dataset-name"  
table_id = "table-name"  
config_file_path = "schema.txt"
```

## Configuration

The `config.py` file contains the following configuration variables:

- `project_id`: Your BigQuery project ID
- `dataset_id`: The BigQuery dataset ID
- `table_id`: The BigQuery table ID
- `config_file_path`: The path to your configuration file

4. **Run:**

```bash
python schema_validator.py

```

### Output

The script prints a report for each column, indicating whether the name, data type, and nullability match the configuration. It also provides placeholders for checking PK/FK constraints (not fully implemented).

```
INFO:root:Column: datetime
INFO:root:  - Name: OK
INFO:root:  - Type: OK
INFO:root:  - Nullable: Expected True, got False
INFO:root:  - Mode: Expected NULLABLE, got REQUIRED
INFO:root:Column: store_code
INFO:root:  - Name: OK
INFO:root:  - Type: OK
INFO:root:  - Nullable: OK
INFO:root:  - Mode: OK
INFO:root:Column: country_iso2
INFO:root:  - Name: OK
INFO:root:  - Type: OK
INFO:root:  - Nullable: OK
INFO:root:  - Mode: OK
INFO:root:Column: total_entries
INFO:root:  - Name: OK
INFO:root:  - Type: OK
INFO:root:  - Nullable: OK
INFO:root:  - Mode: OK
INFO:root:Column: passers_by
INFO:root:  - Name: OK
INFO:root:  - Type: OK
INFO:root:  - Nullable: OK
INFO:root:  - Mode: OK
INFO:root:Column: entrance
INFO:root:  - Name: OK
INFO:root:  - Type: OK
INFO:root:  - Nullable: Expected True, got False
INFO:root:  - Mode: OK

Generated DDL:
CREATE TABLE `gia-develop-int-94070.deloitte_test.store_footfall` (
  datetime datetime,
  store_code str NOT NULL,
  country_iso2 str NOT NULL,
  total_entries int NOT NULL,
  passers_by int,
  entrance list NOT NULL
)

```


### Future Enhancements

- **Data Validation:** Add an optional feature to validate a sample of actual data against the expected types.
- **Logging/Reporting:** Improve the output to a structured format for logging or generating reports.
