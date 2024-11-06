import os.path
from itertools import chain, combinations
from unittest import TestCase

from easychair_extra.read import read_submission, authors_as_list, author_list_to_str, read_topics


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class TestRead(TestCase):
    def test_authors_as_list(self):
        authors = "   Simon Rey   "
        assert authors_as_list(authors) == ["Simon Rey"]
        authors = "Simon Rey    and    Ulle Endriss"
        assert authors_as_list(authors) == ["Simon Rey", "Ulle Endriss"]
        authors = "Simon Rey, Anauthor Withandin Name, Ulle Endriss"
        assert authors_as_list(authors) == ["Simon Rey", "Anauthor Withandin Name", "Ulle Endriss"]
        authors = "Simon Rey, Anauthor Withandin Name and Ulle Endriss"
        assert authors_as_list(authors) == ["Simon Rey", "Anauthor Withandin Name", "Ulle Endriss"]
        authors = "Simon Rey, Anauthor Withandin Name, and Ulle Endriss"
        assert authors_as_list(authors) == ["Simon Rey", "Anauthor Withandin Name", "Ulle Endriss"]
        authors = "Simon Rey,, Anauthor Withandin Name,,, and Ulle Endriss"
        assert authors_as_list(authors) == ["Simon Rey", "Anauthor Withandin Name", "Ulle Endriss"]

    def test_author_list_to_str(self):
        author_list = ["Simon Rey"]
        assert author_list_to_str(author_list) == "Simon Rey"
        author_list = ["Simon Rey", "Ulle Endriss"]
        assert author_list_to_str(author_list) == "Simon Rey and Ulle Endriss"
        author_list = ["Simon Rey", "Ulle    Endriss"]
        assert author_list_to_str(author_list) == "Simon Rey and Ulle    Endriss"
        author_list = ["Simon Rey", "Ulle Endriss", "Ronald de Haan"]
        assert author_list_to_str(author_list) == "Simon Rey, Ulle Endriss and Ronald de Haan"

    def test_read_topics(self):
        read_topics(os.path.join("..", "easychair_sample_files", "topics.csv"))

    def test_read_submission(self):
        root_dir = os.path.join("..", "easychair_sample_files")

        optional_arguments = {
            "submission_topic_file_path": os.path.join(root_dir, "submission_topic.csv"),
            "author_file_path": os.path.join(root_dir, "author.csv"),
        }

        for arguments in powerset(optional_arguments):
            args = {}
            for arg in arguments:
                args[arg] = optional_arguments[arg]
            read_submission(os.path.join(root_dir, "submission.csv"), **args)

