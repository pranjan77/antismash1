# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
from installed_clients.KBaseReportClient import KBaseReport
from antismash1.Utils.AntismashUtils import AntismashUtils

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

    def run_antismash_single(self,final_report_dir, genbank_file_path, genome_folder_name):
         os.system("ls /miniconda/envs/py39/bin && source /miniconda/etc/profile.d/conda.sh && conda activate py39  &&  antismash /kb/module/work/sequence.gbk --output-dir /kb/module/work/ndc")
#source activate py39 && python -m antismash /kb/module/work/sequence.gbk && source deactivatei py39")

#            output_dir = os.path.join(final_report_dir, genome_folder_name)
#            argstring = "source activate py39  && antismash " + str(genbank_file_path) + " --output-dir=" + str(output_dir)
#            args = argstring.split(" ")
#            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
#            (stdout, stderr) = proc.communicate()
#            print('-' * 80)
#            print('Antismash output:')
#            print(stdout)
#            print(stderr)
#            print('-' * 80)
#            if proc.returncode != 0:
#                raise Exception(f"Error generating Antismash output: {stderr}")
#
#            index_path=os.path.join(output_dir, "index.html")
#            if os.path.exists(index_path):
#                 self.delete_zip(ioutput_dir)
#            report_genome_index = str(genome_folder_name) + "/" + "index.html"
#            return report_genome_index

    #x = run_antismash_single(final_report_dir, genbank_file_path, genome_folder_name)




 
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
        genome_refs = params['genome_refs']
        f = AntismashUtils(self.config, params)
        output = f.run_antismash_main(genome_refs)
        print (output)

        #final_report_dir = "/kb/module/work"
        #genbank_file_path = "/kb/module/work/KBase_derived_Bacillus_sp_OV322_assembly_Prokka.RAST.gbff"
        #genome_folder_name = "zfffr"

        #x = self.run_antismash_single(final_report_dir, genbank_file_path, genome_folder_name)
        #report = KBaseReport(self.callback_url)
        #report_info = report.create({'report': {'objects_created':[],
        #                                        'text_message': "infoxxxxx"},
        #                                        'workspace_name': params['workspace_name']})

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
