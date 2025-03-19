import re
import os

# INPUTS
dbSfname = os.getenv('DB_SFNAME', 'Dbname')
schemaSfname = os.getenv('SCHEMA_SFNAME', 'Schemaname')
fileLoc = os.getenv('FILE_LOC', 'ddl_files')
folder_path = "snowflake/conversion"

def extract_table_info(ddl):
    # Regex to handle 'CREATE OR REPLACE TABLE' and 'CREATE TABLE'
    pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:([\w]+)\.)?(?:([\w]+)\.)?(\w+)'
    match = re.search(pattern, ddl, re.IGNORECASE)
    
    if match:
        db_name = match.group(1) or dbSfname
        schema_name = match.group(2) or schemaSfname
        table_name = match.group(3)
        return db_name, schema_name, table_name
    return None, None, None

def rename_ddl_files(folder_path):
    print(f"Processing files in folder: {folder_path}")
    # Loop through all .sql files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".sql"):
            file_path = os.path.join(folder_path, file_name)
            print(f"Reading file: {file_path}")
            
            # Read DDL content
            with open(file_path, 'r') as file:
                ddl_content = file.read()

            # Extract table info
            db_name, schema_name, table_name = extract_table_info(ddl_content)
            print(f"Extracted info - DB: {db_name}, Schema: {schema_name}, Table: {table_name}")
            
            if table_name:
                # Generate new file name
                new_file_name = f"R__{db_name}_{schema_name}_{table_name}.sql"
                new_file_path = os.path.join(folder_path, new_file_name)
                
                # Rename the file
                os.rename(file_path, new_file_path)
                print(f"Renamed: {file_name} ➜ {new_file_name}")

                tbl_patterns = [
                    r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE',
                    r'CREATE\s+TABLE',
                    r'CREATE\s+TABLE\s+IF\s+NOT\s+EXIST',
                ]

                for pattern in tbl_patterns:
                    ddl_content = re.sub(pattern, 'CREATE OR ALTER TABLE', ddl_content, flags=re.IGNORECASE)

                # Write the modified content back to the file
                with open(new_file_path, 'w') as file:
                    file.write(ddl_content)

                print("Done Replace")
            else:
                print(f"No table info found in {file_name}")

if __name__ == "__main__":
    # Example usage
    rename_ddl_files(folder_path)