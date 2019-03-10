import numpy as np
import sqlalchemy
from sqlalchemy import text
from sqlalchemy import create_engine
# -1 -> empty grid
# 0 -> spot empty
# 1 -> occupied
# 2 -> road
# 3 -> wall
# 4 -> Enter
# 5 -> Exit
# 6 -> not available

engine = None

DEFAULT_PATH = "grid"
POINTS = 50

class DB:

    def __init__(self, parking_file_path=""):
        global engine
        engine = create_engine("postgresql:///parking")
        try:
            if parking_file_path == "":
                parking_file_path = DEFAULT_PATH
            self.parking_file_path = parking_file_path
            self.parking_grid = np.load(parking_file_path)
        except:
            print("No file found.")
            self.create_grid(10, 10)
        self.grid_to_num = {}
        self.parking_num_to_grid_num = {}
        num = 1
        for i in range(self.parking_grid.shape[0]):
            for j in range(self.parking_grid.shape[1]):
                if(self.parking_grid[i][j] == 0 or self.parking_grid[i][j] == 1):
                    self.parking_num_to_grid_num[num] = (i, j)
                    self.grid_to_num[(i,j)] = num
                    num += 1

        self.car_num_to_parking_num = {}
        self.parking_num_to_car_num = {}
        
        self.car_num_serial = {}


    def get_car_num_to_parking_num(self):
        return self.car_num_to_parking_num

    def get_parking_num_to_car_num(self):
        return self.parking_num_to_car_num

    def get_num_by_grid(self, i ,j):
        return self.grid_to_num[(i, j)]

    def check_spot(i,j):
        if self.parking_grid[i][j]==0:
            return True
        return False

    def book_parking_spot(self, num, car_num):
        # grid num change
        # add this to parking_num_to_car_num
        i, j = self.parking_num_to_grid_num[num]
        self.parking_grid[i][j] = 1
        self.save_grid()
        self.parking_num_to_car_num[num] = car_num
        self.car_num_to_parking_num[car_num] = num


    def free_parking_spot(self, num):
        i, j = self.parking_num_to_grid_num[num]
        self.parking_grid[i][j] = 0
        self.save_grid()
        car_num = self.parking_num_to_car_num[num]
        self.set_user_out_time(car_num)
        self.car_num_to_parking_num.pop(car_num, None)
        self.parking_num_to_car_num.pop(num, None)
        

    def car_at_parking_spot(self, car_num):
        return self.car_num_to_parking_num[car_num]

    def mark_road(self, i, j):        
        self.parking_grid[i][j] = 2
        self.save_grid()

    def mark_enter(self, i, j):
        self.parking_grid[i][j] = 4
        self.save_grid()

    def mark_exit(self, i, j):
        self.parking_grid[i][j] = 5
        self.save_grid()

    def mark_wall(self, i, j):
        self.parking_grid[i][j] = 3
        self.save_grid()

    def mark_not_available(self, i, j):
        self.parking_grid[i][j] = 6
        self.save_grid()

    def mark_parkable(self, i, j):
        self.parking_grid[i][j] = 0

    def save_grid(self):
        np.save(self.parking_file_path, self.parking_grid)

    def create_grid(self, numRows, numCols):
        self.parking_grid = np.full((numRows, numCols), 0)
        self.save_grid()

    def get_grid(self):
        return self.parking_grid

    def get_grid_val(self, i ,j):
        return self.parking_grid[i][j]

    def get_cars_in_parking(self):
        return set(self.car_num_to_parking_num.keys())

    # user stats
    def enter_user(self, car_num):
        with engine.begin() as connection:
            result = connection.execute(text("""INSERT INTO user_stats (car_num, points_available) values(:car_num, :points) RETURNING id"""), {'car_num': car_num, 'points': POINTS})
            self.car_num_serial[car_num] = result.fetchone()[0]
    
    def get_user_info(self, car_num):
        with engine.begin() as connection:
            result = connection.execute(text("""SELECT * FROM user_stats WHERE car_num = :car_num"""), {'car_num': car_num})
            l = []
            for r in result:
                l.append(r)
                print(r[1], r[3].strftime("%Y-%m-%d %H:%M:%S"), r[4].strftime("%Y-%m-%d %H:%M:%S"))
        return l

    def set_user_out_time(self, car_num):
        with engine.begin() as connection:
            connection.execute(text("""UPDATE user_stats SET out_time = now() WHERE id = :id"""), {'id':self.car_num_serial[car_num]})
            result = connection.execute(text("""SELECT points_available from user_stats where car_num = :car_num ORDER BY id LIMIT 1"""), {'car_num': car_num})
            pt = result.fetchone()[0]
            connection.execute(text("""UPDATE user_stats SET points_available = :pt WHERE car_num = :car_num"""), {'car_num': car_num, 'pt': pt-5})

    def get_user_points(self, car_num):
        with engine.begin() as connection:
            result = connection.execute(text("""SELECT points_available from user_stats where car_num = :car_num ORDER BY id LIMIT 1"""), {'car_num': car_num})
            pt = result.fetchone()[0]
            return pt
            
    def reset_db(self):
        with engine.begin() as connection:
            connection.execute(text("""TRUNCATE table user_stats"""))
