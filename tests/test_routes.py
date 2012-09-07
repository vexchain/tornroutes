
# make sure we get our local tornroutes before anything else
import sys, os.path
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

import unittest
import tornado.web
from tornado.testing import AsyncHTTPTestCase

from tornroutes import route, route_redirect, generic_route

# NOTE - right now, the route_redirect function is not tested.

class RouteTests(unittest.TestCase):

    def setUp(self):
        route._routes = [] # reach in and ensure this is clean
        @route('/xyz')
        class XyzFake(object):
            pass

        route_redirect('/redir_elsewhere', '/abc')

        @route('/abc', name='abc')
        class AbcFake(object):
            pass

        route_redirect('/other_redir', '/abc', name='other')


    def test_num_routes(self):
        self.assertTrue( len(route.get_routes()) == 4 ) # 2 routes + 2 redir

    def test_routes_ordering(self):
        # our third handler's url route should be '/abc'
        self.assertTrue( route.get_routes()[2].reverse() == '/abc' )

    def test_routes_name(self):
        # our first handler's url route should be '/xyz'
        t = tornado.web.Application(route.get_routes(), {})
        self.assertTrue( t.reverse_url('abc') )
        self.assertTrue( t.reverse_url('other') )


class GenericRouteTests(unittest.TestCase):

    def setUp(self):
        route._routes = [] # clean things out just in case

    def test_generic_routes_default_handler(self):
        generic_route('/something', 'some_template.html')
        assert len(route.get_routes()) == 1


class TestGenericRouteRender(AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application(
            route.get_routes(),
            template_path = os.path.dirname(__file__)
            )

    @classmethod
    def setUpClass(cls):
        route._routes = []

        # must be done here prior to get_app being called
        generic_route('/generic', 'generic_1.html')
        generic_route('/other', 'generic_2.html')

    def test_generic_render(self):
        generic_1 = open(
            os.path.join( os.path.dirname(__file__), 'generic_1.html')
            ).read()
        generic_2 = open(
            os.path.join( os.path.dirname(__file__), 'generic_2.html')
            ).read()

        response = self.fetch('/generic')
        assert generic_1.strip() == response.body.strip()
        assert response.code == 200

        response = self.fetch('/other')
        assert generic_2.strip() == response.body.strip()
        assert response.code == 200

