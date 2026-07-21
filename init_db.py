import pandas as pd
import sqlite3
import os
import db

EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SUIVI CITERNE 2107.xlsx")

def init_database_from_excel(force=False):
    db.create_tables()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if already populated
    cursor.execute("SELECT COUNT(*) FROM citernes")
    count = cursor.fetchone()[0]
    if count > 0 and not force:
        print(f"Database already populated with {count} citernes. Use force=True to re-init.")
        conn.close()
        return

    if force:
        cursor.execute("DELETE FROM suivi_progress")
        cursor.execute("DELETE FROM etapes")
        cursor.execute("DELETE FROM citernes")
        conn.commit()

    print("Parsing Excel file:", EXCEL_PATH)
    xl = pd.ExcelFile(EXCEL_PATH)
    
    for sheet in ['CARBURANT', 'EAU']:
        print(f"\nProcessing sheet: {sheet}")
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=None)
        
        cadence_row_idx = 5 if sheet == 'CARBURANT' else 9
        code_col_idx = 3 if sheet == 'CARBURANT' else 4
        start_data_row = 6 if sheet == 'CARBURANT' else 10
        
        # 1. Extract Steps & Categories with Forward Fill for Merged Cells
        header_df = df.iloc[1:cadence_row_idx, code_col_idx+1:].copy()
        header_ffill = header_df.ffill(axis=1)
        
        etapes_list = []
        step_id_map = {} # col_index -> step_db_id
        
        step_order = 1
        for col_i, c in enumerate(range(code_col_idx+1, df.shape[1])):
            col_headers = []
            for r_i in range(header_ffill.shape[0]):
                val = header_ffill.iloc[r_i, col_i]
                if pd.notna(val):
                    val_str = str(val).strip().replace('\n', ' ')
                    if not val_str.startswith('Citerne') and val_str not in col_headers:
                        col_headers.append(val_str)
                        
            cadence_val = df.iloc[cadence_row_idx, c]
            try:
                cadence_hours = float(cadence_val) if pd.notna(cadence_val) else 1.0
                if cadence_hours <= 0: cadence_hours = 1.0
            except:
                cadence_hours = 1.0
                
            category = col_headers[0] if col_headers else 'Général'
            step_name = ' - '.join(col_headers[1:]) if len(col_headers) > 1 else col_headers[0]
            
            cursor.execute("""
            INSERT INTO etapes (citerne_type, category, step_name, cadence_hours, step_order)
            VALUES (?, ?, ?, ?, ?)
            """, (sheet, category, step_name, cadence_hours, step_order))
            
            step_id = cursor.lastrowid
            step_id_map[c] = step_id
            step_order += 1
            
        print(f"Inserted {len(step_id_map)} steps for {sheet}.")
        
        # 2. Extract Citernes and Progress
        citerne_count = 0
        for r in range(start_data_row, df.shape[0]):
            code_val = df.iloc[r, code_col_idx]
            if pd.notna(code_val) and str(code_val).strip():
                code = str(code_val).strip()
                
                # Check comments in other non-step columns
                comment_parts = []
                for c in range(0, code_col_idx):
                    val = df.iloc[r, c]
                    if pd.notna(val) and type(val) == str and not val.strip().isdigit():
                        comment_parts.append(str(val).strip())
                initial_comment = " | ".join(comment_parts) if comment_parts else ""
                
                cursor.execute("""
                INSERT OR REPLACE INTO citernes (code, type, comments)
                VALUES (?, ?, ?)
                """, (code, sheet, initial_comment))
                citerne_count += 1
                
                # Extract step progress values
                for col_idx, step_id in step_id_map.items():
                    val = df.iloc[r, col_idx]
                    pct = 0.0
                    if pd.notna(val):
                        try:
                            fval = float(val)
                            if fval == 1.0 or fval == 1:
                                pct = 100.0
                            elif fval > 0.0 and fval <= 1.0:
                                pct = round(fval * 100.0, 1)
                            elif fval > 1.0:
                                pct = min(100.0, float(fval))
                        except:
                            pct = 0.0
                            
                    cursor.execute("""
                    INSERT OR REPLACE INTO suivi_progress (citerne_code, step_id, completion_pct, comment)
                    VALUES (?, ?, ?, '')
                    """, (code, step_id, pct))
                    
        print(f"Inserted {citerne_count} citernes for {sheet}.")

    conn.commit()
    conn.close()
    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    init_database_from_excel(force=True)
