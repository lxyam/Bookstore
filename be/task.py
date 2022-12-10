# 每0.5s检查有没有超时未支付的订单
class Config(object):
    JOBS = [
        {
            'id': 'soft_real_time',
            'func': '__main__:delete_timeout_order',
            'trigger': 'interval',
            'seconds': 0.5,
        }
    ]