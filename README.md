# Trekking Management Application

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)

## Introduction
The Trekking Management Application helps adventure organizations manage trek approvals, staff assignments, and trekker bookings in one place, replacing manual coordination over spreadsheets and phone calls. Admins create and manage treks, trek staff handle the treks assigned to them, and trekkers can browse open treks and book a slot, all with role-based access control.

## Features
- Role-based authentication for Admin, Trek Staff, and Trekkers
- Admin is pre-created programmatically (no admin registration)
- Trek Staff self-register but can only log in after Admin approval
- Admin dashboard with trek/user/staff/booking counts, full trek CRUD, staff approval and assignment, blacklist controls, and search by name or ID
- Trek Staff dashboard limited to their assigned treks, with slot/status updates and participant management
- Trekker dashboard to browse and filter open treks by difficulty and location, book a trek, and view booking history
- Overbooking prevention, duplicate-booking prevention, and booking allowed only when a trek is Open
- Complete booking history maintained per user (treks with existing bookings cannot be deleted)
- Trek status tracking through Pending / Approved / Open / Closed / Completed

## Technologies Used
- **Backend:** Flask, Flask-SQLAlchemy
- **Frontend:** HTML, Jinja2, Bootstrap
- **Database:** SQLite

## Installation
1. Clone the repository:
   - git clone `https://github.com/itsayushch/trekking-management-system`
   - cd trekking-management-system
2. Create a virtual environment:
   - python -m venv venv
   - source venv/Scripts/activate (On Windows use `venv\Scripts\activate`)
3. Install the required packages:
   - pip install -r requirements.txt
4. Create the pre-defined Admin account:
   - python seed_admin.py
5. Run the application
   - python app.py

## Usage
- Open http://127.0.0.1:5000 in your browser.
- Login as Admin with `admin@gmail.com` / `admin123` (created by `seed_admin.py`).
- Register as a Trekker to browse and book treks, or register as Trek Staff and wait for Admin approval before logging in.

