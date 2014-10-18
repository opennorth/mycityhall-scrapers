from __future__ import unicode_literals
from utils import CanadianScraper, CanadianPerson as Person

import re

COUNCIL_PAGE = 'http://www.stcatharines.ca/en/governin/MayorCouncil.asp'


class StCatharinesPersonScraper(CanadianScraper):

    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        councillors = page.xpath('//li[@class="withChildren"]/ul/li/a')[1:]
        for councillor in councillors:
            page = self.lxmlize(councillor.attrib['href'])

            name = councillor.text_content().split(',')[0]

            district = page.xpath('//p[preceding::h2[contains(text(), "Ward")]]/text()')[0]
            district = re.sub(', Ward \d+', '', district)

            role = 'Councillor'
            if 'Mayor' or 'At large' in district:
                district = 'St. Catharines'
                role = 'Mayor'

            p = Person(primary_org='legislature', name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            p.add_source(councillor.attrib['href'])

            image = page.xpath('//div[@class="right"]/p/img/@src')
            if image:
                p.image = image[0]

            contacts = page.xpath('//div[@class="contactDetails"]')[0]
            address = contacts.xpath('.//p')[2].text_content()
            phone = contacts.xpath('.//p')[3].text_content()
            fax = contacts.xpath('.//p')[4].text_content()
            if 'Councillor' in address:
                address = contacts.xpath('.//p')[3].text_content()
                phone = contacts.xpath('.//p')[4].text_content()
                fax = contacts.xpath('.//p')[5].text_content()

            address = re.sub(r'([a-z\.])([A-Z])', r'\1, \2', address)
            phone = phone.replace('Tel: ', '').replace('.', '-')
            fax = fax.replace('Fax: ', '').replace('.', '-')
            email = contacts.xpath('.//a[contains(@href, "mailto:")]/@href')[0].replace('mailto:', '')

            p.add_contact('address', address, 'legislature')
            p.add_contact('voice', phone, 'legislature')
            p.add_contact('fax', fax, 'legislature')
            p.add_contact('email', email)
            yield p
