#!/usr/bin/env python
import os
import sys
import logging
import time
import argparse
import configparser
import datetime
import validators
# Start of the fun!
import bin.m2emHelper as helper
import bin.m2emRssParser as mparser
import bin.m2emDownloader as mdownloader
import bin.m2emConverter as mconverter
import bin.m2emSender as msender

#logging.basicConfig(format='%(message)s', level=logging.DEBUG)

class M2em:

    def __init__(self):

        # Python 3 is required!
        if sys.version_info[0] < 3:
            sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
            sys.exit(1)

        # Get args right at the start
        self.args = None
        if not self.args:
            self.read_arguments()

        # Load config right at the start
        self.config = None
        if not self.config:
            self.read_config()

        # Check if Database exists, else create
        if not os.path.isfile(self.config["Database"]):
            helper.createDB(self.config)


    def read_arguments(self):

        # Get user Input
        parser = argparse.ArgumentParser(description='Manga to eManga - m2em')
        parser.add_argument("-af", "--add-feed", help="Add RSS Feed of Manga. Only Mangastream & MangaFox are supported")
        parser.add_argument("-au", "--add-user", help="Adds new user",
                                action="store_true")
        parser.add_argument("-lc", "--list-chapters", help="Lists the last 10 Chapters",
                                action="store_true")
        parser.add_argument("-Lc", "--list-chapters-all", help="Lists all Chapters",
                                action="store_true")
        parser.add_argument("-lf", "--list-feeds", help="Lists all feeds",
                                action="store_true")
        parser.add_argument("-lu", "--list-users", help="Lists all Users",
                                action="store_true")
        parser.add_argument("-cd", "--create-db", help="Creates DB. Uses Configfile for Naming",
                                action="store_true")
        parser.add_argument("-a", "--action", help="Start action. Options are: rss (collecting feed data), downloader, converter or sender ",
                            action="store_true")
        parser.add_argument("-s", "--start", help="Start a single loop. If no arguments are passed, a single loop will also start",
                            action="store_true")
        parser.add_argument("-ss", "--switch-send", help="Pass ID of User. Switches said user Send eBook status")
        parser.add_argument("-sc", "--switch-chapter", help="Pass ID of Chapter. Switches said Chapter Sent status")
        parser.add_argument("-dc", "--delete-chapter", help="Pass ID of Chapter. Deletes said Chapter")
        parser.add_argument("-du", "--delete-user", help="Pass ID of User. Deletes said User")
        parser.add_argument("-df", "--delete-feed", help="Pass ID of Feed. Deletes said Feed")
        parser.add_argument("--daemon", help="Run as daemon",
                                action="store_true")
        parser.add_argument("-d", "--debug", help="Debug Mode",
                                action="store_true")
        self.args = parser.parse_args()

        # Logging
        if self.args.debug:
            logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(message)s', level=logging.INFO)


    #Read Config
    def read_config(self):

        logging.debug("Loading configuration")
        config_reader = configparser.ConfigParser()
        config_reader.read("config.ini")
        self.config = config_reader["CONFIG"]

        # Load Config Variables
        if self.config["SaveLocation"]:
            logging.debug("Succesfully loaded SaveLocation: %s ", self.config["SaveLocation"])
        if self.config["EbookFormat"]:
            logging.debug("Succesfully loaded EbookFormat: %s ", self.config["EbookFormat"])
        if self.config["Database"]:
            logging.debug("Succesfully loaded Database: %s ", self.config["Database"])
        if self.config["Sleep"]:
            logging.debug("Succesfully loaded Database: %s ", self.config["Sleep"])


    '''
    Catch -af/--add-feed
    '''
    def save_feed_to_db(self):
        logging.debug("Entered URL: %s" % self.args.add_feed)
        if validators.url(self.args.add_feed):
            helper.writeFeed(self.args.add_feed, self.config)
        else:
            logging.error("You need to enter an URL!")


    '''
    Catch -s/--switch-user
    '''
    def switch_user_status(self):
        logging.debug("Entered USERID: %s" % self.args.switch_send)
        helper.switchUserSend(self.args.switch_send, self.config)



    '''
    Catch -s/--switch-user
    '''
    def switch_chapter_status(self):
        logging.debug("Entered CHAPTERID: %s" % self.args.switch_chapter)
        helper.switchChapterSend(self.args.switch_chapter, self.config)


    '''
    Delete Stuff functions
    '''
    def delete_user(self):
        logging.debug("Entered USERID: %s" % self.args.delete_user)
        helper.deleteUser(self.args.delete_user, self.config)

    def delete_chapter(self):
        logging.debug("Entered USERID: %s" % self.args.delete_chapter)
        helper.deleteChapter(self.args.delete_chapter, self.config)

    def delete_feed(self):
        logging.debug("Entered USERID: %s" % self.args.delete_feed)
        helper.deleteFeed(self.args.delete_feed, self.config)



    '''    
    Catch --list-feeds
    '''
    def list_feeds(self):
        helper.printFeeds(self.config)


    '''    
    Catch -L/--list-chapters-all
    '''
    def list_all_chapters(self):
        helper.printChaptersAll(self.config)
        pass


    '''    
    Catch -l/--list-chapters
    '''
    def list_chapters(self):
        helper.printChapters(self.config)
        pass


    '''    
    Catch --list-users
    '''
    def list_users(self):
        helper.printUsers(self.config)
        pass


    '''    
    Catch -u/--add-user
    '''
    def add_user(self):
        helper.createUser(self.config)
        pass


    '''    
    Catch -cd/--create-db
    '''
    def create_db(self):
        helper.createDB(self.config)
        pass




    '''
    This are the worker, one round
    '''
    #  Worker to get and parse  rss feeds
    def parse_add_feeds(self):
        mparser.RssParser(self.config)

    # Worker to fetch all images
    def images_fetcher(self):
        mdownloader.ChapterDownloader(self.config)

    # Worker to convert all downloaded chapters into ebooks
    def image_converter(self):
        mconverter.RecursiveConverter(self.config)

    # Worker to convert all downloaded chapters into ebooks
    def send_ebooks(self):
        msender.sendEbook(self.config)



    '''
    Application Run & Daemon loop
    '''
    def run(self):

        if self.args.add_feed:
            self.save_feed_to_db()
            return

        if self.args.switch_send:
            self.switch_user_status()
            return

        if self.args.list_feeds:
            self.list_feeds()
            return

        if self.args.list_chapters_all:
            self.list_all_chapters()
            return

        if self.args.list_chapters:
            self.list_chapters()
            return

        if self.args.add_user:
            self.add_user()
            return

        if self.args.list_users:
            self.list_users()
            return


        if self.args.switch_chapter:
            self.switch_chapter_status()
            return


        if self.args.delete_user:
            self.delete_user()
            return


        if self.args.delete_chapter:
            self.delete_chapter()
            return


        if self.args.delete_feed:
            self.delete_feed()
            return

        if self.args.create_db:
            self.create_db()
            return


        # Mainloop
        loop = True
        while loop:
            if not self.args.daemon:
                loop = False

            logging.info("Starting Loop at %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            logging.info("Starting RSS Data Fetcher!")
            self.parse_add_feeds()
            logging.info("Finished Loading RSS Data")

            logging.info("Starting all outstanding Chapter Downloads!")
            self.images_fetcher()
            logging.info("Finished all outstanding Chapter Downloads")

            logging.info("Starting recursive image conversion!")
            self.image_converter()
            logging.info("Finished recursive image conversion!")

            logging.info("Starting to send all ebooks!")
            self.send_ebooks()
            logging.info("Finished sending ebooks!")

            if loop:
                logging.info("Sleeping for %s seconds...\n" % (self.config["Sleep"]))
                time.sleep(int(self.config["Sleep"]))

# Execute Main
if __name__ == '__main__':
    me = M2em()
    me.run()
