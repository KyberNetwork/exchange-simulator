# Order Book Generator

## Prerequisites
1. Install redis (e.g. `apt-get install redis`)
2. Install Python 3.6
3. Install Python dependencies (`pipenv install`)


## Running it
Assuming Redis is installed and its' server is at `/usr/local/bin/redis-server`:

    $ python -m generator.generator ----redis-server-cmd /usr/local/bin/redis-server


## Output
Redis dump file (`dump.rdb`) will be in `/output/TIMESTAMP` directory.