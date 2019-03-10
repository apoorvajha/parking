#!/usr/bin/env python3

# Main flask app

import db
from flask import Flask
from flask import render_template, request, render_template_string
DEBUG = True

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('temp.html')


@app.route("/get_text")
def get_text():
    pass


@app.route("/get_current_image")
def get_current_image():
    pass


@app.route("/reset_client")
def reset_client():
    pass


@app.route('/user', methods=['post', 'get'])
def user():
    stats = ''
    pts = ''
    parking_slot=''
    car_num = request.form.get('car_num')  # access the data inside 
    stats = database.get_user_info(car_num)
    st = ""
    if car_num:
        pts = database.get_user_points(car_num)
        parking_slot = database.car_at_parking_spot(car_num)
        print(pts)
    print(car_num)
    for l in stats:
        st += l[1]+'\t|\t'+str(l[3].strftime("%Y-%m-%d %H:%M:%S"))+'\t|\t'+str(l[4].strftime("%Y-%m-%d %H:%M:%S"))
    return render_template('user.html', message=st, pts=pts)

@app.route('/client', methods=['post', 'get'])
def client():
    car_num = request.form.get('car_num')
    client_type = request.form.get('type')
    parking_slots = database.get_car_num_to_parking_num()
    if client_type == '1':
        #enter
        #find empty spot and fill it
        if car_num not in parking_slots:
            grid = database.get_grid()
            f=0
            for i in range(grid.shape[0]):
                for j in range(grid.shape[1]):
                    if grid[i][j] == 0:
                        num = database.get_num_by_grid(i, j)
                        database.book_parking_spot(num, car_num)
                        database.enter_user(car_num)
                        f=1
                        break
                if f==1:
                    break
    else:
        #exit
        if car_num in parking_slots:
            num = database.car_at_parking_spot(car_num)
            database.free_parking_spot(num)
    print(database.get_parking_num_to_car_num())
    return render_template('user.html', pts=database.get_parking_num_to_car_num())


if __name__ == "__main__":
    global database
    database = db.DB()
    app.run(host= '0.0.0.0', debug=DEBUG)
