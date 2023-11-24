import requests

def search_zipcode(zipcode):
    url = "https://zipcloud.ibsnet.co.jp/api/search"
    params = {"zipcode": zipcode}

    response = requests.get(url, params=params)
    data = response.json()

    try:
        if data["status"] == 200:
            result = {
                "address1": data["results"][0]["address1"],
                "address2": data["results"][0]["address2"],
                "address3": data["results"][0]["address3"]
            }
            return result
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while processing the request: {e}")
        return None