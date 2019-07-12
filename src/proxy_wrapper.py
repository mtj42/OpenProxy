import the_proxy


the_proxy.logging.basicConfig(level=getattr(the_proxy.logging, 'DEBUG'),
                        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')

try:
    proxy = the_proxy.HTTP(hostname="127.0.0.1", port=8080)
    proxy.run()
except KeyboardInterrupt:
    pass




