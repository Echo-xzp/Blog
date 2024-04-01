import xml.etree.ElementTree as ET
import requests

HOST = 'www.hitagi.icu'
KEY = '0e52759f43d34d53847eaaadd6130adf'

def get_latest_posts(sitemap_path, n=10):
    # Parse the XML sitemap.
    url = sitemap_path  # 替换为你想要读取的具体 URL
    with request.urlopen(url) as response:
      xml_data = response.read()
    root = ET.fromstring(xml_data)
    # tree = ET.parse(sitemap_path)
    # root = tree.getroot()

    # Namespace dictionary to find the 'loc' and 'lastmod' tags.
    namespaces = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Get all URLs.
    urls = [(url.find('s:loc', namespaces).text, url.find('s:lastmod', namespaces).text)
            for url in root.findall('s:url', namespaces)
            if "/posts/" in url.find('s:loc', namespaces).text]

    # Sort URLs by the lastmod tag (in descending order), hence most recent pages come first.
    urls.sort(key=lambda x: x[1], reverse=True)

    # Return the n most recent URLs.
    return [url[0] for url in urls[:n]]

def ping_bing(url_list):
    # Prepare the URL and headers.
    # url = 'https://www.bing.com/indexnow'
    url = 'api.indexnow.org/IndexNow'
    headers = {
      'Content-Type': 'application/json; charset=utf-8',
    }

    # Prepare the body data.
    data = {
      "host": HOST,
      "key": KEY,
      "keyLocation": f"https://{HOST}/{KEY}.txt",
      "urlList": url_list
    }

    # Send the POST request.
    response = requests.post(url, headers=headers, json=data)
    return response

if __name__ == "__main__":
    # sitemap_path = "../../public/sitemap.xml"
    sitemap_path = f"https://{HOST}/sitemap.xml"
    url_list = get_latest_posts(sitemap_path, 10)
    # url_list.insert(0, f'https://{HOST}/')
    print(url_list)

    response = ping_bing(url_list)
    # Print the response.
    print(response.status_code)
    print(response.text)
