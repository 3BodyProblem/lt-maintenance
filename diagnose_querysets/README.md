 - Python
    - Version == 2.7

 - Install Py libraries:
    - pip install -r requirements.txt
   
 - Help
    - `python -m diagnose_querysets --help`
   
 - Run script
    - `python -m diagnose_querysets --cert_folder=/Users/barrypaneer/.ssh/ --fr_mysql_pswd=[...] --us_mysql_pswd=[...] --policy_name=triboo_analytics_reportlog`
       - `--policy_name` is a mandatory argument. We could get valid policy list by argument `--help` .
       - `--cert_folder` is the folder of ssl cert pem files.
       - At least one of pswd should be specified.
    - Output: 
       - A SSL Shell Echo dump file (Sample: `./analytics_2021-11-22.dump`)

 - *** Accessible Database ***
   - The default database is specified by connection string of conf/nodes.txt 
