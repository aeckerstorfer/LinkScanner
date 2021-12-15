import requests
from bs4 import BeautifulSoup


class Link:
    def __init__(self, url, status_code):
        self.url = url
        self.status_code = status_code


class LinkScanner:
    __broken_status_codes = {'301', '404', '410', '500', '502', '503', '504'}

    def get_links(self, url):
        return map(lambda link: link.url, self.get_links_with_status_codes(url))

    def get_links_with_status_codes(self, url):
        links = []
        self.__get_page_links(url, url, links, [])
        return links

    def get_broken_links(self, url):
        links = self.get_links_with_status_codes(url)
        return [link for link in links if link.status_code in self.__broken_status_codes]

    def __get_page_links(self, base_url, url, return_list, checked_urls):
        request = requests.get(url)

        status_code = request.status_code
        checked_urls.append(url)
        return_list.append(Link(url, status_code))

        if status_code == 200:
            soup = BeautifulSoup(request.content, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')

                if self.__is_valid_url(href):
                    href = '{}{}'.format(
                        base_url, href) if href.startswith('#') else href
                    href = '{}{}'.format(
                        url, href) if href.startswith('/') else href

                    if href not in checked_urls and self.__check_if_still_on_site(base_url, href):
                        self.__get_page_links(
                            base_url, href, return_list, checked_urls)

    def __is_valid_url(self, url):
        return (url is not None
                and not url.startswith('.')
                and url != ''
                )

    def __check_if_still_on_site(self, base_url, url):
        return url.startswith(base_url)