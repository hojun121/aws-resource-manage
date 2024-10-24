# Project Setup and Execution Instructions

## 1. Install Anaconda

- Download and install Anaconda from the [Anaconda download page](https://www.anaconda.com/products/distribution#download-section).

## 2. Create a Virtual Environment

Open a terminal or Anaconda Prompt and run the following command to create a virtual environment:

```bash
conda create -n myenv python=3.9
```

You can replace `myenv` with your desired environment name.

## 3. Activate the Virtual Environment

Activate the virtual environment with the following command:

```bash
conda activate myenv
```

## 4. Install Required Packages

Install the necessary packages using the following command:

```bash
pip install pandas openpyxl xlsxwriter SQLAlchemy psycopg2 tqdm
```

### Explanation of Required Packages:
- **pandas**: For data manipulation and analysis.
- **openpyxl**: To work with Excel files in Python.
- **xlsxwriter**: For creating Excel files.
- **SQLAlchemy**: To manage database connections.
- **psycopg2**: PostgreSQL database adapter for Python.

## 5. Set Up Database Connection

Ensure that the PostgreSQL database is running and that the connection URI in the `__init__.py` file is correctly set. The current format in the file is:

```
DB_URI = 'postgresql://username:password@localhost:port/dbname'
```

Update it with the actual credentials and connection details of your PostgreSQL instance.

## 6. Run the Script

Execute the `__init__.py` script with the following command:

```bash
python __init__.py
```

Make sure the required directories (`file/upload` and `file/download`) exist. The script will process data and save the results in an Excel file.

## 7. Check the Results

The processed Excel file can be found in the `file/download` directory. The file is named based on the schema and the current date (e.g., `toolbox_prod_inventory_YYYYMMDD.xlsx`).

---