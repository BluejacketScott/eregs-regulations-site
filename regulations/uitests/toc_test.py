import os
import unittest
from base_test import BaseTest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

class TOCTest(BaseTest, unittest.TestCase):

    def job_name(self):
        return 'TOC test'

    def test_toc(self):
        self.driver.get('http://localhost:8000/1005')
        drawer_toggle = WebDriverWait(self.driver, 10).until(
            lambda driver: driver.find_element_by_id('panel-link'))
        drawer_toggle.click()

        # toggle arrow should switch
        self.assertTrue(drawer_toggle.get_attribute('class').find('open'))

        toc_link_1005_1 = self.driver.find_element_by_xpath('//*[@id="toc"]/ol/li[1]/a')
        # toc link should have the proper section id attr
        self.assertEquals(toc_link_1005_1.get_attribute('data-section-id'), '1005-1')
        toc_link_1005_1.click()

        # reg section should load in content area
        self.assertIn('catharine and myriads', self.driver.find_element_by_class_name('section-title').text)

        # toc link should be highlighted
        self.assertIn('current', toc_link_1005_1.get_attribute('class'))

        # test another section
        toc_link_1005_7 = self.driver.find_element_by_xpath('//*[@id="toc"]/ol/li[7]/a')
        self.assertEquals(toc_link_1005_7.get_attribute('data-section-id'), '1005-7')
        toc_link_1005_7.click()

        self.assertIn('roentgenologist zest', self.driver.find_element_by_class_name('section-title').text)
        self.assertIn('current', toc_link_1005_7.get_attribute('class'))

        # make sure that the current class has been removed from the prev section
        self.assertNotIn('current', toc_link_1005_1.get_attribute('class'))

if __name__ == '__main__':
    unittest.main()
