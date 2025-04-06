import time
import os
import json
import math

def ai_predict_timings():
    with open("live_counts.txt",'r') as file:
        current=file.read()

    car = ""
    for i in range(0,3):
        if current[current.find("Car: ")+5+i].isnumeric():
            car += str(current[current.find("Car: ")+5+i])
    car = int(car)
# print(car)

    Motorcycle = ""
    for i in range(0,3):
        if current[current.find("Motorcycle: ")+12+i].isnumeric():
            Motorcycle += str(current[current.find("Motorcycle: ")+12+i])
    Motorcycle = int(Motorcycle)
# print(Motorcycle)


    axletruck=''

    axletruck = ""
    for i in range(0,3):
        if current[current.find("4-axle-truck: ")+14+i].isnumeric():
            axletruck += str(current[current.find("4-axle-truck: ")+14+i])
    axletruck = int(axletruck)
# print(axletruck)

    congestion = 4*car + 8*axletruck + 2*Motorcycle

    green_time = int(4*(congestion)**0.5)
    
    return  green_time


directions = ['N', 'S', 'E', 'W']
current_green = ai_predict_timings()  # Initial AI prediction
override_end = 0

while True:
    # Check for override file
    if os.path.exists('override.json'):
        try:
            with open('override.json') as f:
                data = json.load(f)
                current_green = data['time']
                override_end = time.time() + data['duration']
                os.remove('override.json')
                print(f"Manual override: {current_green}s green time for {data['duration']/60} minutes")
        except:
            pass
    
    # Check if override expired
    if time.time() > override_end:
        # Revert to AI predictions
        current_green = ai_predict_timings()
    
    # Run traffic sequence
    for direction in directions:
        print(f"\n{direction} GREEN - Others RED ({current_green}s")
        time.sleep(current_green)
        