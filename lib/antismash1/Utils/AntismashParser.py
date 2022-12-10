import time
import os
import errno
import uuid
import shutil
import stat
import gzip
from zipfile import ZipFile, ZIP_DEFLATED
import subprocess  # nosec
from collections import defaultdict
import pandas as pd
import json


def log(message, prefix_newline=False):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    print(('\n' if prefix_newline else '') + time_str + ': ' + message)

class AntismashParser:


    def __init__(self):
        self.antismash_parse = defaultdict(dict)
        pass

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

    def load_antismash_json_output(self, json_file):
        with open (json_file) as f:
            data = json.load(f)
        return data


    #score 1 this is the number of "areas" antiSMASH determines to be producing biosynthetic products
    def get_number_bsgregions(self, data):
        number2=0
        for i in range (len(data["records"])):
            number=len(data["records"][i]['areas'])
            #print(number)
            number2=number+number2
        return(number2)


    # score 2 is the list of the biosynthetic gene clusters
    #I am working to be able to translate to interactions between organisms
    #for example microbe A produces antibiotic X which is known to kill microbe B this interaction would be indentified


    def get_bsgc_list(self, data):
        number=self.get_number_bsgregions(data)
        list1=[]
        for i in range (len(data["records"])):
            number=len(data["records"][i]['areas'])
            for j in range(number):

                bsgc=data["records"][i]['areas'][j]['products']
                list1.append(bsgc)
            flatlist = list(set([str for sublist in list1 for str in sublist]))


        return(flatlist)


    #score 3 is the number of biosynthetic gene clusters, existing within the areas

    def get_number_bsgc(self, data):
        bsgc_list=self.get_bsgc_list(data)
        number_bsgc=len(bsgc_list)

        return(number_bsgc)


    # score 4 obtains the clusterblast annotations
    #as with score 2, working on a metric for what is mean in relation to community formation

    def get_clusterblast_annotations(self, data):
        annotation_list=[]
        for j in range (len(data["records"])):
            try:
                for i in range(len(data["records"][j]['modules']['antismash.modules.clusterblast']['knowncluster']['proteins'])):
                    annotation_list.append(data["records"][j]['modules']['antismash.modules.clusterblast']['knowncluster']['proteins'][i]['annotations'])
            except:
                pass
        unique_annotation_list = list(set(annotation_list))
        return(unique_annotation_list)


    # score 5 exracts information on resistance from clusterblast
    #as with score 2 and 4, working on a metric for what is mean in relation to community formation

    def get_resistance_list(self, data):
        annotation_list=self.get_clusterblast_annotations(data)
        resistance_list = list(set([s for s in annotation_list if "resistance" in s]))
        return(resistance_list)

    #score 6 gets the number of proteins associated with resistance

    def get_resistance_number(self, data):
        annotation_list=self.get_clusterblast_annotations(data)
        resistance_number=sum((itm.count("resistance") for itm in annotation_list))
        return(resistance_number)


    def get_mibig_annotation_RegionToRegion_RiQ(self, data):
        mibig_list = list()
        for j in range (len(data["records"])):
            try:
                for k in (data["records"][j]['modules']['antismash.modules.cluster_compare']['db_results']['MIBiG']['by_region']):
                    for p in (data["records"][j]['modules']['antismash.modules.cluster_compare']['db_results']['MIBiG']['by_region'][str(k)]['RegionToRegion_RiQ']['scores_by_region']):
                        (mibig_id, location) = p.split(':')
                        #print (mibig_id)
                        mibig_list.append(mibig_id)
                #data["records"][j]['modules']['antismash.modules.cluster_compare']['db_results']['MIBiG']=""
            except:
                pass
        mibig_unique_list = list(set(mibig_list))
        return mibig_unique_list

    def process_single_genome(self, antismash_json_file, genome):
            antismash_data = self.load_antismash_json_output(antismash_json_file)
            self.antismash_parse['number_bsgregions'][genome] = self.get_number_bsgregions(antismash_data)
            self.antismash_parse['bsgc_list'][genome] = self.get_bsgc_list(antismash_data)
            self.antismash_parse['clusterblast_annotations'][genome] = self.get_clusterblast_annotations(antismash_data)
            self.antismash_parse['resistance_list'][genome] = self.get_resistance_list(antismash_data)
            self.antismash_parse['resistance_number'][genome]=self.get_resistance_number(antismash_data)
            self.antismash_parse['mibig'][genome]= self.get_mibig_annotation_RegionToRegion_RiQ(antismash_data)

    def process_multiple_genomes(self, json_list):
           for json_file in json_list:
               print (json_file)
               genome = os.path.basename(json_file)
               genome = genome.replace(".json", "")
               print (genome)
               self.process_single_genome(json_file, genome)
               print (json_file)
           print (self.antismash_parse)
           return self.antismash_parse


    def generate_tsv_from_lists(self, data, key):
        id_list = list()
        data_dict = {}
        for k in data[key]:
            id_list.extend(data[key][k])
        data_dict['unique_id_list'] = list(set(id_list))

        for k in data[key]:
            klist = data[key][k]
            tmplist = list()
            for p in data_dict['unique_id_list']:
                if p in klist:
                    tmplist.append(1)
                else:
                    tmplist.append(0)
            data_dict[k] = tmplist

        df = pd.DataFrame(data_dict)
        return df

    def get_html_from_df(self, df, filepath):
            html = df.to_html()

            # write html to file
            with open(filepath, "w") as f:
                f.write(html)
            return filepath



if __name__ == "__main__":
#    json_list=["~/antismash1/antismash1/test_local/workdir/tmp/7fa37973-144d-4779-ab29-000efc884fd6/Bacillus_sp_OV322_assembly_Prokka.RAST_63151_520_2/Bacillus_sp_OV322_assembly.json", "~/antismash1/antismash1/test_local/workdir/tmp/7fa37973-144d-4779-ab29-000efc884fd6/Bacillus_sp_OV322_assembly_Prokka.RAST_63151_520_2/Bacillus_sp_OV322_assembly2.json"]
    json_list = ["./Bacillus_sp_OV322_assembly2.json", "./Bacillus_sp_OV322_assembly.json"]
    AP = AntismashParser()
    antismash_parse_data = AP.process_multiple_genomes(json_list)
    key = "mibig"
    df = AP.generate_tsv_from_lists(antismash_parse_data, key)
    htmlpath = AP.get_html_from_df(df, "./mibig.html")

