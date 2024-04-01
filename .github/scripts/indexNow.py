import xml.etree.ElementTree as ET
import requests

HOST = 'www.hitagi.icu'
KEY = '5ba6dc01e9fb45919e0b708d37407ff1'

def get_latest_posts(sitemap_path, n=10):
    # Parse the XML sitemap.
    url = sitemap_path  # 替换为你想要读取的具体 URL
    response = requests.get(url)
    # 确认请求是否成功
    if response.status_code == 200:
      xml_data = response.content
    else:
      print("请求失败，请检查URL或其他问题。")
      exit()
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
    url = 'https://api.indexnow.org/IndexNow'
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

    print('提交index中....')
    response = ping_bing(url_list)
    # Print the response.
    print('提交完成,返回结果如下:')
    print(response.status_code)
    print(response.content)
