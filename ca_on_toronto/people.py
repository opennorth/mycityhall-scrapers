from __future__ import unicode_literals
from utils import CanadianScraper, CanadianPerson as Person

import re

COUNCIL_PAGE = 'http://www1.toronto.ca/wps/portal/contentonly?vgnextoid=c3a83293dc3ef310VgnVCM10000071d60f89RCRD'


class TorontoPersonScraper(CanadianScraper):

    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        a = page.xpath('//a[contains(text(),"Mayor")]')[0]
        yield self.scrape_mayor(a.attrib['href'])

        for a in page.xpath('//a[contains(text(),"Councillor")]'):
            page = self.lxmlize(a.attrib['href'])
            h1 = page.xpath('//h1//text()')[0]
            if 'Council seat is vacant' not in h1:
                yield self.scrape_councilor(page, h1, a.attrib['href'])

    def scrape_councilor(self, page, h1, url):
        name = h1.split('Councillor')[1]
        ward_full = page.xpath('//p/descendant-or-self::*[contains(text(), "Profile:")]/text()')[0].replace('\xa0', ' ')
        ward_num, ward_name = re.search(r'(Ward \d+) (.+)', ward_full).groups()
        if ward_name == 'Etobicoke Lakeshore':
            ward_name = 'Etobicoke\u2014Lakeshore'

        district = '{0} ({1})'.format(ward_name.replace('-', '\u2014'), ward_num.split()[1])

        p = Person(primary_org='legislature', name=name, district=district, role='Councillor')
        p.add_source(COUNCIL_PAGE)
        p.add_source(url)

        p.image = page.xpath('//main//img/@src')[0].replace('www.', 'www1.')  # @todo fix lxmlize to use the redirected URL to make links absolute
        email = self.get_email(page)
        p.add_contact('email', email)

        addr_cell = page.xpath('//*[contains(text(), "Toronto City Hall")]/ancestor::td')[0]
        phone = (addr_cell.xpath('(.//text()[contains(., "Phone:")])[1]')[0]
                          .split(':')[1])
        p.add_contact('voice', phone, 'legislature')

        address = '\n'.join(addr_cell.xpath('./p[2]/text()')[:2])
        if address:
            p.add_contact('address', address, 'legislature')

        return p

    def scrape_mayor(self, url):
        page = self.lxmlize(url)
        name = page.xpath("//h1/text()")[0].replace("Toronto Mayor", "").strip()

        p = Person(primary_org='legislature', name=name, district="Toronto", role='Mayor')
        p.add_source(COUNCIL_PAGE)
        p.add_source(url)

        p.image = page.xpath('//article/img/@src')[0].replace('www.', 'www1.')

        url = page.xpath('//a[contains(text(), "Contact the Mayor")]')[0].attrib['href'].replace('www.', 'www1.')
        p.add_source(url)
        page = self.lxmlize(url)

        mail_elem, email_elem, phone_elem = page.xpath('//header')[:3]
        address = ''.join(mail_elem.xpath('./following-sibling::p//text()'))
        phone = phone_elem.xpath('./following-sibling::p[1]//text()')[0]
        email = email_elem.xpath('./following-sibling::p[1]//text()')[0]

        p.add_contact('address', address, 'legislature')
        p.add_contact('voice', phone, 'legislature')
        p.add_contact('email', email)
        return p
