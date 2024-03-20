# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from antismash1.antismash1Impl import antismash1
from antismash1.antismash1Server import MethodContext
from antismash1.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class antismashTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('antismash1'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'antismash1',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = antismash1(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
#        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            pass
            #cls.wsClient.delete_workspace({'workspace': cls.wsName})
            #print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
#        ret = self.serviceImpl.run_antismash(self.ctx, {'workspace_name': "pranjan77:narrative_1638896817146",
#                                                             'genome_refs': ['65225/2/2', '70893/10/1']})

        params = {'workspace_name': 'pranjan77:narrative_1675119107551', 
                  'workspace_id':136582, 
                  'genome_refs': ['136582/389/1', '136582/388/1'], 
                  'annotation_options': {'cb-knownclusters': 1, 
                                          'rre': 1, 
                                          'clusterhmmer': 1,
                                          'smcog-trees':1,
                                          'asf': 1, 
                                          'tfbs': 1, 
                                          'cb-subclusters': 1}, 
                   'save_genome_options': {'save_genome': 1, 
                                           'suffix': '_antismash'}}

        ret = self.serviceImpl.run_antismash(self.ctx, params)


