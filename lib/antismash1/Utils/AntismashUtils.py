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
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from installed_clients.KBaseReportClient import KBaseReport
from .AntismashParser import AntismashParser


ANTISMASH_SCRIPT="/kb/module/lib/antismash1/Utils/run_antismash.sh"

def log(message, prefix_newline=False):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    print(('\n' if prefix_newline else '') + time_str + ': ' + message)

class AntismashUtils:


    def __init__(self, config, params):
        self.ws_url = config["workspace-url"]
        self.callback_url =os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']

        self.dfu = DataFileUtil(self.callback_url)
        self.gfu = GenomeFileUtil(self.callback_url)
        self.au = AssemblyUtil(self.callback_url)
        self.report = KBaseReport (self.callback_url)
        self.result_dir = ""
        
        self.workspace_name = params['workspace_name']
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

    def get_gff_path(self,download_ret):
       gff_file_path = download_ret.get('file_path')
       return gff_file_path
    def get_assembly_path (self,download_ret):
       for j in download_ret:
          return (download_ret[j]['paths'][0]) # return the first instance
    
    def get_fasta_gff_file_path(self, genome_ref):
         genome_folder_name = self.get_genome_folder_name(genome_ref)
         result_dir = os.path.join (self.scratch, genome_folder_name)
         self._mkdir_p(result_dir)

         #Download fasta
         download_params2 = {'ref_lst': [genome_ref]}
         download_ret2 = self.au.get_fastas(download_params2)
         print (download_ret2)
         fasta_file_path = self.get_assembly_path(download_ret2)
         print (fasta_file_path)
         fasta_file_name = os.path.basename(fasta_file_path)
         shutil.move(fasta_file_path, result_dir)
         n_fasta_file_path = os.path.join(result_dir, fasta_file_name)

         #Download gff
         download_params = {'genome_ref': genome_ref}
         download_ret = self.gfu.genome_to_gff(download_params)
         print (download_ret)
         gff_file_path = self.get_gff_path(download_ret)
         gff_file_name = os.path.basename(gff_file_path)
         shutil.move(gff_file_path, result_dir)
         n_gff_file_path = os.path.join(result_dir, gff_file_name)

         return {"gff": n_gff_file_path, "fasta":n_fasta_file_path} 


    def run_antismash_single(self, final_report_dir, gff_file_path, fasta_file_path, genome_folder_name):

        output_dir = os.path.join(final_report_dir, genome_folder_name)
        argstring = ANTISMASH_SCRIPT + " "  + fasta_file_path + " " + gff_file_path + " "  +  output_dir
        print (argstring)
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
             self.delete_zip(output_dir)
        report_genome_index = str(genome_folder_name) + "/" + "index.html"
        return report_genome_index


    def add_html_page(self, output_dir, html_string):
        try:
            with open(output_dir +"/index.html" , "w") as html_file:
               html_file.write(html_string +"\n") 
        except IOError:
            print("Unable to write to "+  output_dir + "/index.html" + " file on disk.")
 
        

    def create_html_report(self, output_dir, workspace_name):
        '''
        function for creating html report
        :param callback_url:
        :param output_dir:
        :param workspace_name:
        :return:
        '''

        #dfu = DataFileUtil(callback_url)
        report_name = 'antismash_report_' + str(uuid.uuid4())
        #report = KBaseReport(callback_url)
#        index_file_path = output_dir + "/snpEff_genes.txt"
#        htmlstring = self.create_enrichment_report("snpEff_genes.txt", output_dir)

 #       try:
 #           with open(output_dir +"/index.html" , "w") as html_file:
 #              html_file.write(htmlstring +"\n")
 #       except IOError:
 #           print("Unable to write "+ index_file_path + " file on disk.")

        report_shock_id = self.dfu.file_to_shock({'file_path': output_dir,
                                            'pack': 'zip'})['shock_id']

        html_file = {
            'shock_id': report_shock_id,
            'name': 'index.html',
            'label': 'index.html',
            'description': 'HTML report for Antismash'
            }
        
        report_info = self.report.create_extended_report({
                        'direct_html_link_index': 0,
                        'html_links': [html_file],
                        'report_object_name': report_name,
                        'workspace_name': workspace_name
                    })
        return {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }

    def find_antismash_json_outputs(self):
          directory = self.result_dir
          print ("====================")
          print ("=================+++++" + directory + "-------------------------------\n")
          print ("====================")

          json_files = list()
          for genome in os.listdir(directory):
              newpath  = os.path.join(directory, genome)
              print (newpath)
              if os.path.isdir(newpath):
                  for npath in os.listdir(newpath):
                      if ".json" in npath:
                          json_path = os.path.join(newpath,npath)
                          json_files.append(json_path)
          return json_files  

    def create_html_tables_from_json(self):
        #json_list = ["./Bacillus_sp_OV322_assembly2.json", "./Bacillus_sp_OV322_assembly.json"]
        json_list = self.find_antismash_json_outputs()
        AP = AntismashParser()
        antismash_parse_data = AP.process_multiple_genomes(json_list)
        key = "mibig"
        df = AP.generate_tsv_from_lists(antismash_parse_data, key)
        mibigoutput_file = os.path.join(self.result_dir, "mibig.html")
        htmlpath = AP.get_html_from_df(df, mibigoutput_file)
        
    def run_antismash_main(self,genome_refs):
            result_dir = os.path.join(self.scratch, str(uuid.uuid4()))
            self.result_dir = result_dir
  
            self._mkdir_p(result_dir)
            html_str = "<html><body><pre>"
            html_str += "<a href='mibig.html'>migbig results</a>\n"
            for genome_ref in genome_refs:
                g_download = self.get_fasta_gff_file_path(genome_ref)
                gff_file_path = g_download.get('gff')
                fasta_file_path = g_download.get('fasta')

                genome_folder_name = self.get_genome_folder_name(genome_ref)
                genome_folder_path = os.path.join(result_dir, genome_folder_name)
                run_index = self.run_antismash_single(result_dir, gff_file_path, fasta_file_path,  genome_folder_name) 
                html_str += "<a href='./" + str(run_index) + "'>" + genome_folder_name + "</a>\n";
                      
            html_str += "</pre></body></html>"
            print (html_str)
            self.add_html_page(result_dir, html_str)

            self.create_html_tables_from_json()
            output = self.create_html_report(result_dir, self.workspace_name)            
            return output


