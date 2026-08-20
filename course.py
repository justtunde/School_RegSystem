"""
course.py
Same 3-part pattern as student.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
from database import db


# ---------- 1. Data class ----------
class Course:
    def __init__(self, course_id, course_code, course_name, credit_units, department_id, lecturer_id):
        self.course_id = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.credit_units = credit_units
        self.department_id = department_id
        self.lecturer_id = lecturer_id


# ---------- 2. CRUD manager ----------
class CourseManager:
    def add_course(self, course_code, course_name, credit_units, department_id, lecturer_id):
        try:
            cursor = db.get_cursor()
            query = """INSERT INTO Courses (course_code, course_name, credit_units, department_id, lecturer_id)
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (course_code, course_name, credit_units or 3,
                                    department_id or None, lecturer_id or None))
            db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            raise Exception(f"Could not add course: {e}")

    def get_all_courses(self):
        cursor = db.get_cursor()
        cursor.execute("""SELECT c.course_id, c.course_code, c.course_name, c.credit_units,
                                  d.department_name, l.first_name AS lecturer_first, l.last_name AS lecturer_last
                           FROM Courses c
                           LEFT JOIN Departments d ON c.department_id = d.department_id
                           LEFT JOIN Lecturers l ON c.lecturer_id = l.lecturer_id
                           ORDER BY c.course_id""")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def update_course(self, course_id, course_code, course_name, credit_units, department_id, lecturer_id):
        try:
            cursor = db.get_cursor()
            query = """UPDATE Courses
                       SET course_code=%s, course_name=%s, credit_units=%s,
                           department_id=%s, lecturer_id=%s
                       WHERE course_id=%s"""
            cursor.execute(query, (course_code, course_name, credit_units or 3,
                                    department_id or None, lecturer_id or None, course_id))
            db.connection.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Error as e:
            raise Exception(f"Could not update course: {e}")

    def delete_course(self, course_id):
        try:
            cursor = db.get_cursor()
            cursor.execute("DELETE FROM Courses WHERE course_id=%s", (course_id,))
            db.connection.commit()
            cursor.close()
            return cursor.rowcount > 0
        except Error as e:
            raise Exception(f"Could not delete course: {e}")


# ---------- 3. GUI frame ----------
class CourseFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = CourseManager()
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        form = tk.LabelFrame(self, text="Course Details", padx=10, pady=10)
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="Course Code").grid(row=0, column=0, sticky="w")
        self.code_entry = tk.Entry(form)
        self.code_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form, text="Course Name").grid(row=1, column=0, sticky="w")
        self.name_entry = tk.Entry(form)
        self.name_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form, text="Credit Units").grid(row=2, column=0, sticky="w")
        self.units_entry = tk.Entry(form)
        self.units_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(form, text="Department ID").grid(row=3, column=0, sticky="w")
        self.department_entry = tk.Entry(form)
        self.department_entry.grid(row=3, column=1, padx=5, pady=2)

        tk.Label(form, text="Lecturer ID").grid(row=4, column=0, sticky="w")
        self.lecturer_entry = tk.Entry(form)
        self.lecturer_entry.grid(row=4, column=1, padx=5, pady=2)

        btn_frame = tk.Frame(form)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Add", command=self.add).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update", command=self.update).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side="left", padx=5)

    def _build_table(self):
        columns = ("id", "code", "name", "units", "department", "lecturer")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            courses = self.manager.get_all_courses()
            for c in courses:
                lecturer_name = "-"
                if c.get("lecturer_first"):
                    lecturer_name = f"{c['lecturer_first']} {c['lecturer_last']}"
                self.tree.insert("", "end", values=(
                    c["course_id"], c["course_code"], c["course_name"], c["credit_units"],
                    c.get("department_name") or "-", lecturer_name
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        self.selected_id = values[0]
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, values[1])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[2])
        self.units_entry.delete(0, tk.END)
        self.units_entry.insert(0, values[3])

    def add(self):
        try:
            self.manager.add_course(
                self.code_entry.get().strip(),
                self.name_entry.get().strip(),
                self.units_entry.get().strip() or None,
                self.department_entry.get().strip() or None,
                self.lecturer_entry.get().strip() or None
            )
            messagebox.showinfo("Success", "Course added.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a course from the table first.")
            return
        try:
            self.manager.update_course(
                self.selected_id,
                self.code_entry.get().strip(),
                self.name_entry.get().strip(),
                self.units_entry.get().strip() or None,
                self.department_entry.get().strip() or None,
                self.lecturer_entry.get().strip() or None
            )
            messagebox.showinfo("Success", "Course updated.")
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select a course from the table first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this course?"):
            return
        try:
            self.manager.delete_course(self.selected_id)
            self.clear_form()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.selected_id = None
        self.code_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.units_entry.delete(0, tk.END)
        self.department_entry.delete(0, tk.END)
        self.lecturer_entry.delete(0, tk.END)