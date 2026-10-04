# EduSphere - Production School Management System

A real-time, production-style School Management Web Application built with **Django**, **Django REST Framework**, and **Tailwind CSS**. It enforces strict **Role-Based Access Control (RBAC)** across three primary tiers: **Principal**, **Teacher**, and **Student**.

---

## 👥 Role Permissions & Access Control Matrix

| Feature / Module | 👑 Principal (Admin) | 👨‍🏫 Teacher | 🎓 Student |
| :--- | :---: | :---: | :---: |
| **School Overview & KPI Analytics** | ✅ Full Access (All School KPIs) | ⚠️ Limited (Assigned Classes only) | ⚠️ Limited (Personal Stats only) |
| **Student Directory & Admissions** | ✅ View, Admit, Edit, Delete | ⚠️ View Assigned Section Students | 🔒 View Personal Profile only |
| **Faculty & Teacher Directory** | ✅ View, Hire, Assign Subjects | ⚠️ View Staff Directory & Personal Profile | ⚠️ Read-Only Directory |
| **Academics (Classes, Sections, Subjects)**| ✅ Full CRUD Access | ⚠️ Read-Only Curriculum | ⚠️ Read-Only Curriculum |
| **Attendance Management** | ✅ School-Wide View & Reports | ✅ Live Bulk Marking for Assigned Classes | 🔒 View Own Attendance History |
| **Fees & Invoices Ledger** | ✅ Full Access (Set Fees, Record Payments) | ❌ Restricted (403 Forbidden) | ⚠️ View Own Fees & Receipts |
| **Teacher Leave Management** | ✅ One-Click Approve / Reject with Remarks | ✅ Submit Requests & Track Status | ❌ Restricted (403 Forbidden) |

---

## 🚀 Instant Demo Credentials

The database comes pre-seeded with realistic production data. You can log in with:

| Persona | Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Dr. Rajiv Verma** | 👑 Principal | `principal` | `password123` | **Full Unrestricted Access** |
| **Mr. Rajesh Kumar** | 👨‍🏫 Teacher | `teacher.rajesh` | `password123` | **Class 10-A (Class Teacher), Math & Science** |
| **Rahul Verma** | 🎓 Student | `student.rahul` | `password123` | **Class 10-A, Roll #1** |

> 💡 **Quick Role Switcher**: At the top of every dashboard page, an interactive demo bar allows you to switch between **Principal**, **Teacher**, and **Student** with a single click to instantly test permissions in real-time.

---

## 🛠️ How to Run the Website

Activate the virtual environment and launch the server:

```powershell
.\venv\Scripts\python.exe manage.py runserver 8000
```

Open your browser and visit:
👉 **http://127.0.0.1:8000/**

To re-seed fresh demo data at any time:
```powershell
.\venv\Scripts\python.exe manage.py seed_demo_data
```

---

## 🌟 Key Production Features

1. **Real-time Live Attendance Register**:
   - Teachers select their assigned class/section.
   - Click "Mark All Present" or toggle per-student (`P`, `A`, `L`, `HD`).
   - Saves in real-time to the database via `/api/attendance/bulk-mark/`.

2. **Executive Principal Command Center**:
   - Dynamic KPIs: Enrolled students, faculty, today's attendance percentage, and pending leave queue.
   - Interactive Doughnut Chart showing live Present vs Absent ratio.
   - Fee collection progress bar comparing expected vs collected fees.

3. **Faculty Leave Workflow**:
   - Teachers submit leave requests with category, dates, and justification.
   - The Principal's dashboard instantly flags pending requests with a badge.
   - The Principal can approve or reject with custom feedback remarks.

4. **Student Financial & Academic Self-Service**:
   - Verified student card with Admission ID, Roll No, and Blood Group.
   - Attendance percentage ring and date-by-date verified attendance history.
   - Transparent fee ledgers with breakdown of Tuition, Transport, and Exam fees with itemized payment receipts.
