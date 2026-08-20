"""
department.py
TODO: Copy the 3-part pattern from student.py:
  1. Department class (department_id, department_name)
  2. DepartmentManager: add_department, get_all_departments,
     update_department, delete_department
  3. DepartmentFrame: same Tkinter layout as StudentFrame but with
     just a "Department Name" field (no search needed unless you want it)

This is the simplest module to build next since it only has one field.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
from database import db


# ---------- 1. Data class ----------
"""
department.py
Same 3-part pattern as student.py, simplified to one field.
"""


# ---------- 1. Data class ----------
class Department:
    def __init__(self, department_id, department_name):
        self.department_id = department_id
        self.department_name = department_name


# ---------- 2. CRUD manager ----------
class DepartmentManager:
    def add_department(self, department_name):
        try:
            cursor = db.get_cursor()
            cursor.execute(
                "INSERT INTO Departments (department_name) VALUES (%s)",
                (department_name,)
            )
            db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            raise Exception(f"Could not add department: {e}")

    def get_all_departments(self):
        cursor = db.get_cursor()
        cursor.execute("SELECT department_id, department_name FROM Departments ORDER BY department_id")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def update_department(self, department_id, department_name):
        try:
            cursor = db.get_cursor()
            cursor.execute(
                "UPDATE Departments SET department_name=%s WHERE department_id=%s",
                (department_name, department_id)
            )
            db.connection.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Error as e:
            raise Exception(f"Could not update department: {e}")

    def delete_department(self, department_id):
        try:
            cursor = db.get_cursor()
            cursor.execute("DELETE FROM Departments WHERE department_id=%s", (department_id,))
            db.connection.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Error as e:
            raise Exception(f"Could not delete department: {e}")


# ---------- 3. GUI frame ----------
class DepartmentFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = DepartmentManager()
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        form = tk.LabelFrame(self, text="Department Details", padx=10, pady=10)
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="Department Name").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(form)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)

        btn_frame = tk.Frame(form)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Add", command=self.add).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update", command=self.update).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side="left", padx=5)

    def _build_table(self):
        columns = ("id", "name")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Department Name")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            departments = self.manager.get_all_departments()
            for d in departments:
                self.tree.insert("", "end", values=(d["department_id"], d["department_name"]))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        self.selected_id = values[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])

    def add(self):
        try:
            self.manager.add_department(self.name_entry.get().strip())
            messagebox.showinfo("Success", "Department added.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a department from the table first.")
            return
        try:
            self.manager.update_department(self.selected_id, self.name_entry.get().strip())
            messagebox.showinfo("Success", "Department updated.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a department from the table first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this department?"):
            return
        try:
            self.manager.delete_department(self.selected_id)
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.selected_id = None
        self.name_entry.delete(0, tk.END)