import os
from unittest import TestCase

from easychair_extra.programcommittee import papers_without_pc
from easychair_extra.read import read_committee, read_submission


class TestProgramCommittee(TestCase):
    def test_papers_without_pc(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        committee = read_committee(
            os.path.join(current_dir, "..", "easychair_sample_files", "committee.csv"),
            bids_file_path=os.path.join(current_dir, "..", "easychair_sample_files", "bidding.csv"),
        )
        submissions = read_submission(
            os.path.join(current_dir, "..", "easychair_sample_files", "submission.csv")
        )
        with self.assertRaises(ValueError):
            papers_without_pc(committee, submissions)

        author_file = os.path.join(
            current_dir, "..", "easychair_sample_files", "author.csv"
        )
        submissions = read_submission(
            os.path.join(current_dir, "..", "easychair_sample_files", "submission.csv"),
            author_file_path=author_file,
        )
        papers_without_pc(committee, submissions)
        assert "no_author_pc" in submissions.columns
