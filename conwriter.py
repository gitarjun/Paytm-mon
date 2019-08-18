from sys import stdout
from threading import Thread
import time

class conprint(Thread):
    def __init__(self,space=80,speed=1):
        Thread.__init__(self)
        self.statement = None
        self.string = space
        self.running = True
        self._counter = 0
        self.speed = speed
        self.pattern = ['[-]','[\\]','[/]']
        self.start()

    def run(self):
        while self.running:
            time.sleep(1/self.speed)
            if self.statement is None:
                continue
            cur_blk = self.pattern[self._counter % 3]
            rem_space = self.string - len(self.statement) - 4
            pnt_count = self._counter % rem_space
            pnts = eval("\"{:<%d}\".format('-'*pnt_count+'>')" % rem_space)
            stdout.write("\r{}{}{}".format(self.statement, pnts, cur_blk))
            stdout.flush()
            self._counter += 1

    def con_write(self,string):
        self.statement = string

    def terminate(self):
        self.running = False

    def reset_curser(self):
        self._counter=0


def main():
    print(123)
    d = conprint(speed=2)
    print(123)
    d.con_write('Hai')
    time.sleep(5)
    d.con_write("Hello")
    time.sleep(5)
    d.con_write("Delhi | DEL/HUB-Delhi | In transit from DEL/HUB (881)")
    time.sleep(5)
    d.terminate()
    print(123)

if __name__ == '__main__':
    main()