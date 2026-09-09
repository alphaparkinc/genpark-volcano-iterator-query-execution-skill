from client import SeqScanOperator, HashJoinOperator, SortAggregateOperator

def main():
    print("=== Testing Volcano Iterator Query Execution ===")
    orders = [
        {'order_id': 1, 'cust_id': 101, 'amount': 120},
        {'order_id': 2, 'cust_id': 102, 'amount': 250},
        {'order_id': 3, 'cust_id': 101, 'amount': 300},
    ]
    customers = [
        {'cust_id': 101, 'name': 'Alice'},
        {'cust_id': 102, 'name': 'Bob'},
    ]

    scan_orders = SeqScanOperator(orders, predicate=lambda r: r['amount'] >= 150)
    scan_cust = SeqScanOperator(customers)
    join_op = HashJoinOperator(scan_cust, scan_orders, 'cust_id', 'cust_id')
    agg_op = SortAggregateOperator(join_op, 'name', 'amount', 'SUM')

    agg_op.open()
    rows = []
    while True:
        r = agg_op.next()
        if r is None:
            break
        rows.append(r)
    agg_op.close()

    print("Aggregated query output:", rows)
    assert len(rows) == 2
    print("Volcano Iterator Query Engine verified successfully!")

if __name__ == '__main__':
    main()
