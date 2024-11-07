import os.path
from itertools import chain, combinations
from unittest import TestCase

from easychair_extra.read import (
    read_submission,
    authors_as_list,
    author_list_to_str,
    read_topics,
    read_committee,
)


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


class TestRead(TestCase):
    def test_authors_as_list(self):
        authors = "   Simon Rey   "
        assert authors_as_list(authors) == ["Simon Rey"]
        authors = "Simon Rey    and    Ulle Endriss"
        assert authors_as_list(authors) == ["Simon Rey", "Ulle Endriss"]
        authors = "Simon Rey, Anauthor Withandin Name, Ulle Endriss"
        assert authors_as_list(authors) == [
            "Simon Rey",
            "Anauthor Withandin Name",
            "Ulle Endriss",
        ]
        authors = "Simon Rey, Anauthor Withandin Name and Ulle Endriss"
        assert authors_as_list(authors) == [
            "Simon Rey",
            "Anauthor Withandin Name",
            "Ulle Endriss",
        ]
        authors = "Simon Rey, Anauthor Withandin Name, and Ulle Endriss"
        assert authors_as_list(authors) == [
            "Simon Rey",
            "Anauthor Withandin Name",
            "Ulle Endriss",
        ]
        authors = "Simon Rey,, Anauthor Withandin Name,,, and Ulle Endriss"
        assert authors_as_list(authors) == [
            "Simon Rey",
            "Anauthor Withandin Name",
            "Ulle Endriss",
        ]
        authors = "Simon Rey and Anauthor Withandin Name and Ulle Endriss"
        with self.assertRaises(ValueError):
            authors_as_list(authors)

    def test_author_list_to_str(self):
        author_list = ["Simon Rey"]
        assert author_list_to_str(author_list) == "Simon Rey"
        author_list = ["Simon Rey", "Ulle Endriss"]
        assert author_list_to_str(author_list) == "Simon Rey and Ulle Endriss"
        author_list = ["Simon Rey", "Ulle    Endriss"]
        assert author_list_to_str(author_list) == "Simon Rey and Ulle    Endriss"
        author_list = ["Simon Rey", "Ulle Endriss", "Ronald de Haan"]
        assert (
            author_list_to_str(author_list)
            == "Simon Rey, Ulle Endriss and Ronald de Haan"
        )

    def test_read_topics(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        areas_to_topics, topics_to_areas = read_topics(
            os.path.join(current_dir, "..", "easychair_sample_files", "topics.csv")
        )
        assert len(areas_to_topics) == 13
        for area, topics in areas_to_topics.items():
            for topic in topics:
                assert topics_to_areas[topic] == area
        for topic, area in topics_to_areas.items():
            assert topic in areas_to_topics[area]
        assert len(topics_to_areas) == 300 - 13 - 1  # #lines - #areas - #header

    def test_read_submission(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(current_dir, "..", "easychair_sample_files")

        areas_to_topics, topics_to_areas = read_topics(
            os.path.join(root_dir, "topics.csv")
        )

        optional_arguments = {
            "submission_topic_file_path": os.path.join(
                root_dir, "submission_topic.csv"
            ),
            "author_file_path": os.path.join(root_dir, "author.csv"),
            "review_file_path": os.path.join(root_dir, "review.csv"),
            "remove_deleted": False,
            "remove_desk_reject": False,
            "topics_to_areas": topics_to_areas,
        }

        for arguments in powerset(optional_arguments):
            args = {}
            for arg in arguments:
                args[arg] = optional_arguments[arg]
            read_submission(os.path.join(root_dir, "submission.csv"), **args)

        subs = read_submission(os.path.join(root_dir, "submission.csv"))
        assert len(subs[subs["deleted?"] == "yes"].index) == 0
        assert len(subs[subs["decision"] == "desk reject"].index) == 0
        subs = read_submission(
            os.path.join(root_dir, "submission.csv"), remove_deleted=False
        )
        assert len(subs[subs["deleted?"] == "yes"].index) > 0
        subs = read_submission(
            os.path.join(root_dir, "submission.csv"), remove_desk_reject=False
        )
        assert len(subs[subs["decision"] == "desk reject"].index) > 0

    def test_read_committee(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(current_dir, "..", "easychair_sample_files")

        areas_to_topics, topics_to_areas = read_topics(
            os.path.join(root_dir, "topics.csv")
        )

        optional_arguments = {
            "committee_topic_file_path": os.path.join(root_dir, "committee_topic.csv"),
            "bids_file_path": os.path.join(root_dir, "bidding.csv"),
            "topics_to_areas": topics_to_areas,
        }

        for arguments in powerset(optional_arguments):
            args = {}
            for arg in arguments:
                args[arg] = optional_arguments[arg]
            read_committee(os.path.join(root_dir, "committee.csv"), **args)
