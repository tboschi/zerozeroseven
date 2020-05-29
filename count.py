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
            yield len(ticks) + 1, snap - now
        else:
            yield None, snap - now


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
            yield tot - len(ticks) - 1, snap - now
        else:
            yield None, snap - now



if __name__ == "__main__":
    import sys

    #cc = down(10, dt=1)
    cc = up(10, dt=0.5)
    while True:
        try:
            tt, now = next(cc)
        except StopIteration:
            print("end")
            break
        else:
            if tt is not None:
                print(now, ":", tt)
            else:
                print(now, ":")
        #time.sleep(float(sys.argv[1]))
        time.sleep(0.1)
