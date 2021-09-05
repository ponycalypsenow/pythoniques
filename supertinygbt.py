import numpy as np
import time


class Tree(object):
    def __init__(self, params):
        self.params = params
        self.nodes = [None]*(2**(params['max_depth'] + 1) - 1)

    def build(self, samples, grad, shrinkage_rate, depth=0, id=0):
        def split_gain(G, H, G_l, H_l):
            def calc_term(g, h):
                return np.square(g)/(h + 1.)
            return calc_term(G_l, H_l) + calc_term(G - G_l, H - H_l) - calc_term(G, H)

        def leaf_weight(g):
            return np.sum(g)/(2*len(g) + 1.)

        self.nodes[id] = {}
        if depth >= self.params['max_depth']:
            self.nodes[id]['weight'] = leaf_weight(grad)*shrinkage_rate
            return
        G, H = np.sum(grad), 2*len(grad)
        best_gain, best_feature_id, best_value, best_left_sample_ids, best_right_sample_ids = 0., None, 0., None, None
        for feature_id in range(samples.shape[1]):
            G_l, H_l = 0., 0.
            sorted_sample_ids = samples[:, feature_id].argsort()
            for j in range(sorted_sample_ids.shape[0]):
                G_l, H_l = G_l + grad[sorted_sample_ids[j]], H_l + 2
                current_gain = split_gain(G, H, G_l, H_l)
                if current_gain > best_gain:
                    best_gain, best_feature_id, best_value, best_left_sample_ids, best_right_sample_ids = current_gain, feature_id, samples[
                        sorted_sample_ids[j]][feature_id], sorted_sample_ids[:j+1], sorted_sample_ids[j+1:]
        if best_gain < self.params['min_split_gain']:
            self.nodes[id]['weight'] = leaf_weight(grad)*shrinkage_rate
        else:
            self.nodes[id]['split_feature_id'], self.nodes[id]['split_value'] = best_feature_id, best_value
            self.build(samples[best_left_sample_ids], grad[best_left_sample_ids], shrinkage_rate, depth + 1, 2*id + 1)
            self.build(samples[best_right_sample_ids], grad[best_right_sample_ids], shrinkage_rate, depth + 1, 2*id + 2)
        return self

    def predict(self, x, id=0):
        if 2*id + 1 >= len(self.nodes) or self.nodes[2*id + 1] is None or self.nodes[2*id + 2] is None:
            return self.nodes[id]['weight']
        else:
            if x[self.nodes[id]['split_feature_id']] <= self.nodes[id]['split_value']:
                return self.predict(x, 2*id + 1)
            else:
                return self.predict(x, 2*id + 2)


class GBT(object):
    def __init__(self, params={}):
        self.params = {'min_split_gain': 0.1,
                       'max_depth': 4,
                       'learning_rate': 0.3} | params
        self.trees = []

    def train(self, X, y, num_boost_round=20, eval_set=None, early_stopping_rounds=5):
        def forward(X):
            if len(self.trees) == 0:
                return None
            return np.array([self.predict(X[i]) for i in range(len(X))])

        def gradient(y, predictions):
            if predictions is None:
                return np.random.uniform(np.min(y), np.max(y), len(y))
            return np.array([2*(y[i] - predictions[i]) for i in range(len(y))])

        def loss(X, y):
            errors = [y - self.predict(x) for x, y in zip(X, y)]
            return np.mean(np.square(errors))

        best_eval_loss = np.iinfo(np.int64).max
        best_round = None
        for round in range(num_boost_round):
            round_start_time = time.time()
            grad = gradient(y, forward(X))
            self.trees.append(Tree(self.params).build(X, grad, self.params['learning_rate'] if round > 0 else 1))
            train_loss = loss(X, y)
            eval_loss = loss(eval_set[0], eval_set[1]) if eval_set else None
            print("Round {:>3}, Train's L2: {:.10f}, Eval's L2: {}, Elapsed: {:.2f} secs".format(
                round, train_loss, '{:.10f}'.format(eval_loss) if eval_loss else '-', time.time() - round_start_time))
            if eval_loss is not None and eval_loss < best_eval_loss:
                best_eval_loss, best_round = eval_loss, round
            if round - best_round >= early_stopping_rounds:
                break

        self.trees = self.trees if best_round is None else self.trees[:best_round]

    def predict(self, x):
        return np.sum([t.predict(x) for t in self.trees])
