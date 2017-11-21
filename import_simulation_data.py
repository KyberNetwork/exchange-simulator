from simulator import utils, config


def main():
    rdb = utils.get_redis_db()
    if config.MODE == 'simulation':
        rdb = utils.get_redis_db()
        ob_file = 'data/full_ob.dat'
        # ob_file = 'data/sample_ob.dat'
        utils.setup_data(rdb, ob_file)


if __name__ == '__main__':
    main()
