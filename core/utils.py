from ipware.ip import get_client_ip
import requests


def get_country_from_request(request):
    ip, _ = get_client_ip(request)

    # local testing
    if not ip or ip in ["127.0.0.1", "localhost"]:
        return "IN"   # test ke liye US

    try:
        response = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=3
        )
        data = response.json()
        return data.get("country_code", "IN")
    except Exception:
        return "IN"



