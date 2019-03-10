# Parking Automation and Management system

Parking lots generally have congestion problems as human vendors give receipts, in addition to 

the problem of finding your car after it has been parked for a long time. SO we present an 

platform which requires no human intervention. As a car enters the parking lot, our interface 

will recognize the plate number and give a slot number, as per availability. 

Upon exit, the parking admin can view user stats such as entry and exit time for the 

corresponding car number.

# Installation guide

## Dependencies

* postgresSQL

* opencv > 3.4 (for dnn.readNet function)

* tesseract

* python3

* flask

* numpy


* Download pre trained neural network weights from [here]('https://www.dropbox.com/s/r2ingd0l3zt8hxs/frozen_east_text_detection.tar.gz?dl=1')

To run first create table in psql

```
create table user_stats(id serial, car_num text, points_available integer, in_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(), out_time TIMESTAMP WITH TIME ZONE DEFAULT NOW());

```

clients run ```python3 camera.py```

this runs the webcam of the client to detect and read text in front of it.

server run ```python3 __init__.py```

this runs a flask server which gets data from clients and allot parking slots to the clients

and upon exit stores user stats and removes that from the parking slot.
