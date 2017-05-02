class Timer:
    def __init__(self, h=0, m=0, s=0, seconds=None):
        self.h = h
        self.m = m
        self.s = self.tot_sec = s
        if seconds:
            self.add(seconds)

    def add(self, secs):
        self.tot_sec += secs
        self.s += secs
        if self.s >= 60:
            self.m += self.s // 60
            self.s %= 60
            if self.m >= 60:
                self.h += self.m // 60
                self.m %= 60

    def to_seconds(self):
        return self.tot_sec

    def __int__(self):
        return self.tot_sec

    def __add__(self, other):
        if type(other) is int:
            self.add(other)
        elif type(other) is Timer:
            self.add(other.to_seconds())
        else:
            raise TypeError
        return self

    def __str__(self):
        return "%02d:%02d:%02d" % (self.h, self.m, self.s)
