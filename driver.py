#https://developer.basespace.illumina.com/docs/content/documentation/native-apps/spacedock-conventions#UploadResultstoBaseSpacewithProperties

import glob, json, os, subprocess, sys

#most files are in /opt/files, so switch to it and use as a working directory
os.chdir('/opt/files')

#decompress reference fasta file
print('Decompressing reference fasta...')
subprocess.check_call(['gunzip', 'all_sequences.fa.gz'])
print('Done decompressing')

#download and setup VEP cache
print('Downloading VEP cache, this may take a while...')
subprocess.check_call(['curl', '-OsS', 'ftp://ftp.ensembl.org/pub/release-90/variation/VEP/homo_sapiens_vep_90_GRCh38.tar.gz'])
print('Download complete. Unpacking...')
subprocess.check_call(['tar', 'xzf', 'homo_sapiens_vep_90_GRCh38.tar.gz'])
print('Unpacking complete')


#get basespace related properties/metadata
with open("/data/input/AppSession.json") as a_s_j:
    appsession = json.load(a_s_j)

#finding the ID of the project from which this analysis was launched; this is needed in order
#to create the directory structure specified by basespace for automatic result uploading
for e in appsession['Properties']['Items']:
    if e['Name'] == 'Input.Projects':
        project_id = e['Items'][0]['Id'] #note that this will return a unicode object, not a str; this is still python 2.7.x, so these are 2 different things
    if e['Name'] == 'Input.Files':
        file_href = e['Items'][0]['Href'] #note that this is a hardcoded example; there may be multiple requiring more complex logic in production
appsession_href = appsession['Href'] #basespace internal reference to the current appsession

cram_search = glob.glob('/data/input/appresults/*/*.cram')
if len(cram_search) != 1:
    print('Error- expected 1 cram file but found {0}'.format(len(cram_search)))
    sys.exit(1)
crai_search = glob.glob('/data/input/appresults/*/*.crai')
if len(crai_search) != 1:
    print('Error- expected 1 crai file but found {0}'.format(len(cram_search)))
    sys.exit(1)

cram_file = cram_search[0]
crai_file = crai_search[0]
name = cram_file.split("/")[-1].split(".")[0]

#basespace-specified directory structure: /data/output/appresults/<project-id>/[directory_with_appresult_name]/[your_files]
output_base = "/data/output/appresults/" + project_id + "/{0}" 

json_dict = {}
json_dict["Cram"] = cram_file
json_dict["CramIndex"] = crai_file
json_dict["Name"] = name
json_dict["OutputDir"] = "/data/output/appresults/{0}".format(project_id)

#with open("/opt/files/inputs.json") as f:


curr_output_dir = output_base.format("example_output")
os.makedirs(curr_output_dir)
curr_outfile = curr_output_dir + "/inputs.json"

with open(curr_outfile, "w+") as f:
    json.dump(json_dict, f)

metadata_outfile = curr_output_dir + "/_metadata.json"

#TODO the properties list may need to be dynamically generated from fields in AppSession.json
metadata_json_template = \
{
    "Name": "",
    "Description": "",
    "HrefAppSession": "",
    "Properties": [
        {
            "Type": "file[]",
            "Name": "Input.Files",
            "Items": [
            
		]
        }
    ]
}

#these are specific to the test case and are being hardcoded; should be dynamically generated in production
metadata_json_template["Name"] = "example_output" #must match dirname at the trailing end of $curr_output_dir
metadata_json_template["Description"] = "test inputs file as output"
metadata_json_template["HrefAppSession"] =  appsession_href
metadata_json_template['Properties'][0]['Items'].append(file_href)

with open(metadata_outfile, "w+") as f:
    json.dump(metadata_json_template, f)

second_tester = curr_output_dir + "/another_file.json"
with open(second_tester, "w+") as f:
    json.dump(metadata_json_template, f)
