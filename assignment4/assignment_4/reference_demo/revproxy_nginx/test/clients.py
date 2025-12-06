import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint

import requests


def send_request(id, url):
  try:
    response = requests.get(url)
    msg = response.text.strip()
    server_id = int(msg.rsplit(' ', maxsplit=1)[-1][:-1])
  except requests.RequestException as e:
    msg = str(e)
    server_id = -1
  return server_id, f'{id}: {msg}'


def test_load_balancing(url, n_requests):
  # server_id => cnt
  res_dict = {}
  with ThreadPoolExecutor(max_workers=n_requests) as executor:
    res_futures = [executor.submit(send_request, i, url)
                   for i in range(n_requests)]
    for res_future in as_completed(res_futures):
      res_server_id, res_msg = res_future.result()
      # statistics
      if res_server_id not in res_dict:
        res_dict[res_server_id] = 0
      res_dict[res_server_id] += 1
      # sys.stdout.write(f'{res_msg}\n')
      # sys.stdout.flush()
  pprint(res_dict)


if __name__ == '__main__':
  test_load_balancing(url='http://localhost:80/', n_requests=1000)
