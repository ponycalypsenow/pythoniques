class Dataset(object):
    def __init__(self, X, y):
        self.X = X
        self.y = y


class Tree(object):
    def __init__(self, params):
        self.params = params
        self.nodes = [None]*(2**(params['max_depth'] + 1) - 1)

    def build(self, instances, grad, shrinkage_rate, depth=0, id=0):
        def split_gain(G, H, G_l, H_l):
            def calc_term(g, h):
                return np.square(g)/(h + 1.)
            return calc_term(G_l, H_l) + calc_term(G - G_l, H - H_l) - calc_term(G, H)

        def leaf_weight(grad):
            return np.sum(grad)/(2*len(grad) + 1.)

        self.nodes[id] = {}
        if depth >= self.params['max_depth']:
            self.nodes[id]['weight'] = leaf_weight(grad)*shrinkage_rate
            return
        G, H = np.sum(grad), 2*len(grad)
        best_gain, best_feature_id, best_value, best_left_instance_ids, best_right_instance_ids = 0., None, 0., None, None
        for feature_id in range(instances.shape[1]):
            G_l, H_l = 0., 0.
            sorted_instance_ids = instances[:, feature_id].argsort()
            for j in range(sorted_instance_ids.shape[0]):
                G_l, H_l = G_l + grad[sorted_instance_ids[j]], H_l + 2
                current_gain = split_gain(G, H, G_l, H_l)
                if current_gain > best_gain:
                    best_gain, best_feature_id, best_value, best_left_instance_ids, best_right_instance_ids = current_gain, feature_id, instances[
                        sorted_instance_ids[j]][feature_id], sorted_instance_ids[:j+1], sorted_instance_ids[j+1:]
        if best_gain < self.params['min_split_gain']:
            self.nodes[id]['weight'] = leaf_weight(grad)*shrinkage_rate
        else:
            self.nodes[id]['split_feature_id'], self.nodes[id]['split_value'] = best_feature_id, best_value
            self.build(instances[best_left_instance_ids], grad[best_left_instance_ids], shrinkage_rate, depth + 1, 2*id + 1)
            self.build(instances[best_right_instance_ids], grad[best_right_instance_ids], shrinkage_rate, depth + 1, 2*id + 2)
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
                       'max_depth': 4, 'learning_rate': 0.7} | params
        self.models = []

    def train(self, train_set, num_boost_round=20, eval_set=None, early_stopping_rounds=5):
        def forward(X):
            if len(self.models) == 0:
                return None
            return np.array([self.predict(X[i]) for i in range(len(X))])

        def gradient(y, predictions):
            if predictions is None:
                return np.random.uniform(size=len(y))
            return np.array([2*(y[i] - predictions[i]) for i in range(len(y))])

        def loss(X, y):
            errors = [y - self.predict(x) for x, y in zip(X, y)]
            return np.mean(np.square(errors))

        best_eval_loss = np.iinfo(np.int64).max
        best_round = None
        for round in range(num_boost_round):
            iter_start_time = time.time()
            grad = gradient(train_set.y, forward(train_set.X))
            self.models.append(Tree(self.params).build(train_set.X, grad, self.params['learning_rate']**round))
            train_loss = loss(train_set.X, train_set.y)
            eval_loss = loss(eval_set.X, eval_set.y) if eval_set else None
            print("Round {:>3}, Train's L2: {:.10f}, Eval's L2: {}, Elapsed: {:.2f} secs".format(
                round, train_loss, '{:.10f}'.format(eval_loss) if eval_loss else '-', time.time() - iter_start_time))
            if eval_loss is not None and eval_loss < best_eval_loss:
                best_eval_loss, best_round = eval_loss, round
            if round - best_round >= early_stopping_rounds:
                break

        self.models = self.models if best_round is None else self.models[:best_round]

    def predict(self, x):
        return np.sum([m.predict(x) for m in self.models])
