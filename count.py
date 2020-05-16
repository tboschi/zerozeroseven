import time
def down(tot, dt = 1):
    """3 2 1 countdown from tot seconds"""
    snap = time.time()
    end  = snap + tot * dt
    ticks = [end - t * dt for t in range(tot)]
    while time.time() < end:
        now = time.time()
        if now > snap:
            while ticks and now > snap:
                snap = ticks.pop()
            yield len(ticks) + 1
        else:
            yield None


def up(tot, dt = 1):
    """1 2 3 countup to tot seconds"""
    snap = time.time()
    end  = snap + tot * dt
    ticks = [end - t * dt for t in range(tot)]
    while time.time() < end:
        now = time.time()
        if now > snap:
            while ticks and now > snap:
                snap = ticks.pop()
            yield tot - len(ticks) - 1
        else:
            yield None



if __name__ == "__main__":
    import sys

    cc = down(10, dt=1)
    while True:
        try:
            tt = next(cc)
        except StopIteration:
            print("end")
            break
        else:
            if tt is not None:
                print(tt)
        time.sleep(float(sys.argv[1]))
