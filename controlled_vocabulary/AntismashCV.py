import pandas as pd
import json



class AntismashCV:


     def __init__(self,):
         pass

     def get_date_time(self):

         from datetime import datetime
         now = datetime.now() # current date and time
         date_time = now.strftime("%Y-%m-%d-%Y %H-%M-%S")
         return (date_time)


     def download_antismash_table(self,date_time):

         url = "https://docs.antismash.secondarymetabolites.org/glossary/index.html"
         date_time_f = date_time.replace(" ", "")
         df  = pd.read_html(url)[0]
         df = df.set_index('Label')

         filename = "antismash_glossary-" + date_time_f + ".csv"

         df.to_csv(filename, sep="\t")
         return (filename)


     def build_antismash_term_hash(self,antismash_glossary_file):
         with open (antismash_glossary_file) as agf:
             agfdata = agf.readlines()

         term_hash = dict()

         for line in agfdata:
             label, description, added, last_update = line.split("\t")
             if label == "Label":
                 continue
             key = "AS:" + label
             synonyms = []
             id = label
             name = description
             term_hash[key] = {"name":name, "id": id, "synonyms": synonyms}

         return (term_hash)

     def build_antismash_cv (self, date_version):
        date_time = self.get_date_time()
        csvfile = self.download_antismash_table(date_time)
        antismash_term_hash = self.build_antismash_term_hash(csvfile)

        antismash_dict = dict()

        antismash_dict= {
            "ontology" : "Antismash_cv",
            "format_version" : "N/A",
            "date" : date_time,
            "data_version" : date_version,
            "term_hash": antismash_term_hash
        }
        return (antismash_dict)


if __name__ == "__main__":

     date_version = "01-Mar-2023"
     ASC = AntismashCV()
     antismash_dict = ASC.build_antismash_cv(date_version)
     with open('Antismash_CV.json', 'w') as fp:
        json.dump(antismash_dict, fp, indent=2)


