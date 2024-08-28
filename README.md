# Calendly API with Flask

This repository contains a simple implementation of a Calendly-like scheduling API using Flask in Python. The API allows users to set their availability, view availability, and find overlapping time slots between two users.

## Assumptions
- **user_id='user123'** is considered as logged_in user for get_availability, reschedule, delete and finding overlap.
- For simplicity purpose, set_availability is allowed to set for any user. 
   In ideal scenario, current user can set his availability only
- In memory DB is taken for consideration.
- In apis, only UTC timezone is allowed. This will avoid complexity in codebase.
- User has to pass isoformat str as datetimes for setting availability.


## Features

- **Set Availability**: Users can set their availability in UTC.
- **View Availability**: Retrieve the availability of a user.
- **Find Overlap**: Determine overlapping availability between two users.
- **Delete Availability (Pre-Existing Slot)**: Remove existing availability.

## Endpoints
- Hosted the app on vercel.
- BASE_URL: https://calendly-chi-nine.vercel.app/

### 1. `/availability` (POST)
Set a user's availability. Period is taken either "weekly" or "none" for now. 
We can extend this functionality.

- **Request**: 
  ```json
  {
      "user_id": "user123",
      "availability": [
          {"start_time": "2024-09-27T09:00:00Z", "end_time": "2024-09-27T10:00:00Z"}
      ]
  }
- **Response**: 
  ```json
    {
    "message": "Availability set successfully"
    }

### 2. `/availability` (GET)
Set a user's availability.
- **Response**: 
  ```json
    {
        "user_id": "user123",
        "availability": [
            {"start_time": "2024-09-27T09:00:00Z", "end_time": "2024-09-27T10:00:00Z"}
        ]
    }

### 3. `/overlap` (GET)
Set a user's availability.
- **Request**: 
  ```json
    {
    "user_id_2": "user456"
    }
- **Response**: 
  ```json
    {
        "overlap": [
            {"start_time": "2024-09-27T09:00:00Z", "end_time": "2024-09-27T09:30:00Z"}
        ]
    }

### 4. `/availability` (DELETE)
Reschedule availability time slot
- **Request**: 
  ```json
    {
      "start_time": "2024-09-29T09:00:00+00:00",
      "end_time": "2024-09-29T11:00:00+00:00"
  }
- **Response**: 
    ```json
  {
      "message": "Availability slot deleted successfully"
  }
  
## Setup

### 1. Clone the Repository

```bash
    git clone https://github.com/AnkurSaldhi/calendly.git
    cd calendly
```
### 2. Create virtual env
```bash
  python -m venv venv
  source venv/bin/activate
```
### 3. Run flask server
```bash
  export FLASK_APP=calendly.py
  flask run
```