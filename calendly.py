from flask import Flask, request, jsonify
from datetime import datetime, timezone, timedelta
from collections import defaultdict

app = Flask(__name__)

# In-memory storage for availability
availability_db = defaultdict(list)


# Helper function to parse ISO 8601 timestamps
def parse_iso8601(timestamp):
    """Parse an ISO 8601 formatted string into a datetime object, ensuring UTC."""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    # Check if the parsed datetime object is in UTC
    if dt.tzinfo != timezone.utc:
        return None  # Return None to indicate it's not in UTC

    return dt


# Helper function
def to_iso8601(dt):
    return dt.isoformat()


# Helper function to check overlap between two intervals
def get_overlap(intervals1, intervals2):
    overlap = []
    ptr1, ptr2 = 0, 0

    while ptr1 < len(intervals1) and ptr2 < len(intervals2):
        start1, end1 = intervals1[ptr1]
        start2, end2 = intervals2[ptr2]

        latest_start = max(start1, start2)
        earliest_end = min(end1, end2)

        if latest_start < earliest_end and is_future_date(latest_start):
            overlap.append((latest_start, earliest_end))

        if end1 < end2:
            ptr1 += 1
        else:
            ptr2 += 1

    return overlap


# Endpoint to set availability
def is_future_date(date):
    """Check if the given datetime object is in the future."""
    current_time = datetime.now(tz=timezone.utc)
    return date > current_time

@app.route('/', methods=['GET'])
def ping():
    return jsonify({"message": "Server Running"})

@app.route('/availability', methods=['POST'])
def set_availability():
    """
    only UTC timezone will be considered
    """
    data = request.json
    user_id = data['user_id']

    if user_id not in availability_db:
        availability_db[user_id] = []


    for slot in data['availability']:
        start_time = parse_iso8601(slot['start_time'])
        end_time = parse_iso8601(slot['end_time'])
        period = slot.get('period', 'none')  # Get the period if provided, default to 'none'

        if start_time is None or end_time is None:
            return jsonify({"error": "Timestamps must be in UTC format (e.g., '2024-09-27T09:00:00Z')."}), 400

        if not is_future_date(start_time):
            return jsonify({"error": f"Start time {start_time.isoformat()} is not in the future."}), 400

        if end_time < start_time:
            return jsonify({"error": f"End time {end_time.isoformat()} must be greater than start time {start_time.isoformat()}."}), 400

        if period == 'weekdays':
            # Calculate weekly availability for the next 30 days, only on weekdays
            end_period = start_time + timedelta(days=30)
            current_start = start_time
            current_end = end_time
            while current_start < end_period:
                if current_start.weekday() < 5:  # Weekday check: 0 (Monday) to 4 (Friday)
                    if (current_start, current_end) not in availability_db[user_id]:
                        availability_db[user_id].append((current_start, current_end))

                current_start += timedelta(days=1)
                current_end += timedelta(days=1)
        else:
            # Add a single availability slot for non-weekly periods
            if (start_time, end_time) not in availability_db[user_id]:
                availability_db[user_id].append((start_time, end_time))

    # Sorting the intervals for efficient overlap calculations
    availability_db[user_id].sort()
    return jsonify({"message": "Availability set successfully"}), 200


# Endpoint to get own availability
@app.route('/availability', methods=['GET'])
def get_availability():
    user_id = 'user123' # current session user
    user_availability = availability_db.get(user_id, [])

    future_availability = [
        (start_time, end_time) for start_time, end_time in user_availability
        if is_future_date(start_time)
    ]

    formatted_availability = [
        {
            "start_time": to_iso8601(start_time),
            "end_time": to_iso8601(end_time)
        } for start_time, end_time in future_availability
    ]
    return jsonify({"availability": formatted_availability}), 200


# Endpoint to find overlap between logged_in and another user
@app.route('/overlap/<user_id_2>', methods=['GET'])
def find_overlap(user_id_2):
    user_id_1 = 'user123' #assuming this is coming from session
    # user_id_2 = data['user_id_2']

    availability_1 = availability_db.get(user_id_1, [])
    availability_2 = availability_db.get(user_id_2, [])

    # Find overlap using sorted intervals
    overlap_intervals = get_overlap(availability_1, availability_2)

    # Format the response
    overlap = [
        {
            "start_time": to_iso8601(start_time),
            "end_time": to_iso8601(end_time)
        } for start_time, end_time in overlap_intervals
    ]

    return jsonify({"overlap": overlap}), 200


@app.route('/availability', methods=['DELETE'])
def update_availability():
    data = request.json
    user_id = 'user123' # logged in user

    start_time = parse_iso8601(data['start_time'])
    end_time = parse_iso8601(data['end_time'])

    if start_time is None or end_time is None:
        return jsonify({"error": "Timestamps must be in UTC format (e.g., '2024-09-27T09:00:00Z')."}), 400

    if user_id not in availability_db or (start_time, end_time) not in availability_db[user_id]:
        return jsonify({"error": "Old slot not found in availability."}), 404

    # Remove the old slot
    availability_db[user_id].remove((start_time, end_time))

    # Sort the intervals for efficient overlap calculations
    availability_db[user_id].sort()
    return jsonify({"message": "Availability slot deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
