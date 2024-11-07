from __future__ import annotations

import os

from easychair_extra.read import read_committee, read_submission
from easychair_extra.reviewassignment import (
    find_feasible_review_assignment,
    committee_to_bid_profile,
)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Read the committee file with the bids
    committee = read_committee(
        os.path.join(current_dir, "..", "easychair_sample_files", "committee.csv"),
        bids_file_path=os.path.join(current_dir, "..", "easychair_sample_files", "bidding.csv"),
    )

    # Read the submission file
    submissions = read_submission(
        os.path.join(current_dir, "..", "easychair_sample_files", "submission.csv")
    )

    # Select reviewers and not higher up PC members
    reviewers = committee[committee["role"] == "PC member"]

    # Define the weights of the bids and compute the bidding profile
    bid_level_weights = {"yes": 1, "maybe": 0.5}
    bid_profile = committee_to_bid_profile(reviewers, submissions, bid_level_weights)

    print("\n" + "=" * 43 + "\n   Looking for the smallest review quota\n" + "=" * 43)
    # Required number of reviewers per paper
    number_review_per_paper = 3
    total_num_reviews_needed = len(submissions.index) * number_review_per_paper

    # Iteratively increase the maximum number of reviews per reviewer until finding an assignment
    # that covers everything.
    reviewers_assignment = {}
    number_max_review_per_reviewer = 0
    num_assigned_previous = 0
    while sum(len(p) for p in reviewers_assignment.values()) < total_num_reviews_needed:
        number_max_review_per_reviewer += 1
        # Compute the review assignment
        reviewers_assignment = find_feasible_review_assignment(
            bid_profile,
            bid_level_weights,
            number_max_review_per_reviewer,
            number_review_per_paper,
        )
        # Print info about the new assignment
        if reviewers_assignment:
            num_assigned = sum(len(p) for p in reviewers_assignment.values())
            print(
                f"\tFOUND: Assignment with {number_review_per_paper} reviews per paper and a "
                f"maximum of {number_max_review_per_reviewer} reviews per reviewers: "
                f"{num_assigned} reviews in total for {total_num_reviews_needed} needed."
            )
            if num_assigned == num_assigned_previous:
                break
            num_assigned_previous = num_assigned
        else:
            print("\tProblem solving the ILP...")
            break


if __name__ == "__main__":
    main()
