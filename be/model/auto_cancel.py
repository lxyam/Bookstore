
import time
from be.model.order import Order

# 允许的未支付的时间为10分钟
time_limit = 600 
unpaid_orders = {}  

def get_time_stamp():
    cur_time_stamp = time.time()
    return int(cur_time_stamp)

  
def check_order_time(order_time):
    check_time = get_time_stamp()
    elapsed_time = check_time - order_time
    if elapsed_time > time_limit:
        return False
    else:
        return True

def add_unpaid_order(orderID):
    unpaid_orders[orderID] = get_time_stamp()
    return 200, "ok"

def delete_unpaid_order(orderID):
    try:
        unpaid_orders.pop(orderID)
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"

def delete_timeout_order():
    del_temp=[]
    order = Order()
    for (oid,tim) in unpaid_orders.items():
        if check_order_time(tim) == False:
            del_temp.append(oid)  
    for oid in del_temp:
        delete_unpaid_order(oid)
        order.cancel_order(oid)
    return 200