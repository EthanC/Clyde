from environs import env

env.read_env()

assert env.str("TESTS_WEBHOOK_URL", default=None)
