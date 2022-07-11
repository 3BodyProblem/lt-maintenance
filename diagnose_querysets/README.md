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

    - Supported Policy Names ( `--policy_name=???` ):
       - `triboo_analytics_reportlog`
         ```
            Sample of dump file as follow:
               # FR > Abbott >>>>>>>>>>>
               SELECT * FROM triboo_analytics_reportlog WHERE date(created)>="2021-11-22 ^H";
               +-----+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+
               | id  | created                    | modified                   | learner_visit              | learner_course             | learner                    | course                     | microsite                  | country                    |
               +-----+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+
               | 119 | 2021-11-22 01:40:06.906722 | 2021-11-22 01:40:13.224861 | 2021-11-22 01:40:06.901095 | 2021-11-22 01:40:12.662131 | 2021-11-22 01:40:12.999630 | 2021-11-22 01:40:13.081538 | 2021-11-22 01:40:13.153081 | 2021-11-22 01:40:13.222970 |
               | 120 | 2021-11-23 01:40:06.439054 | 2021-11-23 01:40:09.939896 | 2021-11-23 01:40:06.430946 | 2021-11-23 01:40:09.648886 | 2021-11-23 01:40:09.812521 | 2021-11-23 01:40:09.858002 | 2021-11-23 01:40:09.899777 | 2021-11-23 01:40:09.937358 |
               | 121 | 2021-11-24 01:40:06.720530 | 2021-11-24 01:40:11.557364 | 2021-11-24 01:40:06.713794 | 2021-11-24 01:40:11.218092 | 2021-11-24 01:40:11.394345 | 2021-11-24 01:40:11.460681 | 2021-11-24 01:40:11.514731 | 2021-11-24 01:40:11.555625 |
               ...
               ...
               ...
         ```
       
       - `auth_group`
         ```
            Sample of dump file as follow:
               # US > Griky - Astrazeneca  >>>>>>>>>>> 
               SELECT `name` FROM auth_group;
               +-----------------------------------+
               | name                              |
               +-----------------------------------+
               | Anderspink Denied Users           |
               | API Access Request Approvers      |
               | Catalog Denied Users              |
               | Crehana Denied Users              |
               ...
               ...
               ...
         ```

 - *** Accessible Database ***
   - The default database is specified by connection string of conf/nodes.txt 
