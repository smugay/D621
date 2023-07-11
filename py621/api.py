# This file should probably be renamed since it now contains both public and private api calls, not sure what to name it though
import requests
from py621 import types
import hashlib
import json
import re

# Custom user agent header for identification within e621
headers = {"User-Agent": "py621/1.2.0 (by Bugman69 on e621)"}


def genmd5(file):
    """[Calculates md5 value for a file]

    Args:
        file ([str]): [The path to the file to calculate from]

    Returns:
        [str]: [The calculated md5 value]
    """
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# HTTP Code handler


def handleCodes(StatusCode):
    """[Handles HTTP Status Codes]

    Args:
        StatusCode ([int]): [Status code provided by the server]

    Raises:
        ConnectionRefusedError: [Raised when anything but a status code of 200 is given]
    """

    if StatusCode == 200:
        return
    else:
        Codes = {
            "401": "API Key Error",
            "403": "Forbidden; Access denied",
            "404": "Not found",
            "412": "Precondition failed",
            "420": "Invalid Record; Record could not be saved",
            "421": "User Throttled; User is throttled, try again later",
            "422": "Locked; The resource is locked and cannot be modified",
            "423": "Already Exists; Resource already exists",
            "424": "Invalid Parameters; The given parameters were invalid",
            "500": "Internal Server Error; Some unknown error occurred on the server",
            "502": "Bad Gateway; A gateway server received an invalid response from the e621 servers",
            "503": "Service Unavailable; Server cannot currently handle the request or you have exceeded the request rate limit. Try again later or decrease your rate of requests.",
            "520": "Unknown Error; Unexpected server response which violates protocol",
            "522": "Origin Connection Time-out; CloudFlare's attempt to connect to the e621 servers timed out",
            "524": "Origin Connection Time-out; A connection was established between CloudFlare and the e621 servers, but it timed out before an HTTP response was received",
            "525": "SSL Handshake Failed; The SSL handshake between CloudFlare and the e621 servers failed"}
        try:
            raise ConnectionRefusedError(
                "Server connection refused! HTTP Status code: " + str(StatusCode) + " " + Codes[str(StatusCode)])
        except KeyError:  # This shouldn't happen but if it does this is here just in case
            raise ConnectionRefusedError(
                "Server connection refused! HTTP Status code: " + str(StatusCode) + " Unknown status code")


