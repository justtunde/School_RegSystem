"""
lecturer.py
Same 3-part pattern as student.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
from database import db


# ---------- 1. Data class ----------
class Lecturer:
    def __init__(self, lecturer_id, first_name, last_name, email, department_id):
        self.lecturer_id = lecturer_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.department_id = department_id


# ---------- 2. CRUD manager ----------
class LecturerManager:
    def add_lecturer(self, first_name, last_name, email, department_id):
        try:
            cursor = db.get_cursor()
            query = """INSERT INTO Lecturers (first_name, last_name, email, department_id)
                       VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (first_name, last_name, email, department_id or None))
            db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            raise Exception(f"Could not add lecturer: {e}")

    def get_all_lecturers(self):
        cursor = db.get_cursor()
        cursor.execute("""SELECT l.lecturer_id, l.first_name, l.last_name, l.email,
                                  d.department_name
                           FROM Lecturers l
                           LEFT JOIN Departments d ON l.department_id = d.department_id
                           ORDER BY l.lecturer_id""")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def update_lecturer(self, lecturer_id, first_name, last_name, email, department_id):
        try:
            cursor = db.get_cursor()
            query = """UPDATE Lecturers
                       SET first_name=%s, last_name=%s, email=%s, department_id=%s
                       WHERE lecturer_id=%s"""
            cursor.execute(query, (first_name, last_name, email, department_id or None, lecturer_id))
            db.connection.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Error as e:
            raise Exception(f"Could not update lecturer: {e}")

    def delete_lecturer(self, lecturer_id):
        try:
            cursor = db.get_cursor()
            cursor.execute("DELETE FROM Lecturers WHERE lecturer_id=%s", (lecturer_id,))
            db.connection.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Error as e:
            raise Exception(f"Could not delete lecturer: {e}")


# ---------- 3. GUI frame ----------
class LecturerFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = LecturerManager()
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        form = tk.LabelFrame(self, text="Lecturer Details", padx=10, pady=10)
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="First Name").grid(row=0, column=0, sticky="w")
        self.first_name_entry = tk.Entry(form)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form, text="Last Name").grid(row=1, column=0, sticky="w")
        self.last_name_entry = tk.Entry(form)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form, text="Email").grid(row=2, column=0, sticky="w")
        self.email_entry = tk.Entry(form)
        self.email_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(form, text="Department ID").grid(row=3, column=0, sticky="w")
        self.department_entry = tk.Entry(form)
        self.department_entry.grid(row=3, column=1, padx=5, pady=2)

        btn_frame = tk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Add", command=self.add).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update", command=self.update).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side="left", padx=5)

    def _build_table(self):
        columns = ("id", "first_name", "last_name", "email", "department")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            lecturers = self.manager.get_all_lecturers()
            for l in lecturers:
                self.tree.insert("", "end", values=(
                    l["lecturer_id"], l["first_name"], l["last_name"],
                    l["email"], l.get("department_name") or "-"
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        self.selected_id = values[0]
        self.first_name_entry.delete(0, tk.END)
        self.first_name_entry.insert(0, values[1])
        self.last_name_entry.delete(0, tk.END)
        self.last_name_entry.insert(0, values[2])
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, values[3])

    def add(self):
        try:
            self.manager.add_lecturer(
                self.first_name_entry.get().strip(),
                self.last_name_entry.get().strip(),
                self.email_entry.get().strip(),
                self.department_entry.get().strip() or None
            )
            messagebox.showinfo("Success", "Lecturer added.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a lecturer from the table first.")
            return
        try:
            self.manager.update_lecturer(
                self.selected_id,
                self.first_name_entry.get().strip(),
                self.last_name_entry.get().strip(),
                self.email_entry.get().strip(),
                self.department_entry.get().strip() or None
            )
            messagebox.showinfo("Success", "Lecturer updated.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a lecturer from the table first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this lecturer?"):
            return
        try:
            self.manager.delete_lecturer(self.selected_id)
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.selected_id = None
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.department_entry.delete(0, tk.END)