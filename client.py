class VolcanoOperator:
    def open(self):
        pass
    def next(self):
        return None
    def close(self):
        pass

class SeqScanOperator(VolcanoOperator):
    def __init__(self, table_data, predicate=None):
        self.table_data = table_data
        self.predicate = predicate
        self.cursor = 0

    def open(self):
        self.cursor = 0

    def next(self):
        while self.cursor < len(self.table_data):
            row = self.table_data[self.cursor]
            self.cursor += 1
            if self.predicate is None or self.predicate(row):
                return row
        return None

    def close(self):
        self.cursor = len(self.table_data)

class HashJoinOperator(VolcanoOperator):
    def __init__(self, left_child, right_child, left_key, right_key):
        self.left_child = left_child
        self.right_child = right_child
        self.left_key = left_key
        self.right_key = right_key
        self.hash_table = {}
        self.current_matches = []
        self.probe_row = None

    def open(self):
        self.left_child.open()
        self.right_child.open()
        self.hash_table = {}
        while True:
            row = self.left_child.next()
            if row is None:
                break
            k = row.get(self.left_key)
            if k not in self.hash_table:
                self.hash_table[k] = []
            self.hash_table[k].append(row)
        self.current_matches = []
        self.probe_row = None

    def next(self):
        while True:
            if self.current_matches:
                match_left = self.current_matches.pop(0)
                joined = dict(match_left)
                joined.update(self.probe_row)
                return joined

            self.probe_row = self.right_child.next()
            if self.probe_row is None:
                return None
            k = self.probe_row.get(self.right_key)
            if k in self.hash_table:
                self.current_matches = list(self.hash_table[k])

    def close(self):
        self.left_child.close()
        self.right_child.close()
        self.hash_table = {}
        self.current_matches = []

class SortAggregateOperator(VolcanoOperator):
    def __init__(self, child, group_by_col, agg_col, agg_fn='SUM'):
        self.child = child
        self.group_by_col = group_by_col
        self.agg_col = agg_col
        self.agg_fn = agg_fn
        self.aggregated_rows = []
        self.cursor = 0

    def open(self):
        self.child.open()
        buckets = {}
        while True:
            row = self.child.next()
            if row is None:
                break
            g = row[self.group_by_col]
            v = row[self.agg_col]
            if g not in buckets:
                buckets[g] = []
            buckets[g].append(v)

        self.aggregated_rows = []
        for g in sorted(buckets.keys()):
            vals = buckets[g]
            if self.agg_fn == 'SUM':
                res = sum(vals)
            elif self.agg_fn == 'COUNT':
                res = len(vals)
            elif self.agg_fn == 'AVG':
                res = sum(vals) / len(vals)
            else:
                res = sum(vals)
            self.aggregated_rows.append({self.group_by_col: g, f"{self.agg_fn}_{self.agg_col}": res})
        self.cursor = 0

    def next(self):
        if self.cursor < len(self.aggregated_rows):
            r = self.aggregated_rows[self.cursor]
            self.cursor += 1
            return r
        return None

    def close(self):
        self.child.close()
        self.cursor = len(self.aggregated_rows)
