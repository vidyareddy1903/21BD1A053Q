from flask import Flask, jsonify, request
import requests
from collections import deque
import time

app = Flask(__name__)

WINDOW_SIZE = 10
TIMEOUT = 0.5
number_store = {
    'p': deque(maxlen=WINDOW_SIZE),
    'f': deque(maxlen=WINDOW_SIZE),
    'e': deque(maxlen=WINDOW_SIZE),
    'r': deque(maxlen=WINDOW_SIZE)
}

API_URLS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'r': 'http://20.244.56.144/test/rand'
}

def fetch_numbers(type_id):
    try:
        response = requests.get(API_URLS[type_id], timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data['numbers']
    except (requests.RequestException, ValueError):
        return []

def calculate_average(numbers):
    if numbers:
        return sum(numbers) / len(numbers)
    return 0.0

@app.route('/numbers/<type_id>', methods=['GET'])
def get_numbers(type_id):
    if type_id not in number_store:
        return jsonify({"error": "Invalid type ID"}), 400

    window_prev_state = list(number_store[type_id])
    fetched_numbers = fetch_numbers(type_id)
    
    # Add unique numbers to the store
    for num in fetched_numbers:
        if num not in number_store[type_id]:
            number_store[type_id].append(num)
            if len(number_store[type_id]) > WINDOW_SIZE:
                number_store[type_id].popleft()
    
    window_curr_state = list(number_store[type_id])
    average = calculate_average(window_curr_state)
    
    response = {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "numbers": fetched_numbers,
        "avg": round(average, 2)
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=9876)
