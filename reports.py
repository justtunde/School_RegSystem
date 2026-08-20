"""
reports.py
One button per report. Each button runs a query and shows results
in the shared Treeview below. Uses the views created in schema.sql
where possible.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db


class ReportManager:
    def all_students(self):
        cursor = db.get_cursor()
        cursor.execute("SELECT student_id, first_name, last_name, email FROM Students ORDER BY student_id")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def students_with_departments(self):
        cursor = db.get_cursor()
        cursor.execute("SELECT * FROM StudentsWithDepartments")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def students_per_course(self):
        cursor = db.get_cursor()
        cursor.execute("SELECT * FROM CourseRegistrationReport ORDER BY course_code")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def courses_per_lecturer(self):
        cursor = db.get_cursor()
        cursor.execute("""SELECT l.first_name, l.last_name, c.course_code, c.course_name
                           FROM Lecturers l
                           JOIN Courses c ON l.lecturer_id = c.lecturer_id
                           ORDER BY l.last_name""")
        rows = cursor.fetchall()
        cursor.close()
        return rows


class ReportsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = ReportManager()

        btn_frame = tk.LabelFrame(self, text="Reports", padx=10, pady=10)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text="All Students",
                  command=self.show_all_students).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Students with Departments",
                  command=self.show_students_with_departments).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Students per Course",
                  command=self.show_students_per_course).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Courses per Lecturer",
                  command=self.show_courses_per_lecturer).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _display(self, rows):
        # Rebuild the table's columns to match whatever report was run,
        # since each report has different fields.
        self.tree.delete(*self.tree.get_children())
        if not rows:
            self.tree["columns"] = ()
            messagebox.showinfo("No data", "This report returned no rows.")
            return

        columns = list(rows[0].keys())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120)

        for row in rows:
            self.tree.insert("", "end", values=[row[c] for c in columns])

    def show_all_students(self):
        try:
            self._display(self.manager.all_students())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_students_with_departments(self):
        try:
            self._display(self.manager.students_with_departments())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_students_per_course(self):
        try:
            self._display(self.manager.students_per_course())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_courses_per_lecturer(self):
        try:
            self._display(self.manager.courses_per_lecturer())
        except Exception as e:
            messagebox.showerror("Error", str(e))