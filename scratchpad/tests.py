import logging
import requests

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

schemas = ["http"]
test_urls = ["example.org"]

for idx, url in enumerate(test_urls):
	for schema in schemas:
		fqdn = "//:".join(url, schema)
		expected_result = requests.get(fqdn).text
		logging.debug("test %d : %s" % idx, fqdn)
		logging.debug("expected_result: %s" % expected_result)

