# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
from installed_clients.KBaseReportClient import KBaseReport
from antismash1.Utils.AntismashUtils import AntismashUtils
from installed_clients.WorkspaceClient import Workspace as workspaceService
#END_HEADER


class antismash1:
    '''
    Module Name:
    antismash1

    Module Description:
    A KBase module: antismash
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = ""
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER

 
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.ws_url = config["workspace-url"]


        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

        self.config = config
        #END_CONSTRUCTOR
        pass


    def run_antismash(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_antismash
        print (params)
        genome_input_refs = params['genome_refs']
        antismash_options_str = ""
        for k in params['annotation_options']:
            if params['annotation_options'][k]==1:
                antismash_options_str += " --" + str(k)

        print (antismash_options_str)

        save_genome_options = params["save_genome_options"]
        #if params["save_genome_options"]["save_genome"] == 1:
        #    if len(params["save_genome_options"]['suffix']) > 0:
        #        genome_suffix = params["save_genome_options"]['suffix']
        #    else:
        #        genome_suffix = "_antismash"
        #else:
        #    genome_suffix = None

        genome_refs = list()
        for genome_input_ref in genome_input_refs:
            wsClient = workspaceService(self.ws_url, token=ctx['token'])
            genome_info = wsClient.get_object_info_new({'objects': [{'ref': genome_input_ref}]})[0]
            genome_input_type = genome_info[2]

            if 'GenomeSet' in genome_input_type:
                genomeSet_object = wsClient.get_objects2({'objects': [{'ref': genome_input_ref}]})['data'][0]['data']
                for ref_dict in genomeSet_object['elements'].values():
                    genome_refs.append(ref_dict['ref'])
            else:
                genome_refs.append(genome_input_ref)

        

        genome_refs = list(set(genome_refs))
        print (genome_refs)

        AS = AntismashUtils(self.config, params)
        output = AS.run_antismash_main(genome_refs, antismash_options_str, save_genome_options)
    
        print (output)

        #END run_antismash

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_antismash return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
