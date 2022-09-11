import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import praw, requests, feedparser, hashlib

#Gives required information to be able to use praw
reddit = praw.Reddit(
    client_id = "r1vCPbjKDhDglkhzesRtKQ",
    client_secret = "vstXTT-X0JhBOpPdnKiqzOfzNBMUfA",
    user_agent = "Hillgo"
)

#Class for getting posts
class get_post():
    def __init__(self, subreddit, file_type):
        self.subreddit = subreddit  #Makes it sort by hot and take the top 50 posts
        self.file_type = file_type
        self.posts_dict= {"Title": [], "ID": [], "Score": [], "Total Comments": [], "Post URL": []} #Creates a dictionary to save data about posts
        self.title = []
        self.url = []

    def df(self):
        #For each post in hot top 50 adds the title, user id, upvotes, amount of comments and the post"s url
        for post in self.subreddit:
            if not post.stickied == True: #Skips posts that're pinned
                if ".jpg" in post.url or ".png" in post.url:
                    
                    self.posts_dict["Title"].append(str(post.title))
                    self.posts_dict["ID"].append(str(post.id))
                    self.posts_dict["Score"].append(str(post.score))
                    self.posts_dict["Total Comments"].append(str(post.num_comments))
                    self.posts_dict["Post URL"].append(str(post.url))
                    self.title.append(post.title)
                    self.url.append(post.url)

    def export(self):
        top_posts = pd.DataFrame(self.posts_dict) #Transforms the data into a dataform

        top_posts.to_json("Top Posts" + self.file_type) #Exports data into requested file type

    #Runs previous class functions
    def run(self):
        Get_Post.df()
        Get_Post.export()

#Class for downloading the posts images
class get_images():   
    #Defines variables for class
    def __init__(self, save_folder):
        self.saved_images = []
        self.saved_image_file = "saved_image_hashes.txt" #Selects what file to store hashes, the code uses the hashes to 
        #make sure that the same post isn't downloaded more than once
        self.save_folder = save_folder
        self.illegal_filepath_characters = ["<", ">", ":", "'", "/", "\\", "|", "?", "*"] #Creates a list of characters that can't bega in a file path
        
        self.urls = ["https://www.reddit.com/r/cursedimages/.rss?limit=50"] #Subreddit to look through and amount of posts to download

    def get_previous_hashes(self): #Function to check if hashes are already in "saved_image_file"
        print("Getting previous image hashes")

        f = open(self.saved_image_file)
        self.saved_images = f.read().splitlines()
        f.close()

        print("Found {} previously saved image hashes".format(len(self.saved_images)))
        print("\n")

    def update_hashes(self): #Function to update the "saved_image_file" with hashes for the new downloads
        print("Updating saved file")

        f = open(self.saved_image_file, "w")
        for hash in self.saved_images: #For each saved image it makes a hash using the "hashlib" library
            f.writelines(hash + "\n") #It writes down the created hash in the file
        f.close()

        print("Updated saved file")



    def save_file(self, file_name, file_url): #The function used for downloading the images
        try:
            response = requests.get(file_url) #Uses the "request" module to get information about the image's url
            extension = response.headers["content-type"].split("/")[1] #Gets the extension of the image (aka, .png or .jpg)

        except: #If the previous url was invalid
            print("Url was invalid and could not be requested {}".format(file_url))
            return

        if (not self.is_image(extension)): #Calls the "is_image" to check if extension is an image or not
            print("{file_name} was not a image it was {extension} and has not been saved".format(file_name = file_name, extension = extension))
            print("\n")
            return

        file_hash = hashlib.md5(response.content).hexdigest() #Gets the hash from the imags's url

        if(file_hash not in self.saved_images): #Check if hash is in list containg hashes
            try:
                #Opens the downloaded file in the requested folder 
                f = open("{save_folder}{name}_{hash}.{extension}".format(save_folder = self.save_folder, name = file_name, hash = file_hash, extension = extension), "wb")
                f.write(response.content) #Writes down the image
                f.close()

            except:
                print("The file could not be saved! {}".format(file_name))
                return

            self.saved_images.append(file_hash) #Adds the hash to a list containg saved images

        else: #If the file is already saved
            print("{file_name} is a duplicate! and will not be saved again".format(file_name = file_name))
            print("\n")
        print("\n")
        
    def is_image(self, extension): #Checks if the file is an image
        if("html" in extension or "charset" in extension):
            return False
        return True


    def remove_illegal_filepath_characters(self, file_name): #Function to remove the illegal characters that were defined in the "__init__" function from filenames
        sanitizedfile_name = file_name 

        for character in self.illegal_filepath_characters: #Removes the illegal characters
            sanitizedfile_name = sanitizedfile_name.replace(character, "")
        
        return sanitizedfile_name #Returns the new file name

    def run(self): #The main function for running the class
        self.get_previous_hashes() #Calls the "get_previous_hashes" function to check for duplicates

        for url in self.urls:
            print("Beginning download for: {}".format(url))
            print("\n")

            feed = feedparser.parse(url) #Gets the feed from the requested subreddit through it's url

            for post in feed.entries:               
                soup = BeautifulSoup(post.content[0].value, "html.parser") #Uses the "BeautifulSoup" module to scrape the subreddit feed
                file_name = self.remove_illegal_filepath_characters(post.title) #Creates the downloads name through getting the original posts title and removing illegal characters
                file_url = soup.find("span").find("a").get("href") #Looks through the scraped html file to find the url for the post's image

                print("Saving:")
                print("Name: " + file_name)
                print("Url: " + file_url)

                self.save_file(file_name, file_url) #Calls the "save_file" function

        self.update_hashes() #Calls the "update_hashes" function

Get_Post = get_post(reddit.subreddit("cursedimages").hot(limit = 50), ".json") #Selects what subreddit to look through and the file type it exports to
Get_Images = get_images("./Images/") #Selects where to place the downloadeded files

#Runs code
def main():
    Get_Images.run()
    Get_Post.run()

if __name__ == "__main__":
    main()