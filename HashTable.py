class HashTable:

    # Create empty bucket list of given size
    def __init__(self, size):
        self.size = size
        self.hash_table = self.create_buckets()

    def create_buckets(self):
        return [[] for _ in range(self.size)]

    # Insert values into hash map
    def set_val(self, key, val):

        # Get the index from the key
        # using hash function
        hashed_key = hash(key) % self.size

        # Get the bucket corresponding to index
        bucket = self.hash_table[hashed_key]
        bucket.append(val)

    # Return searched value with specific key
    def get_val(self, key):

        # Get the index from the key using
        # hash function
        hashed_key = hash(key) % self.size

        # Get the bucket corresponding to index
        bucket = self.hash_table[hashed_key]
        return bucket

    # Remove a value with specific key
    def delete_val(self, key):

        # Get the index from the key using
        # hash function
        hashed_key = hash(key) % self.size

        # Make entry empty
        self.hash_table[hashed_key] = []



    # To print the items of hash map
    def __str__(self):
        return "".join(str(item) for item in self.hash_table)


# hash_table = HashTable(50)

# hash_table.set_val(123, "hello")
# hash_table.set_val(123, "how")
# hash_table.set_val(123, "are")
#
# hash_table.set_val(234, "fuck")
# hash_table.set_val(234, "you")
# print(hash_table.get_val(123))
# print(hash_table.get_val(234))
