import time
import os
import errno
import uuid
import shutil
import stat
import gzip
from zipfile import ZipFile, ZIP_DEFLATED

from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.DataFileUtilClient import DataFileUtil




def log(message, prefix_newline=False):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    print(('\n' if prefix_newline else '') + time_str + ': ' + message)

class GenomeUtils:

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

    def __init__(self, config):
        self.ws_url = config["workspace-url"]
        self.callback_url =os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']

        self.dfu = DataFileUtil(self.callback_url)
        self.gfu = GenomeFileUtil(self.callback_url)



    def download_genome(self, genome_ref, genome_name, export_genome):
        """
        download Genome as GENBANK or GFF
        """

        log('start downloading Genome file')

        if not export_genome:
            log('start downloading GENBANK as default')
            export_genome = {'export_genome_genbank': 1}

        # create the output directory and move the file there
        result_dir = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(result_dir)

        if export_genome.get('export_genome_genbank'):
            download_params = {'genome_ref': genome_ref}
            download_ret = self.gfu.genome_to_genbank(download_params)

            genbank_file = download_ret.get('genbank_file').get('file_path')
            genbank_file_name = os.path.basename(genbank_file)
            shutil.move(genbank_file, result_dir)

            new_file_name = genome_name + '_' + genome_ref.replace('/', '_') + \
                '.' + genbank_file_name.split('.', 1)[1]

            os.rename(os.path.join(result_dir, genbank_file_name),
                      os.path.join(result_dir, new_file_name))

        if export_genome.get('export_genome_gff'):
            download_params = {'genome_ref': genome_ref}
            download_ret = self.gfu.genome_to_gff(download_params)

            gff_file = download_ret.get('file_path')
            gff_file_name = os.path.basename(gff_file)
            shutil.move(gff_file, result_dir)

            new_file_name = genome_name + '_' + genome_ref.replace('/', '_') + \
                '.' + gff_file_name.split('.', 1)[1]

            os.rename(os.path.join(result_dir, gff_file_name),
                      os.path.join(result_dir, new_file_name))

        log('downloaded files:\n' + str(os.listdir(result_dir)))

        return result_dir

