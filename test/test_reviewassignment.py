import os.path
from unittest import TestCase

from easychair_extra.read import read_submission, read_committee
from easychair_extra.reviewassignment import (
    committee_to_bid_profile,
    find_feasible_review_assignment,
    find_emergency_reviewers,
)


class TestReviewAssignment(TestCase):
    def test_find_feasible_review_assignment(self):
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

        reviewers = committee[committee["role"] == "PC member"]

        bid_level_weights = {"yes": 1, "maybe": 0.5}
        bid_profile = committee_to_bid_profile(
            reviewers, submissions, bid_level_weights
        )

        find_feasible_review_assignment(
            bid_profile,
            bid_level_weights,
            3,
            3,
        )

    def test_find_emergency_reviewers(self):
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

        reviewers = committee[committee["role"] == "PC member"]

        bid_level_weights = {"yes": 1, "maybe": 0.5}
        bid_profile = committee_to_bid_profile(
            reviewers, submissions, bid_level_weights
        )

        for verbose in [True, False]:
            find_emergency_reviewers(bid_profile, bid_level_weights, 3, verbose=verbose)
