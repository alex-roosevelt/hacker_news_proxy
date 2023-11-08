import unittest

from main import ProxyHandler


class ProxyHandlerTest(unittest.TestCase):

    def test_modify_html(self):
        sample_html = '<html><body><div class="comment">This is a test coment </div></body></html>'
        modified_html = ProxyHandler.modify_html(sample_html)

        self.assertTrue('<html>' in modified_html)
        self.assertTrue('This is a test coment™' in modified_html)


if __name__ == '__main__':
    unittest.main()
