1. env variables

  export PYTHONPATH=$OPENFRAME_HOME/python:$PYTHONPATH
  export PATH=$PATH:$OPENFRAME_HOME/python

2. CSV column definition

  DSN      = dataset name
  COPYBOOK = copybook name for dsmigin
  RECFM    = record format
  LRECL    = logical record length
  BLKSIZE  = block size
  DSORG    = dataset organization
  VOLSER   = volume serial
  VSAM     = vsam type (KSDS/RRDS/ESDS)
  KEYOFF   = key offset
  KEYLEN   = key length
  MAXLRECL = max logical length
  AVGLRECL = average logical length
  CISIZE   = cisize
  IGNORE   = ignore or skip this row
  FTP      = ftp this row (Y: Yes, N: No, F: Force)
  FTPDATE  = date stamp when if was been fpt'ed
  FTPTIME  = elapse time for ftp
  DSMIGIN  = dsmigin this row (Y: Yes, N: No, F: Force)
  DSMIGINDATE = date stamp when if was been dsmigin'ed. option -D C will not update this column.
  DSMIGINTIME = elapse time for dsmigin. option -D C will not update this column.

3. dsmigin.py options

4. How to use

  4.1 FTP
    - move to /opt/migration/<application>
    - create working directory where the data will be stored (ex. data)
    - use option -W <directory> or --work-directory=<directory> when triggering dsmigin.py
    - use option -F Y or --ftp=Y option to trigger the ftp when triggering dsmigin.py
    - use option -N or --number option to set number of datasets to be downloaded
    
  4.2 DSMIGIN
    - move to /opt/migration/<application>
    - create copybook folder and place coresponding copybook which has been defined in CSV file
    - execute dsmigin.py with -D Y or --dsmigin=Y option
    - use -D C --dsmigin=C to do convert only for testing

5. Example

  5.1 ftp only while downloading only 10 dataset
    - cd /opt/nfs_share/migration/isb
    - dsmigin.py -I MASTER.csv -W data --ftp=Y --number=10