class apiGet:
    """[An API Instance]

    Args:
        url ([str]): [Uses either py621.types.e926 or py621.types.e621]
        username ([str], optional): [If authenticating, set this to your e621 username]
        APIKey ([str], optional): [If authenticating, set this your e621 API key]
    """

    def __init__(self, url, username=None, APIKey=None):
        self.url = url

        if APIKey != None:
            self.authenticate = True
            self.auth = (username, APIKey)
        else:
            self.authenticate = False

    def isTag(self, Tag):
        """[Checks if a tag is valid]

        Args:
            Tag ([str]): [Tag to be checked]

        Returns:
            [bool/str]: [Returns True if the tag is valid, False if it isn't, and returns a string if the tag is an alias]
        """

        # "Tags" that start with any of these will return as false if tested against the list at tags.json despite being valid search terms so we'll check if they match any of these valid searches listed at https://e621.net/help/cheatsheet
        prefixes = {'user:', 'favoritedby:', 'voted:', 'votedup:', 'voteddown:', 'approver:', 'deletedby:', 'commenter:', 'noteupdater:', 'id:', 'date:', 'filesize:', 'score:', 'favcount:', 'comment_count:', 'tagcount:', 'gentags:', 'arttags:', 'copytags:', 'spectags:', 'invtags:', 'lortags:', 'mpixels:', 'ratio:', 'filesize:', 'duration:', 'rating:', 'type:', 'source:', 'description:', 'notes:', 'delreason:', 'ischild:', 'isparent:', 'parent:', 'status:', 'hassource:', 'hasdesription:', 'ratinglocked:', 'notelocked:', 'inpool:', 'pending_replacement:', 'pool:', 'set:', 'md5:', 'order:'}

        if Tag.startswith(tuple(prefixes)):
            return True

        # Since tags can't inherently be NSFW we will always verify tags on e621
        RequestLink = self.url + "tags.json?"

        RequestLink += "search[name_matches]="
        RequestLink += Tag

        # Sends the actual request
        if self.authenticate == True:
            eRequest = requests.get(
                RequestLink, headers=headers, auth=self.auth)
        else:
            eRequest = requests.get(RequestLink, headers=headers)

        # Verify status codes
        handleCodes(eRequest.status_code)

        # Decodes the json into a list
        eJSON = eRequest.json()

        try:
            # Try to access element name, this throws and error when the tag does not exist or is an alias, check for that in the except
            if eJSON[0]["name"] == Tag:
                return True
            # If the tag's name isn't the tag, assume it's a fluke on e621's servers and return false
            else:
                return False
        except:
            # Redoing the request to check if it's an alias
            RequestLink = "https://e621.net/tag_aliases.json?"

            RequestLink += "search[name_matches]="
            RequestLink += Tag

            # Sends the actual request
            if self.authenticate == True:
                eRequest = requests.get(
                    RequestLink, headers=headers, auth=self.auth)
            else:
                eRequest = requests.get(RequestLink, headers=headers)

            # Verify status codes
            handleCodes(eRequest.status_code)

            # Decodes the json into a a list
            eJSON = eRequest.json()

            try:
                # Try to access element name, this WILL throw and exception if it actually does not exist
                if eJSON[0]["antecedent_name"] == Tag:
                    # Return the actual tag
                    return eJSON[0]["consequent_name"]
                # This shouldn't ever happen, but if it does, consider yourself a special snowflake
                else:
                    return False
            except:
                # This tag really does not exist
                return False

    # Simple function, gets a single post
    def getPost(self, PostID):
        """[Gets a post by it's ID]

        Args:
            PostID ([int/str]): [The ID of the post to get info about]

        Returns:
            [Post]: [Returns a Post object]
        """

        RequestLink = self.url

        RequestLink += "posts/"

        # Specifies the Post ID
        RequestLink += str(PostID)
        RequestLink += ".json"

        # Sends the actual request
        if self.authenticate == True:
            eRequest = requests.get(
                RequestLink, headers=headers, auth=self.auth)
        else:
            eRequest = requests.get(RequestLink, headers=headers)

        # Verify status codes
        handleCodes(eRequest.status_code)

        # Decodes the json into a a list
        eJSON = eRequest.json()

        # Return posts from the previously defined list
        return types.ListToPost(eJSON["post"], self)

    # Simple function, returns a list with posts
    def getPosts(self, Tags, Limit, Page, Check):
        """[Get a list of posts]

        Args:
            Tags ([list]): [List of tags to use]
            Limit ([int]): [Number of posts to return, not guaranteed to return this exact number of posts. Hard limit of 320 imposed by the site]
            Page ([int]): [Page number to start the search from]
            Check ([bool]): [Whether or not to check the tags for validity]

        Returns:
            [List[Post]]: [Returns a list of Post objects]
        """

        RequestLink = self.url

        RequestLink += "posts.json?"

        # Gives a limit of posts to the api (can be used for per page limits when combined with Page)
        RequestLink += "limit="
        RequestLink += str(Limit)

        # Specifies the page
        RequestLink += "&page="
        RequestLink += str(Page)

        # Handles tag formation
        RequestLink += "&tags="

        for id, Tag in enumerate(Tags):
            if Check == True:
                # Check the tag, it could not exist
                TagCheck = self.isTag(Tag)

                if TagCheck == False:
                    # Tag does not exist, throw an error, this can help devs later on
                    raise NameError("Tag (" + Tag + ") does not exist!")
                elif TagCheck == True:
                    # Tag exists and isn't an alias, put it on the request
                    RequestLink += Tag
                else:
                    # Tag is an alias, use the actual tag on the request
                    RequestLink += TagCheck
            else:
                # Don't bother with tag checks
                RequestLink += Tag

            if id != (len(Tags) - 1):
                RequestLink += "+"

        # Sends the actual request
        if self.authenticate == True:
            eRequest = requests.get(
                RequestLink, headers=headers, auth=self.auth)
        else:
            eRequest = requests.get(RequestLink, headers=headers)

        # Verify status codes
        handleCodes(eRequest.status_code)

        # Decodes the json into a a list
        eJSON = eRequest.json()

        # Define a list of posts
        Posts = []

        # For every post on json output convert to Post object and append to list
        for post in eJSON["posts"]:
            Posts.append(types.ListToPost(post, self))

        # Return posts from the previously defined list of Post objects
        return Posts

    # Simple function, returns a pool from a pool ID
    def getPool(self,PoolID):
        """[Gets a Pool by its ID]

        Args:
            PoolID ([str/int]): [The ID of the pool to get]
            Limit ([int]): [Number of posts to return, not guaranteed to return this exact number of posts. Hard limit of 320 imposed by the site]


        Returns:
            [Pool]: [Returns a Pool object]
        """

        RequestLink = self.url

        RequestLink += "pools.json?"

        # Specifies the pool ID
        RequestLink += "?&search[id]=" + str(PoolID)

        # Sends the actual request
        if self.authenticate == True:
            eRequest = requests.get(
                RequestLink, headers=headers, auth=self.auth)
        else:
            eRequest = requests.get(RequestLink, headers=headers)

        # Verify status codes
        handleCodes(eRequest.status_code)

        # Decodes the json into a a list and selects first element (the pool, if there are more, how?)
        eJSON = eRequest.json()[0]
        
        # Returns the pool
        return types.ListToPool(eJSON, self)

    # Simple function, returns a list of posts from a specific pool ID
    def getPoolPosts(self, PoolID):
        """[Gets IDs of posts in a pool]

        Args:
            PoolID ([str/int]): [The ID of the pool to get the posts from]

        Returns:
            [List]: [List of Post objects]
        """

        # Get ID of all posts in a pool
        poolPosts = self.getPool(PoolID).post_ids

        # Sets posts list
        posts = []

        for postID in poolPosts:
            posts.append(self.getPost(postID))

        # Return the posts list
        return posts


