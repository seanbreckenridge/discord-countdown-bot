
import json
import time

class User:

    def __init__(self, id):
        self.id = id

    def __repr__(self): return f"User({self.id})"

    def __str__(self): return __repr__()

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        else:
            raise NotImplementedError("User comparison with unknown type: '{}'".format(type(other)))


class ChannelCache:
    # updated whenever channel related perms change, and before a channel related error is thrown
    def __init__(self, server_object):
        self.reinitialize(server_object)

    def reinitialize(self, server_object):
        """Reitinitializes a representation of a server - the channels and categories"""
        self.categories = {}
        self.channels = []

        for text_channel in server_object.text_channels:
            self.channels.append(text_channel)

        for category in server_object.categories:
            self.categories[category.id] = []
            for text_channel in category.text_channels:
                self.categories[category.id].append(text_channel)

    def channel_exists(self, channel_name:str) -> Bool:
        """Returns a Bool representing whether 'channel_name' the name exists or not"""
        for channel_obj in self.channels:
            if channel_obj.name.casefold() == channel_name.casefold():
                return True
        return False

    def category_exists(self, category_name:str) -> Bool:
        """Returns a Bool representing whether 'category_name' by the name exists or not"""
        for id, category_obj in self.categories.items():
            if category_obj.name.casefold() == category_name.casefold():
                return True
        return False


class Server:

    _server_ids = set()  # prevents multiple server instances with the same id

    def __init__(self, server_object): # constructor
        if server_object.id in Server._server_ids:
            raise RuntimeError("A server instance with the id {} already exists: {}".format(server_object.id, str(list(Server._server_ids))))
        self.server_id = server_object.id
        self.channel_cache = ChannelCache(server_object)
        self.disallowed_channels = [] # save both the name and id
        self.disallowed_categories = []
        Server._server_ids.add(server_object.id)

    def to_json(self):
        """Returns a string that contains the contents of this server instance"""
        return json.dumps({"server_id": self.server_id,
                        "disallowed_channels": self.disallowed_channels,
                        "disallowed_categories": self.disallowed_categories})


    def update_from_json(self, json_obj):
        """Construct a Server from the to_json representation"""
        s.disallowed_channels.extend(list(map(int, json_obj["disallowed_channels"])))
        s.disallowed_categories.extend(list(map(int, json_obj["disallowed_categories"])))


    # Wrappers for cache functions

    def channel_exists(self):
        return self.channel_cache.channel_exists()

    def category_exists(self):
        return self.channel_cache.category_exists()
