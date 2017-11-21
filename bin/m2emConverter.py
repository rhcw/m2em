import logging
import os
import zipfile
import subprocess
import bin.m2emHelper as helper


class Converter:

    def __init__(self):
        self.saveloc        = None
        self.ebformat       = None
        self.ebprofile      = None
        self.mangatitle     = None
        self.manganame      = None
        self.imagefolder    = None
        self.eblocation     = None
        self.cbzlocation    = None
        self.chapterdate    = None



    def data_collector(self, config, chapter):

        # Load configs required here
        self.saveloc   = config["SaveLocation"]
        self.ebformat  = config["EbookFormat"]
        self.ebprofile = config["EbookProfile"]


        # get relevant data of this Manga
        self.mangatitle   = chapter[2]
        self.manganame    = chapter[11]
        self.chapterdate  = chapter[3]

        # check if mangatitle or manganame contains ":" characters that OS can't handle as folders
        self.mangatitle = helper.sanetizeName(self.mangatitle)
        self.manganame = helper.sanetizeName(self.manganame)


        # create folder variables
        self.imagefolder  = str(self.saveloc + self.manganame + "/"+  self.mangatitle + "/images/")
        self.eblocation   = str(self.saveloc + self.manganame + "/"+  self.mangatitle + "/" + self.mangatitle + "." + self.ebformat.lower())
        self.cbzlocation  = str(self.saveloc + self.manganame + "/"+ self.mangatitle + "/" + self.mangatitle + ".cbz")




    def cbz_creator(self):

        # Create CBZ to make creation easier
        if os.path.exists(self.cbzlocation):
            logging.debug("Manga %s converted to CBZ already!" % self.mangatitle)
        else:
            logging.info("Starting conversion to CBZ of %s..." % self.mangatitle)


            logging.debug("Opening CBZ archive...")
            try:
                zf = zipfile.ZipFile(self.cbzlocation, "w")
            except Exception as e:
                logging.warning("Failed opening archive! %s" % e)



            logging.debug("Writing Images into CBZ")
            for img in sorted(os.listdir(self.imagefolder)):
                image = self.imagefolder + img
                logging.debug("Writing %s" % image)
                zf.write(image,img)

            zf.close()



    def eb_creator(self):

        # Start conversion to Ebook format!
        if os.path.exists(self.eblocation):
            logging.debug("Manga %s converted to Ebook already!" % self.mangatitle)
        else:
            logging.info("Starting conversion to Ebook of %s..." % self.mangatitle)

            try:
                subprocess.call(["kcc-c2e", "-p", self.ebprofile, "-f", self.ebformat, "-m", "-q", "-r",  "2", "-u", "-s",  self.cbzlocation])
            except Exception as e:
                logging.debug("Failed to convert epub %s" % e)
