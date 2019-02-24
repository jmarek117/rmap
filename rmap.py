#!/usr/bin/python3
import praw

class application():

    def __init__(self):
        self.subreddits = {}
        self.redditors = {}
        self.reddit = praw.Reddit('bot1')

    # takes name of redditor, returns rmap.Redditor
    def get_redditor(self, redditor):
        if redditor not in self.redditors:
            self.redditors[redditor] = Redditor(self.reddit.redditor(redditor))
        return self.redditors[redditor]

    # takes name of subreddit, returns rmap.Subreddit
    def get_subreddit(self, subreddit):
        if subreddit not in self.subreddits:
            self.subreddits[subreddit] = Subreddit(self, self.reddit.subreddit(subreddit))
        return self.subreddits[subreddit]


class Redditor():


    def __init__(self, account):
        self.account = account
        self.communities = {}
        self.comment_limit=50

    def get_active_communities(self, application):
        # loop through comments to find communities user interacts with
        if len(self.communities) == 0:
            for comment in self.account.comments.new(limit=self.comment_limit):
                sr_name = comment.subreddit.display_name
                if sr_name in self.communities:
                    self.communities[sr_name] += 1
                else:
                    self.communities[sr_name] = 1

            ## loop through upvotes to find communities user upvotes in
            #for post in self.account.downvoted():
            #    sr_name = post.subreddit.display_name
            #    if sr_name in self.communities:
            #        self.communities[sr_name] += 1
            #    else:
            #        self.communities[sr_name] = 1

            # loop through downvotes to find communities user downvotes in
            #for post in self.account.upvoted():
            #    sr_name = post.subreddit.display_name
            #    if sr_name in self.communities:
            #        self.communities[sr_name] += 1
            #    else:
            #        self.communities[sr_name] = 1
            self.communities = sorted(self.communities, key=self.communities.get, reverse=True)
        return self.communities

    def print_communities(self, application):
        for subreddit in sorted(self.communities, key=self.communities.get, reverse=True):
            print("r/" + subreddit + ": " + str(self.communities[subreddit]))

    def print_comments(self, application):
        for comment in self.account.comments.new(limit=self.comment_limit):
            print("Subbredit: " + comment.subreddit.display_name + " score: " + str(comment.score))


class Subreddit():


    def __init__(self, application, sr):
        self.sr = sr
        self.application = application
        self.topPosters = []
        self.hotPosters = []
        self.post_limit = 50

    def hot_posters(self, application):
        if len(self.hotPosters) == 0:
            posts = self.sr.hot(limit=self.post_limit)
            commiters = {}
            for post in posts:
                author = application.get_redditor(post.author.name)
                if author in commiters:
                    commiters[post.author.name] += 1
                else:
                    commiters[post.author.name] = 1

            self.hotPosters = [(k, commiters[k]) for k in sorted(commiters, key=commiters.get, reverse=True)]
        return self.hotPosters

    def top_posters(self, application):
        if len(self.topPosters) == 0:
            posts = self.sr.new(limit=self.post_limit)
            commiters = {}
            for post in posts:
                author = application.get_redditor(post.author.name)
                if author in commiters:
                    commiters[post.author.name] += 1
                else:
                    commiters[post.author.name] = 1

            self.topPosters = [(k, commiters[k]) for k in sorted(commiters, key=commiters.get, reverse=True)]
        return self.topPosters

    def print_top_posters(self):
        for k, v in self.topPosters:
            try:
                if v > 1:
                    print("user: " + k + " posts: " + str(v))
            except:
                print("error")

    def print_hot_posters(self):
        print("===== Hot Posters =====")
        for k, v in self.hotPosters:
            try:
                if v > 1:
                    print("user: " + k + " posts: " + str(v))
            except:
                print("error")

    def get_cloud(self, application, depth=1):
        cloud = []    # List of sets. Each set represents a level in our subreddit cloud
        users = set()    # Set of users that have been discovered

        # Fill in initial information
        cloud.append(set())
        for user in self.top_posters(application):
            if user[0] not in users:
                users.add(user[0])
                for sr in application.get_redditor(user[0]).get_active_communities(application):
                    cloud[0].add(sr)

        for x in range(1,depth):
            cloud.append(set())
            for sr in cloud[x-1]:
                for user in application.get_subreddit(sr).top_posters():
                    # Still allows for a subreddit to exist in multiple rings. Will need to be filtered out
                    if user[0] not in users:
                        users.add(user[0])
                        for subreddit in application.get_redditor(user[0]).get_active_communities(application):
                            cloud[x].add(subreddit)
        return cloud


app = application()
#subreddit_name = str(input("Enter subreddit name r/"))
#
#sub = Subreddit(reddit, subreddit_name)
#
#sub.print_top_posters()
#sub.print_hot_posters()

#redditor_name = str(input("Enter user name u/"))
#acc = app.get_redditor(redditor_name)
#acc.print_comments(app)
#acc.get_active_communities(app)
#acc.print_communities(app)

subreddit_name = str(input("Enter subreddit name r/"))
for layer in app.get_subreddit(subreddit_name).get_cloud(app):
    for subreddit in layer:
        print(subreddit)
