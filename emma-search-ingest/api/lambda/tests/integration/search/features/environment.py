from tests.integration import config


def before_all(context):
    """
    Things that need to be set up before all integration tests
    """
    env = context.config.userdata.get("env")
    config.set_servers(env)