import os.path

from easychair_extra.read import read_committee, read_submission
from easychair_extra.reviewassignment import committee_to_bid_profile, find_emergency_reviewers, \
    find_feasible_review_assignment


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(current_dir, "..", "easychair_sample_files")

    # Read the committee file
    committee = read_committee(
        os.path.join(root_dir, "committee.csv"),
        bids_file_path=os.path.join(root_dir, "bidding.csv"),
    )
    committee = committee.head(300)  # Reduce size for performance reason

    # Read the submission file
    submissions = read_submission(os.path.join(root_dir, "submission.csv"))
    submissions = submissions.head(150)  # Reduce size for performance reason

    # Compute a bid profile
    bid_level_weights = {"yes": 1, "maybe": 0.5}
    bid_profile = committee_to_bid_profile(committee, submissions, bid_level_weights)
    # Compute a set of emergency reviewers
    max_num_emergency_revs = int(len(committee.index) * 0.2)
    emergency_revs_assignment = find_emergency_reviewers(
        bid_profile, bid_level_weights, max_num_emergency_revs
    )
    emergency_reviewers = sorted(emergency_revs_assignment)
    num_submission_covered = sum(len(p) for p in emergency_revs_assignment.values())
    print(f"These {len(emergency_reviewers)} reviewers can serve as emergency reviewers: "
          f"{emergency_reviewers}.")
    print(f"This pool of emergency reviewers covers {num_submission_covered}.\n")

    # Check that a review assignment would still be possible without the emergency reviewers
    new_bid_profile = {
        rev: bid_dict for rev, bid_dict in bid_profile.items() if rev not in emergency_reviewers
    }
    number_review_per_paper = 3
    total_num_reviews_needed = len(submissions.index) * number_review_per_paper
    reviewers_assignment = find_feasible_review_assignment(
        new_bid_profile,
        bid_level_weights,
        5,  # Num review per reviewer
        number_review_per_paper,
    )
    size_assignment = sum(len(p) for p in reviewers_assignment.values())
    if size_assignment < total_num_reviews_needed:
        print(f"By excluding the emergency reviewers, there is an assignment providing "
              f"{size_assignment} reviews for {total_num_reviews_needed} reviews needed.")
    else:
        print("By excluding the emergency reviewers, there still is an assignment providing the"
              " required number of reviews.")


if __name__ == "__main__":
    main()
