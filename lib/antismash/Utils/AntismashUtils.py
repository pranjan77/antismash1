import time
import os
import errno
import uuid
import shutil
import stat
import gzip
from zipfile import ZipFile, ZIP_DEFLATED
import subprocess  # nosec

from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace



def log(message, prefix_newline=False):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    print(('\n' if prefix_newline else '') + time_str + ': ' + message)

class AntismashUtils:


    def __init__(self, config):
        self.ws_url = config["workspace-url"]
        self.callback_url =os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']

        self.dfu = DataFileUtil(self.callback_url)
        self.gfu = GenomeFileUtil(self.callback_url)

    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def delete_zip (self,path):
        dir_list = os.listdir(path)
        for j in dir_list:
            if j.endswith(".zip"):
                zipfilename = os.path.join(path,j)
                os.remove(zipfilename)

     

    def get_genome_folder_name(self,genome_ref):
        ws=Workspace(self.ws_url)
        obj = { "ref": genome_ref }
        obj_info = ws.get_object_info3({
            "objects": [obj],
            "includeMetadata": 1
            })

        obs=genome_ref.replace("/", "_")
        return (obj_info['infos'][0][1] + "_" +  str(obs))

    def get_genbank_file_path(self, genome_ref):
         genome_folder_name = self.get_genome_folder_name(genome_ref)
         result_dir = os.path.join (self.scratch, genome_folder_name)
         self._mkdir_p(result_dir)
         download_params = {'genome_ref': genome_ref}
         download_ret = self.gfu.genome_to_genbank(download_params)
         genbank_file = download_ret.get('genbank_file').get('file_path')
         #genbank_file_name = os.path.basename(genbank_file)
         shutil.move(genbank_file, result_dir)
         return genbank_file


    def run_antismash_single(self, final_report_dir, genbank_file_path, genome_folder_name):

        output_dir = os.path.join(final_report_dir, genome_folder_name)
        argstring = "antismash " + str(genbank_file_path) + " --output-dir=" + str(output_dir)
        args = argstring.split(" ")
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
        (stdout, stderr) = proc.communicate()
        print('-' * 80)
        print('Antismash output:')
        print(stdout)
        print(stderr)
        print('-' * 80)
        if proc.returncode != 0:
            raise Exception(f"Error generating Antismash output: {stderr}")

        index_path=os.path.join(output_dir, "index.html")
        if os.path.exists(index_path):
             self.delete_zip(ioutput_dir)
        report_genome_index = str(genome_folder_name) + "/" + "index.html"
        return report_genome_index




        # create the output directory and move the file there

    def run_antismash_main(self,genome_refs):
            result_dir = os.path.join(self.scratch, str(uuid.uuid4()))
            self._mkdir_p(result_dir)
            htmlstr = "<html><body><pre>"
            for genome_ref in genome_refs:
                genbank_file_path = self.get_genbank_file_path(genome_ref)
                genome_folder_name = self.get_genome_folder_name(genome_ref)
                genome_folder_path = os.path.join(result_dir, genome_folder_name)
                run_index = self.run_antismash_single(result_dir, genbank_file_path,  genome_folder_name) 
                html_str += str(run_index) + "\n";

            html_str += "</pre></body></html>"
            print (html_str)

            return result_dir

