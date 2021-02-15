import numpy as np
import urllib.request as request
import matplotlib.pyplot as plt

def getWindow(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def getAutoCorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size/2:]

def getInstrument(name):
    with request.urlopen('https://stooq.pl/q/?s={}'.format(name)) as res:
        cookies = res.info().get_all('Set-Cookie')
        req = request.Request('https://stooq.pl/q/d/l/?s={}&i=d'.format(name))
        for c in cookies:
            req.add_header('Cookie', c)
        
        with request.urlopen(req) as res:
            data = [l.split(',') for l in res.read().decode('utf-8').split('\r\n')]
            data = [l for l in data if len(l) == len(data[0])][1:]
            data = [tuple(str(k) if i == 0 else float(k) for i, k in enumerate(l)) for l in data]
            return np.array(data, dtype=[('date','<U255'), ('o', np.float), ('l', np.float), ('h', np.float), ('c', np.float)])

class Technical:
    ticks = np.array([])
    prices = np.array([])

    def __init__(self, instrument, beginingDate = None, endDate = None):
        self.ticks = instrument if beginingDate is None else instrument[instrument['date'] >= beginingDate]
        self.ticks = self.ticks if endDate is None else self.ticks[self.ticks['date'] <= endDate]
        self.prices = self.ticks['c']
        self.tops = self.getTops()

    def getWindow(self, i, size = 26):
        return self.prices[max(i, 0):min(i + size, len(self.prices))]

    def getTops(self, size = 26):
        def calculateRs(tops):
            for (i, t) in enumerate(tops):
                if i > 0:
                    tops[i - 1]['length'] = t['index'] - tops[i - 1]['index']
                    tops[i - 1]['change'] = t['price'] / tops[i - 1]['price']
                    tops[i - 1]['r'] = np.power(tops[i - 1]['change'], 1 / (tops[i - 1]['length'] + 1)) - 1
            tops[-1]['length'] = len(self.prices) - tops[-1]['index']
            tops[-1]['change'] = self.prices[-1] / tops[-1]['price']
            tops[-1]['r'] = np.power(tops[-1]['change'], 1 / (tops[-1]['length'] + 1)) - 1
            return tops
        
        filterUnique = lambda tops: [t for t in tops if np.where(t['price'] == self.prices)[0][0] == t['index']]
        filterLast = lambda tops: [t for (i, t) in enumerate(tops) if i + 1 < len(tops) and t['type'] != tops[i + 1]['type']]
        tops = []
        for i in range(len(self.prices)):
            w = self.getWindow(i - size, size + 1)
            p, wmax, wmin = self.prices[i], max(w), min(w)
            if self.prices[i] == wmax or self.prices[i] == wmin:
                tops.append({ 'date': self.ticks[i][0], 'type': 'top' if p == wmax else 'bottom', 'price': p, 'index': i })
        return calculateRs(filterLast(filterUnique(tops)))

    def getTop(self, i):
        if i < self.tops[0]['index']:
            return self.tops[0]
        if i >= self.tops[-1]['index']:
            return self.tops[-1]
        return [t for t in self.tops if t['index'] <= i][-1]

    def predictByTops(self, i):
        def predict(t, i):
            return t['price'] * np.power(t['r'] + 1, i - t['index'] + 1)
        return predict(self.getTop(i), i)

t = Technical(getInstrument('xagusd'), '2008-01-01')
plt.plot(range(len(t.prices)), t.prices)
plt.plot(range(len(t.prices)), [t.predictByTops(i) for i in range(len(t.prices))])
plt.fill_between(range(len(t.prices)), 0, max(t.prices), where=[t.getTop(i)['type'] == 'bottom' for i in range(len(t.prices))], alpha=0.125)
plt.tight_layout(pad = 1)
plt.show()
