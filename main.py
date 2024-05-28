from google.cloud import bigquery
import logging

import config

type_map = {
    'datetime': 'DATETIME',
    'str': 'STRING',
    'int': 'INTEGER',
    'list': 'RECORD'
}


def validate_schema(project_id, dataset_id, table_id, config_file_path):
    client = bigquery.Client(project=project_id)

    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    actual_schema = {field.name: (field.field_type, field.is_nullable, field.mode) for field in table.schema}

    with open(config_file_path, 'r') as f:
        config_schema = {}
        for line in f:
            col_name, data_type, *constraints = line.strip().split(',')
            config_schema[col_name] = (data_type, "REQUIRED" in constraints, "REPEATED" in constraints)

    for col_name, (data_type, required, repeated) in config_schema.items():
        actual_type, actual_nullable, actual_mode = actual_schema.get(col_name, (None, None, None))
        logging.info(f"Column: {col_name}")
        logging.info(f"  - Name: {'OK' if actual_type else 'MISSING'}")

        bigquery_type = type_map.get(data_type, data_type).upper()
        logging.info(
            f"  - Type: {'OK' if bigquery_type == actual_type else f'Expected {bigquery_type}, got {actual_type}'}")

        expected_nullable = not required
        logging.info(
            f"  - Nullable: {'OK' if expected_nullable == actual_nullable else f'Expected {expected_nullable}, got {actual_nullable}'}")

        expected_mode = "REPEATED" if repeated else "NULLABLE" if expected_nullable else "REQUIRED"
        logging.info(
            f"  - Mode: {'OK' if expected_mode == actual_mode else f'Expected {expected_mode}, got {actual_mode}'}")

        if "PK" in constraints:
            query = f"""
                SELECT 1 
                FROM {dataset_id}.INFORMATION_SCHEMA.COLUMNS
                WHERE table_name = '{table_id}'
                  AND column_name = '{col_name}'
                  AND is_primary_key = 'YES'
            """
            is_pk = client.query(query).result().total_rows > 0
            logging.info(f"  - Primary Key: {'OK' if is_pk else 'Expected PK, but not a PK'}")

        if "FK" in constraints:
            query = f"""
                SELECT 1
                FROM {dataset_id}.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS  
                WHERE table_name = '{table_id}'
                  AND column_name = '{col_name}'
            """
            is_fk = client.query(query).result().total_rows > 0
            logging.info(f"  - Foreign Key: {'OK' if is_fk else 'Expected FK, but not an FK'}")

        if "UNIQUE" in constraints:
            query = f"""
                SELECT COUNT(DISTINCT {col_name}) = COUNT(*) AS is_unique
                FROM `{project_id}.{dataset_id}.{table_id}`
            """
            is_unique = client.query(query).result().rows[0].is_unique
            logging.info(f"  - Unique: {'OK' if is_unique else 'Expected UNIQUE, but has duplicates'}")

        if any(c.startswith("RANGE") for c in constraints):
            range_constraint = next(c for c in constraints if c.startswith("RANGE"))
            min_val, max_val = map(int, range_constraint.split(" ")[1:])
            query = f"""
                SELECT 
                    MIN({col_name}) >= {min_val} AND MAX({col_name}) <= {max_val} AS in_range
                FROM `{project_id}.{dataset_id}.{table_id}`  
            """
            in_range = client.query(query).result().rows[0].in_range
            logging.info(
                f"  - Range: {'OK' if in_range else f'Expected range {min_val} to {max_val}, but values are outside this range'}")


def generate_schema_ddl(config_file_path, project, dataset, table):
    ddl = f"CREATE TABLE `{project}.{dataset}.{table}` (\n"
    with open(config_file_path, 'r') as f:
        for line in f:
            col_name, data_type, *constraints = line.strip().split(',')
            ddl += f"  {col_name} {data_type}"
            if "NULLABLE" not in constraints:
                ddl += " NOT NULL"
            if "PK" in constraints:
                ddl += " PRIMARY KEY"
            ddl += ",\n"
    ddl = ddl.rstrip(",\n") + "\n)"
    return ddl


def validate_config(config_file_path):
    column_names = set()
    with open(config_file_path, 'r') as f:
        for line in f:
            col_name, data_type, *constraints = line.strip().split(',')
            if col_name in column_names:
                raise ValueError(f"Duplicate column name: {col_name}")
            column_names.add(col_name)
            bigquery_type = type_map.get(data_type, data_type).upper()
            if bigquery_type not in [e.name for e in bigquery.enums.SqlTypeNames]:
                raise ValueError(f"Invalid data type: {data_type}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    project_id = config.project_id
    dataset_id = config.dataset_id
    table_id = config.table_id
    config_file_path = config.schema_file_path

    validate_config(config_file_path)
    validate_schema(project_id, dataset_id, table_id, config_file_path)
    ddl = generate_schema_ddl(config_file_path, project_id, dataset_id, table_id)
    print("\nGenerated DDL:")
    print(ddl)
