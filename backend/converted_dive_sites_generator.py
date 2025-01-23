import pandas as pd

def generate_model_from_csv(csv_path, output_path):
    # Read the CSV file containing column definitions
    columns_df = pd.read_csv(csv_path)
    
    # Start building the model class as a string
    class_code = """
from sqlalchemy import Column, Integer, Float, String, Boolean
from app import db  # Assuming Flask-SQLAlchemy is being used

# Generated code by converted_dive_sites_generator.py
class ConvertedDiveSite(db.Model):
    __tablename__ = 'converted_dive_sites'
    
    id = db.Column(db.Integer, primary_key=True)
"""
    # Map data types from CSV to SQLAlchemy types
    type_mapping = {
        "integer": "db.Integer",
        "bigint": "db.Integer",
        "float": "db.Float",
        "text": "db.String",
        "boolean": "db.Boolean",
        "double precision": "db.Float"
    }
    
    # Generate columns from the CSV
    for _, row in columns_df.iterrows():
        if row['column_name'].strip().lower() == 'id':
            continue
        
        # Process the column name: lowercase and replace spaces with underscores
        column_name = row['column_name'].strip().lower().replace(' ', '_').replace('-', '_')


        data_type = type_mapping.get(row['data_type'].strip().lower())
        
        if not data_type:
            raise ValueError(f"Unsupported data type '{row['data_type']}' in CSV.")
        
        # Check if the column is nullable
        is_nullable = row['is_nullable'].strip().lower() == "yes"
        nullable_str = ", nullable=True" if is_nullable else ""

        # Add column definition to the class code
        class_code += f"    {column_name} = db.Column({data_type}{nullable_str})\n"
    
    # Write the generated class code to a text file
    with open(output_path, "w") as f:
        f.write(class_code)

# Example usage
csv_path = 'backend/Supabase Snippet Retrieve Column Information.csv'  # Replace with your actual CSV file path
output_path = 'backend/converted_dive_site_model.py'  # Path to save the generated Python code
generate_model_from_csv(csv_path, output_path)
