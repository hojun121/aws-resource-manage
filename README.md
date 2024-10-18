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
pip install pandas openpyxl xlsxwriter
```

## 5. Run the Script

Execute the `init.py` script with the following command:

```bash
python __init__.py
```

## 6. Check the Results

The processed Excel file can be found in the `file > download directory`.

---