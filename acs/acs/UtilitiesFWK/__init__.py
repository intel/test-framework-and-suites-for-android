try:
    __import__('pkg_resources').declare_namespace(__name__)
except (KeyboardInterrupt, SystemExit):
    raise
except:
    pass
