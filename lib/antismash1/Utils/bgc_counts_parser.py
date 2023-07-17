import os
import json
import numpy as np
import pandas as pd
import uuid

# path where you want the parser to look for json files
#this must be changed 

class BGCCounter:

    def __init__(self, datapath):
        self.datapath = datapath
        self.index_paths = dict()
        self.url_map = dict()
        pass

    def get_index_path(self, rootpath):
        root = rootpath.split("/")[-1]
        return root + "/" + "index.html"

    #this function loads the data in json format 
    def read_antiSMASHjson(self,path_to_file):
        with open(path_to_file) as json_file:
            data = json.load(json_file)
        return(data)


    #score 1 this is the number of "areas" antiSMASH determines to be producing biosynthetic products 
    def get_number_bsgregions(self,data):
        number2=0
        for i in range (len(data["records"])):
            number=len(data["records"][i]['areas'])
            #print(number)
            number2=number+number2
        return(number2)



    # score 2 is the list of the biosynthetic gene clusters
    #I am working to be able to translate to interactions between organisms
    #for example microbe A produces antibiotic X which is known to kill microbe B this interaction would be indentified 


    def get_bsgc_list(self,data):
        number=get_number_bsgregions(data)
        list1=[]
        for i in range (len(data["records"])):
            number=len(data["records"][i]['areas'])
            for j in range(number):

                bsgc=data["records"][i]['areas'][j]['products']
                list1.append(bsgc)
            flatlist = [str for sublist in list1 for str in sublist]    

        return(flatlist) 
    #get bcg and area it is on  

    #returns a list of list for in each sublist, the FIRST element is THE RECORD NUMBER
    #the SECOND is THE REGION NUMBER (area)
    #the THIRD is THE PRODUCT

    def read_antiSMASHjson(self,path_to_file):
        with open(path_to_file) as json_file:
            data = json.load(json_file)
        return(data)


    def get_bcg_area_totals(self,data):
        bcg_area_all_dict={}
        bcg_area_all=[]
        number2=0
        for i in range (len(data["records"])):
            number=len(data["records"][i]['areas'])
            #bcg_area=[]
            
            for j in range(number):
                
                bsgc=data["records"][i]['areas'][j]['products']
                bcg_area_all.append(bsgc)
                #bcg_area.append(bsgc)
    
            #print(number)
            
            #bcg_area_all.append(bcg_area)
        bcg_area_all = [item for sublist in bcg_area_all for item in sublist]    
        bcg_area_all.sort()
        #print(bcg_area_all)
        bcg_area_all_dict=dict((x,bcg_area_all.count(x)) for x in set(bcg_area_all))
        #bcg_area_all.append(file_name)    
        return(bcg_area_all_dict)


    def get_bgc_counts(self):
        path = self.datapath
        tsvpath = str(uuid.uuid1()) + ".tsv"
        d = {}
        genomes_lst=[]
        # for every json file in this path, perform the following 
        for root, dirs, files in os.walk(path):
            for name in files:
                if '.json' in name:
                    genomes_lst.append(name)
                    self.index_paths[name] = self.get_index_path(root)
                    data = self.read_antiSMASHjson(root + "/" + name)
                    d[name]=self.get_bcg_area_totals(data)

                    #Map antismash result urls for report
                    genome_folder = root.split("/")[-1]
                    name1 = name.replace(".json", "")
                    #Get a new string with ws_id removed from folder name
                    self.url_map[name] = '<a href="' +    './' + genome_folder + '/index.html' + '">' + genome_folder  + "</a>"

        genome_lst=(list(d.keys()))
        bcsg_lst=[]
        for k, v in d.items():
            for k1, v1 in v.items():
                bcsg_lst.append(k1)
                
        bcsg_set=set(bcsg_lst)

        #make dataframe
        df2 = pd.DataFrame(index =  list(bcsg_set), 
                                columns = genomes_lst)
        #fill the dataframe with the counts stored in dictionary "d"
        df2 =pd.DataFrame.from_dict(d,orient='columns')
        df_transpose=df2.T

        #convert nan to 0.0
        df_transpose.replace(np. nan,0,inplace=True) 
        float_col = df_transpose.select_dtypes(include=['float64']) # This will select float columns only
        for col in float_col.columns.values:
            df_transpose[col] = df_transpose[col].astype('int64')

        df_transpose.to_csv(tsvpath, sep="\t")

        return tsvpath


    def generate_html_table(self, df: pd.DataFrame):
        """Display a pandas.DataFrame as jQuery DataTables"""

        # Generate random container name
        id_container = uuid.uuid1()
        output = """
    <div id="datatable-container-{id_container}">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.0/jquery.min.js"></script>
      <script type="text/javascript" src="https://cdn.datatables.net/1.13.5/js/jquery.dataTables.min.js"></script>
      <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.5/css/jquery.dataTables.min.css"/>
      <script type="text/javascript">
        $(document).ready( function () {{
            $('#BGCtable').DataTable();
        }});
      </script>
      <!-- Insert table below -->
      {table}
    </div>
        """.format(
            id_container=id_container,
            table=df.to_html(
                index=False,
                table_id="BGCtable",
                classes="display"
            ),
        )
        return output

    def get_bgc_table(self):
        tsvpath = self.get_bgc_counts()
        print (tsvpath)
        df = pd.read_csv(tsvpath, sep="\t")
        df = df.rename(columns={'Unnamed: 0': 'Genomes'}) 
        df['Genomes'] = df['Genomes'].replace(self.url_map)
        html_str = self.generate_html_table(df)
        html_str = html_str.replace("&lt;", '<')
        html_str = html_str.replace('&gt;', '>')
        return html_str




if __name__ == "__main__":
    datapath = "/Users/4pz/kbase/antismash1/test_local/workdir/tmp/2b985128-bdef-4408-a9d3-829011770256"
    AP = BGCCounter(datapath)
    html = AP.get_bgc_table()
    print (html)

