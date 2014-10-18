from __future__ import unicode_literals
from utils import CanadianScraper, CanadianPerson as Person

import re

COUNCIL_PAGE = 'http://www.greatersudbury.ca/inside-city-hall/city-council/'


class GreaterSudburyPersonScraper(CanadianScraper):

    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        councillors = page.xpath('//div[@id="navMultilevel"]//a')
        for councillor in councillors:
            if councillor == councillors[0]:
                yield self.scrape_mayor(councillor)
                continue

            if '-' not in councillor.text_content():
                break

            district, name = councillor.text_content().split(' - ')
            if name == 'Vacant':
                continue

            page = self.lxmlize(councillor.attrib['href'])

            address = page.xpath('//div[@class="column last"]//p')[0].text_content()
            phone = page.xpath('//article[@id="primary"]//*[contains(text(),"Tel")]')[0].text_content()
            phone = re.findall(r'([0-9].*)', phone)[0].replace(') ', '-')
            fax = page.xpath('//article[@id="primary"]//*[contains(text(),"Fax")]')[0].text_content()
            fax = re.findall(r'([0-9].*)', fax)[0].replace(') ', '-')
            email = page.xpath('//a[contains(@href, "mailto:")]')[0].text_content()

            p = Person(primary_org='legislature', name=name, district=district, role='Councillor')
            p.add_source(COUNCIL_PAGE)
            p.add_source(councillor.attrib['href'])
            p.add_contact('address', address, 'legislature')
            p.add_contact('voice', phone, 'legislature')
            p.add_contact('fax', fax, 'legislature')
            p.add_contact('email', email)
            p.image = page.xpath('//article[@id="primary"]//img/@src')[1]
            yield p

    def scrape_mayor(self, div):
        url = div.attrib['href']
        page = self.lxmlize(url)

        name = div.text_content().replace('Mayor ', '')
        contact_url = page.xpath('//ul[@class="navSecondary"]//a[contains(text(),"Contact")]')[0].attrib['href']
        page = self.lxmlize(contact_url)

        contact_div = page.xpath('//div[@class="col"][2]')[0]

        address = contact_div.xpath('.//p[1]')[0].text_content()
        address = re.findall(r'(City of Greater .*)', address, flags=re.DOTALL)[0]
        phone = contact_div.xpath('.//p[2]')[0].text_content()
        phone = phone.replace('Phone: ', '')
        fax = contact_div.xpath('.//p[3]')[0].text_content()
        fax = fax.split(' ')[-1]
        email = contact_div.xpath('//a[contains(@href, "mailto:")]')[0].text_content()

        p = Person(primary_org='legislature', name=name, district='Greater Sudbury', role='Mayor')
        p.add_source(COUNCIL_PAGE)
        p.add_source(contact_url)
        p.add_contact('address', address, 'legislature')
        p.add_contact('voice', phone, 'legislature')
        p.add_contact('fax', fax, 'legislature')
        p.add_contact('email', email)
        return p
