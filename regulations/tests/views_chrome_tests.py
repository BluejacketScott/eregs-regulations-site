from unittest import TestCase

from django.conf import settings
from django.http import HttpResponseGone
from django.test import Client, RequestFactory
from mock import call, patch, Mock

from regulations.views import chrome


class ViewsChromeTest(TestCase):
    def setUp(self):
        self.original_debug = settings.DEBUG
        self.original_api_base = settings.API_BASE

    def tearDown(self):
        settings.DEBUG = self.original_debug
        settings.API_BASE = self.original_api_base

    @patch('regulations.views.error_handling.api_reader')
    @patch('regulations.views.chrome.ChromeView.set_chrome_context')
    @patch('regulations.views.chrome.generator')
    def test_404(self, generator, set_chrome_context, api_reader):
        """Test that the response of the outer view is that of the inner
        when there's an error"""
        api_reader.ApiReader.return_value.regversions.return_value = None
        generator.get_tree_paragraph.return_value = {}
        set_chrome_context.return_value = None

        class InnerView(chrome.TemplateView):
            def get(self, request, *args, **kwargs):
                return HttpResponseGone()

        class FakeView(chrome.ChromeView):
            partial_class = InnerView

        view = FakeView()
        view.request = RequestFactory().get('/')
        response = view.get(view.request, label_id='lab', version='ver')
        self.assertEqual(404, response.status_code)

    @patch('regulations.views.chrome.error_handling')
    @patch('regulations.views.chrome.generator')
    @patch('regulations.views.chrome.SideBarView')
    def test_error_propagation(self, sbv, generator, error_handling):
        """While we don't rely on this sort of propagation for the main
        content (much), test it in the sidebar"""
        sbv.as_view.return_value.return_value = HttpResponseGone()

        class FakeView(chrome.ChromeView):
            def add_main_content(self, context):
                pass

            def set_chrome_context(self, context, reg_part, version):
                pass

        view = FakeView()
        view.request = RequestFactory().get('/')
        response = view.get(view.request, label_id='lab', version='ver')
        self.assertEqual(410, response.status_code)

    @patch('regulations.views.chrome.generator')
    def test_get_404(self, generator):
        generator.get_regulation.return_value = None
        response = Client().get('/regulation/111/222')
        self.assertEqual(404, response.status_code)

    @patch('regulations.views.chrome.generator')
    def test_get_404_tree(self, generator):
        generator.get_regulation.return_value = {'regulation': 'tree'}
        generator.get_tree_paragraph.return_value = None
        response = Client().get('/regulation/111/222')
        self.assertEqual(404, response.status_code)

    def test_diff_redirect_label_regulation(self):
        """If viewing a full regulation, the redirect for diffs should point
        to the first section"""
        view = chrome.ChromeView()
        toc = [{'section_id': '199-Subpart-A',
                'sub_toc': [{'section_id': '199-4'}, {'section_id': '199-6'}]},
               {'section_id': '199-Subpart-B',
                'sub_toc': [{'section_id': '199-8'}, {'section_id': '199-9'}]}]
        self.assertEqual('199-4', view.diff_redirect_label('199', toc))

    def test_diff_redirect_label_paragraph(self):
        """If viewing a single paragraph, the redirect for diffs should point
        to that paragraph's section. Similarly, all diffs for interpretations
        should point to the root interpretation"""
        view = chrome.ChromeView()
        self.assertEqual('199-4', view.diff_redirect_label('199-4-b', []))
        self.assertEqual('199-4', view.diff_redirect_label('199-4-b-3', []))
        self.assertEqual('199-A', view.diff_redirect_label('199-A', []))
        self.assertEqual('199-A', view.diff_redirect_label('199-A-14B', []))
        self.assertEqual('199-Interp',
                         view.diff_redirect_label('199-Interp', []))
        self.assertEqual('199-Interp',
                         view.diff_redirect_label('199-Interp-h1', []))
        self.assertEqual('199-Interp',
                         view.diff_redirect_label('199-12-Interp-2', []))


class ViewsChromeSubterpTest(TestCase):
    def test_diff_redirect_label(self):
        view = chrome.ChromeSubterpView()
        for label in ('199-Subpart-Interp', '199-Subpart-A-Interp',
                      '199-Appendices-Interp'):
            self.assertEqual('199-Interp',
                             view.diff_redirect_label(label, None))

    @patch('regulations.views.chrome.generator')
    @patch('regulations.views.chrome.filter_by_subterp')
    def test_check_tree(self, filter_by_subterp, generator):
        view = chrome.ChromeSubterpView()

        generator.get_tree_paragraph.return_value = None
        try:
            view.check_tree({'version': 'vvvv', 'label_id': 'llll'})
            self.assertTrue(False)
        except chrome.error_handling.MissingSectionException:
            pass

        generator.get_tree_paragraph.return_value = {'children': []}
        filter_by_subterp.return_value = []
        try:
            view.check_tree({'version': 'vvvv', 'label_id': 'llll'})
            self.assertTrue(False)
        except chrome.error_handling.MissingSectionException:
            pass

        filter_by_subterp.return_value = ["something"]
        view.check_tree({'version': 'vvvv', 'label_id': 'llll'})
        # No exception


def test_chrome_search_version_present(monkeypatch, rf):
    """If a version is in the request, we use it to derive the label_id."""
    monkeypatch.setattr(chrome, 'utils', Mock())
    chrome.utils.first_section.return_value = '111-22'

    view = chrome.ChromeSearchView()
    view.request = rf.get('/?version=some-version')
    result = view.fill_kwargs({'label_id': '111'})

    assert result == {
        'version': 'some-version',
        'skip_count': True,
        'label_id': '111-22',
    }
    assert chrome.utils.first_section.call_args == call('111', 'some-version')


def test_chome_search_missing_version(monkeypatch, rf):
    """A missing version shouldn't cause the results page to explode"""
    monkeypatch.setattr(chrome, 'utils', Mock())
    monkeypatch.setattr(chrome, 'get_versions', Mock())
    chrome.get_versions.return_value = (
        {'version': 'current-version'}, {'version': 'next-version'})
    chrome.utils.first_section.return_value = '222-33'

    view = chrome.ChromeSearchView()
    view.request = rf.get('/')
    result = view.fill_kwargs({'label_id': '222'})

    assert result == {
        'version': 'current-version',
        'skip_count': True,
        'label_id': '222-33',
    }
    assert chrome.get_versions.call_args == call('222')
    assert chrome.utils.first_section.call_args == call('222',
                                                        'current-version')
