
class DistanceList:
    def __init__(self):
        self.measurements = []
        self.filtered = []
        self.result: float | None = None
        self.median_filter_size = 5
        self.required_measurements = 10
        self.max_measurements = 30
        self.cache_valid = False
        self.cached_value = 0

    def add(self, value):
        self.measurements.append(value)
        if len(self.measurements) > self.max_measurements:
            self.measurements.pop(0)
        self.cache_valid = False

    def get_value(self):
        if self.cache_valid:
            return self.cached_value

        if len(self.measurements) < self.required_measurements:
            return None

        def median(seq):
            if len(seq) % 2 == 1:
                return seq[len(seq) // 2]
            return (seq[len(seq) // 2 - 1] + seq[len(seq) // 2]) / 2

        def quantile(seq, q):
            assert 0 <= q <= 1
            index = int(len(seq) * q)
            return seq[index]

        def iqr_mean(seq):
            lo = int(len(seq) * 0.15)
            hi = int(len(seq) * 0.45)
            return sum(seq[lo:hi]) / (hi - lo)

        half_size = self.median_filter_size // 2
        if half_size % 2 == 0:
            half_size += 1
        self.filtered = [median(self.measurements[i-half_size : i+half_size])
                         for i in range(half_size, len(self.measurements) - half_size)]

        self.cached_value = sum(self.filtered) / len(self.filtered)
        # self.cached_value = iqr_mean(self.filtered)
        self.cache_valid = True
        return self.cached_value