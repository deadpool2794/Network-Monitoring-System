from browser_history import get_history
from browser_history import utils
import time
import requests



SERVER = "http://192.168.6.207:5000/predict"

def main():
    
    def extract_browser_name(browser_class):
        return browser_class.split("'")[1].split(".")[2]

    outputs = get_history()


    supported_browsers = ["Edge", "Brave", "Chrome"]
    last_visited = dict()

    for browser in supported_browsers:
        last_visited[browser] = ""

    browser_classes = utils.get_browsers()

    interval = 5

    while(True):
        for browser_class in browser_classes:
            browser_name = extract_browser_name(str(browser_class))
            if browser_name in supported_browsers:
                try:
                    browser_object = browser_class()
                    browser_output_object = browser_object.fetch_history()
                    if(browser_output_object != None):
                        recent_accessed_url = browser_output_object.histories[0][0]
                        if(last_visited[browser_name] != recent_accessed_url):
                            last_visited[browser_name] = recent_accessed_url
                            payload = {
                                "browser": browser_name,
                                "url": recent_accessed_url
                            }
                            try:
                                resp = requests.post(SERVER, json=payload)
                                resp.raise_for_status()
                                result = resp.json()
                            except requests.RequestException as e:
                                print("Error sending to server:", e)
                except AssertionError:
                    pass
        try:
            time.sleep(interval)
        except:
            pass

if __name__=='__main__':
    main()






