import random
from time import sleep


class Result(BaseException):
    def __init__(self, result):
        self.result = result


def illustrated(fn):
    def wrapper(self):
        result = fn(self)
        self.print_lights()
        return result
    return wrapper


class Train():
    def __init__(self):
        self.__cars_count = random.randint(1, 80)
        self.__last_car = self.__cars_count - 1
        self.__current_car = 0
        self.__lights = [random.randint(0, 1) for _ in range(self.__cars_count)]
        self.__steps = 0
        self.__verbose = True
        self.__full_cycle_time = 1
        self.__step_pause = self.__full_cycle_time / self.__cars_count

    def print_lights(self):
        print(''.join(map(str, self.__lights)))
        spaces_before = self.__current_car - 1
        print('%s%s' % (' ' * spaces_before, '^'))
        sleep(self.__step_pause)

    @property
    def light_is_on(self):
        return self.__lights[self.__current_car] == 1

    def run(self):
        try:
            self.what_to_do()
        except Result as r:
            self.__analyze_result(r.result)

    def what_to_do(self):
        raise NotImplemented

    @illustrated
    def move_next(self):
        return self.__move()

    @illustrated
    def move_prev(self):
        return self.__move(-1)

    @illustrated
    def turn_light_on(self):
        return self.__turn_light(1)

    @illustrated
    def turn_light_off(self):
        return self.__turn_light(0)

    def __analyze_result(self, result):
        if result == self.__cars_count:
            print("Correct! %d cars!" % result)
        else:
            print("Sorry, you said %d, but there are %d cars!" % (result, self.__cars_count))

        print("You've made %d steps (inside a train with %d cars)" % (self.__steps, self.__cars_count))

    def __move(self, direction=1):

        self.__steps += 1

        if self.__current_car == 0 and direction == -1:
            self.__current_car = self.__cars_count - 1
        elif self.__current_car == self.__last_car and direction == 1:
            self.__current_car = 0
        else:
            self.__current_car += direction

    def __turn_light(self, state=1):
        self.__lights[self.__current_car] = state


class MyStupidTrain(Train):
    def what_to_do(self):
        print("Running around...")
        for _ in range(1000):
            self.turn_light_off()
            self.move_next()
        print("Hinting...")
        self.turn_light_on()
        print('Yahoo!')
        c = 1
        while not self.light_is_on or c == 1:
            self.move_next()
            c += 1

        raise Result(c)


class MyCleveTrain(Train):

    def what_to_do(self):

        self.turn_light_on()

        while True:
            distance = 0
            while not self.light_is_on or distance == 0:
                distance += 1
                self.move_next()

            self.turn_light_off()

            r_distance = distance

            while r_distance != 0:
                r_distance -= 1
                self.move_prev()

            if self.light_is_on:
                continue

            raise Result(distance)

if __name__ == '__main__':
    train = MyCleveTrain()
    train.run()
