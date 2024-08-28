import requests

BASE_URL = "http://127.0.0.1:9000"

# Test Data
user1_availability = {
    "user_id": "user123",
    "availability": [
        {"start_time": "2024-09-27T09:00:00+00:00", "end_time": "2024-09-27T11:00:00+00:00"},
        {"start_time": "2024-09-29T09:00:00+00:00", "end_time": "2024-09-29T11:00:00+00:00"},
        {"start_time": "2024-09-30T09:00:00+00:00", "end_time": "2024-09-30T11:00:00+00:00"}
    ]
}

user2_availability = {
    "user_id": "user456",
    "availability": [
        {"start_time": "2024-09-27T09:30:00+00:00", "end_time": "2024-09-27T10:30:00+00:00"},
        {"start_time": "2024-09-29T10:00:00+00:00", "end_time": "2024-09-29T11:00:00+00:00"},
        {"start_time": "2024-09-30T08:00:00+00:00", "end_time": "2024-09-30T09:00:00+00:00"}
    ]
}

# 1. Set Availability for User 1 (Current User, for simplicity)
response = requests.post(f"{BASE_URL}/availability", json=user1_availability)
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("User 1 availability set successfully.")

# 2. Set Availability for User 2 (Assuming this user is someone else)
response = requests.post(f"{BASE_URL}/availability", json=user2_availability)
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("User 2 availability set successfully.")

# 3. Get Availability for User 1
response = requests.get(f"{BASE_URL}/availability")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
user1_data = response.json()
print("User 1 availability retrieved successfully.", user1_data)


# 4. Find Overlap Between User 1 and User 2
overlap_request = {
    "user_id_2": "user456"
}
response = requests.get(f"{BASE_URL}/overlap/user456", json=overlap_request)
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
overlap_data = response.json()
assert len(overlap_data['overlap']) > 0, "Expected at least one overlapping interval"
print("Overlap between User 1 and User 2 found successfully.", overlap_data)


# 5. Get Availability for User 1 After Rescheduling
# Reschedule Test Data
reschedule_data = {
    "old_slot": {
        "start_time": "2024-09-29T09:00:00+00:00",
        "end_time": "2024-09-29T11:00:00+00:00"
    },
    "new_slot": {
        "start_time": "2024-09-29T12:00:00+00:00",
        "end_time": "2024-09-29T14:00:00+00:00"
    }
}

response = requests.post(f"{BASE_URL}/reschedule", json=reschedule_data)
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("User 1 slot rescheduled successfully.")

response = requests.get(f"{BASE_URL}/availability")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
user1_data_after_reschedule = response.json()
print("User 1 availability after rescheduling retrieved successfully.", user1_data_after_reschedule)

# Verify the rescheduled slot is updated
expected_new_slot = reschedule_data["new_slot"]
rescheduled_slots = [
    slot for slot in user1_data_after_reschedule['availability']
    if slot['start_time'] == expected_new_slot['start_time'] and slot['end_time'] == expected_new_slot['end_time']
]

assert len(rescheduled_slots) > 0, "Rescheduled slot not found in user availability"
print("Rescheduled slot verified successfully.")