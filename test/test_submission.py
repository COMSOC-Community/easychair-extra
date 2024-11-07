import os
from unittest import TestCase

from easychair_extra.read import read_committee, read_submission
from easychair_extra.submission import bid_similarity, topic_similarity


class TestSubmission(TestCase):
    def test_bid_similarity(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        committee = read_committee(
            os.path.join(current_dir, "..", "easychair_sample_files", "committee.csv"),
            bids_file_path=os.path.join(
                current_dir, "..", "easychair_sample_files", "bidding.csv"
            ),
        )
        submissions = read_submission(
            os.path.join(current_dir, "..", "easychair_sample_files", "submission.csv")
        )
        bid_level_weights = {"yes": 1, "maybe": 0.5}
        bid_similarity(submissions, committee, bid_level_weights)

    def test_topic_similarity(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        submissions = read_submission(
            os.path.join(current_dir, "..", "easychair_sample_files", "submission.csv")
        )
        with self.assertRaises(ValueError):
            topic_similarity(submissions)

        sub_topic_file = os.path.join(
            current_dir, "..", "easychair_sample_files", "submission_topic.csv"
        )
        submissions = read_submission(
            os.path.join(current_dir, "..", "easychair_sample_files", "submission.csv"),
            submission_topic_file_path=sub_topic_file,
        )
        topic_similarity(submissions)
