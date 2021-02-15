const fs = require('fs');
const btcusd = require('./cdr_d.json');

const random = (high = 1, low = 0) => (high - low) * Math.random() + low;
const clamp = (x, high = 1, low = 0) => Math.max(Math.min(x, high), low);
const array = n => Array.from({ length: n });
const reshape = (a, rows, cols) => array(rows).map((_, row) => array(cols).map((_, col) => a[row * cols + col]));
const sum = l => l.reduce((ret, _, i) => ret + l[i], 0);
const dot = (l, r) => l.reduce((ret, _, i) => ret + l[i] * r[i], 0);

class Creators {
    static real(n, high = 4.0, low = -4.0) {
        return () => array(n).map(_ => random(high, low));
    }
}

class Mutators {
    static real(high = 4.0, low = -4.0, gamma = 0.01) {
        const r = Math.abs(high - low) * gamma;
        return g => g.map(x => clamp(x, high, low));
    }
}

class Loss {
    static crossentropy(y, p) {
        return -p.reduce((ret, _, i) => ret + y[i] * Math.log(p[i]), 0);
    }

    static mse(y, p) {
        return p.reduce((ret, _, i) => ret + Math.pow(y[i] - p[i], 2), 0);
    }
}

class Optimizer {
    // pool = [];
    // errors = [];

    setCreator(creator, poolSize = 30) {
        this.creator = creator;
        this.pool = array(poolSize).map(_ => creator());
        return this;
    }

    setMutator(mutator) {
        this.mutator = mutator;
        return this;
    }

    setEvaluator(evaluator) {
        this.evaluator = evaluator;
        this.errors = this.pool.map(g => evaluator(g));
        return this;
    }

    evolve(maxGenerations = 3000, crossoverRatio = 0.9, mutationRatio = 0.3) {
        const getWorst = () => this.errors.indexOf(Math.max(...this.errors));
        const getBest = () => this.errors.indexOf(Math.min(...this.errors));
        const getRandom = () => Math.floor(random() * this.pool.length);
        for (let i = 0; i < maxGenerations; i++) {
            let candidate = this.creator();
            for (let j = 0; j < candidate.length; j++) {
                if (random() < crossoverRatio) {
                    candidate[j] = this.pool[getRandom()][j];
                    if (random() < mutationRatio) {
                        candidate[j] = this.mutator(candidate)[j];
                    }
                }
            }

            const candidateError = this.evaluator(candidate);
            const worstIndex = getWorst();
            if (this.errors[worstIndex] > candidateError) {
                [this.pool[worstIndex], this.errors[worstIndex]] = [candidate, candidateError];
            }
        }

        return this.pool[getBest()];
    }
}

class Layers {
    static linear(inTotal, outTotal, bias = true, seedWeights = null) {
        const weights = seedWeights ? seedWeights : array(outTotal).map(() => Creators.real(inTotal + (bias ? 1 : 0))());
        const forward = input => array(outTotal).map((_, i) => dot(input, weights[i]) + (bias ? weights[i][inTotal] : 0));
        const totalWeights = sum(weights.flatMap(w => w.length));
        return { bias, weights, inTotal, outTotal, totalWeights, forward };
    }

    static relu() {
        return { forward: input => input.map(x => Math.max(x, 0)) };
    }

    static sigmoid() {
        return { forward: input => input.map(x => 1.0 / (1.0 + Math.exp(-x))) };
    }

    static tanh() {
        return { forward: input => input.map(x => (Math.exp(x) - Math.exp(-x)) / (Math.exp(x) + Math.exp(-x))) };
    }

    static softmax() {
        return { forward: input => input.map(x => Math.exp(x) / sum(input.map(y => Math.exp(y)))) };
    }
}

class Network {
    // weightsTotal = 0;
    // layers = [];

    setLayers(...layers) {
        this.layers = [...layers];
        this.weightsTotal = sum(layers.filter(w => w.weights).map(l => sum(l.weights.map(w => w.length))));
        return this;
    }

    setEvaluator(evaluator) {
        this.evaluator = evaluator;
        return this;
    }

    forward(input) {
        return this.layers.reduce((output, l) => l.forward(output), input);
    }

    getClone(genotype) {
        let weightsIndex = 0;
        return new Network().setLayers(...this.layers.map(l => {
            if (!l.weights) {
                return l;
            } else {
                const genotypeWindow = genotype.slice(weightsIndex, weightsIndex + l.totalWeights);
                const seedWeights = reshape(genotypeWindow, l.weights.length, l.weights[0].length);
                weightsIndex += l.totalWeights;
                return Layers.linear(l.inTotal, l.outTotal, l.bias, seedWeights);
            }
        })).setEvaluator(this.evaluator);
    }

    evolve(maxGenerations = 3000) {
        let o = new Optimizer();
        o.setCreator(Creators.real(this.weightsTotal));
        o.setMutator(Mutators.real());
        o.setEvaluator(g => this.evaluator(this.getClone(g)));
        this.layers = this.getClone(o.evolve(maxGenerations)).layers;
        this.errorTotal = this.evaluator(this);
        return this;
    }
}

class Technical {
    // ticks = [];
    // prices = [];
    // tops = [];

    constructor(instrument, beginningDate = null, endingDate = null) {
        this.ticks = instrument.filter(t => beginningDate == null || t.Date >= beginningDate);
        this.ticks = this.ticks.filter(t => endingDate == null || t.Date <= endingDate)
        this.prices = this.ticks.map(t => t.Close);
        this.tops = this.getTops();
    }

    getWindow(i, size = 26) {
        return this.prices.slice(Math.max(i, 0), Math.min(i + size, this.prices.length));
    }

    getTops(size = 26) {
        const isUnique = t => this.prices.indexOf(t.price) == t.index;
        const isLast = (t, i, all) => all[i + 1]?.type != t.type;
        const filterUnique = t => t.filter(isUnique).filter(isLast);
        const calculateRs = t => t.reduce((ret, t, i, all) => {
            if (i > 0) {
                all[i - 1].length = t.index - all[i - 1].index;
                all[i - 1].change = t.price / all[i - 1].price;
                all[i - 1].r = Math.pow(all[i - 1].change, 1 / (all[i - 1].length + 1)) - 1;
            }

            return [...ret, t];
        }, []);
        let tops = [];
        for (let i = 0; i < this.prices.length; i++) {
            const window = [...this.getWindow(i - size, size + 1)];
            const [max, min] = [Math.max(...window), Math.min(...window)];
            if (this.prices[i] == max || this.prices[i] == min) {
                tops = [...tops, { date: this.ticks[i].Date, type: this.prices[i] == max ? 'top' : 'bottom', price: this.prices[i], index: i, mid: parseFloat(Math.sqrt(max * min).toFixed(2)) }];
            }
        }

        return calculateRs(filterUnique(tops))
    }

    predictUsingTops(i) {
        const predict = (t, i) => t.price * Math.pow(t.r + 1, i - t.index + 1);
        const predictions = this.tops.filter(t => t.index < i).map(t => t.price);
        return predictions;
    }
}

const t = new Technical(btcusd);
const tops = t.getTops();
console.log(tops);
console.log(tops[tops.length - 2]);
console.log(t.predictUsingTops(tops[tops.length - 2].index));