class apiPost:
    """
    [Used for uploading posts, creating a new flag, voting on post, creating a note, or creating a new pool]

    Args:
        username ([str]): [Username of the user]
        apiKey ([str]): [The API requires that API access be enabled on the account before it can log in using the API. To enable API access, you must go to your profile page (Account > My profile) and generate an API key.]
    """

    def __init__(self, username, apiKey):
        self.auth = (username, apiKey)

    def createPost(self, file, tags, rating, directURL=None, source=None, description=None, parentID=None, referrerURL=None, asPending=None):  # ! UNFINISHED
        PostLink = "https://e621.net/uploads.json"
        md5 = genmd5(file)
        params = {
            "upload[tag_string]": tags,
            "upload[rating]": rating,
            "upload[direct_url]": directURL,
            "upload[source]": source,
            "upload[description]": description,
            "upload[parent_id]": parentID,
            "upload[referrer_url]": referrerURL,
            "upload[md5_confirmation]": md5,
            "upload[as_pending]": asPending
        }
        params = json.dumps(params)
        uploadFile = {'upload[file]': open(file, 'rb')}
        requestPost = requests.post(
            url=PostLink, files=uploadFile, json=params, headers=headers, auth=self.auth)
        handleCodes(requestPost.status_code)
        return requestPost
        #  Will return {"success":true", "location":"/posts/<Post_ID>", "post_id":<Post_ID>} when successful or {"success": false, "reason": "duplicate", "location": "/posts/<Post_ID>", "post_id": < Post_ID >} when it fails (in this example it failed because the post was a duplicate)
