from __future__ import annotations

import os
from collections.abc import Collection

import numpy as np
from pandas import DataFrame
from sklearn.cluster import KMeans

from easychair_extra.read import read_committee, read_submission
from easychair_extra.submission import bid_similarity


class Submission:
    """Class used to work with submissions"""
    def __init__(
            self,
            name,
            pairwise_scores=None,
            title=None,
            group_of=None,
            weight=1,
    ):
        self.name = str(name)
        self.title = title
        self.pairwise_scores = pairwise_scores
        self.group_of = group_of
        self.weight = weight

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def cluster_submissions(submissions: Collection[Submission], n_clusters):
    """Clusters submissions based on their similarity scores"""
    score_matrix = np.array(
        [
            [s1.pairwise_scores.get(s2.name, 0) for s1 in submissions]
            for s2 in submissions
        ],
        dtype=float,
    )
    score_matrix /= score_matrix.max()
    distance_matrix = 1 - score_matrix
    np.fill_diagonal(distance_matrix, 0)

    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(distance_matrix)
    labels = kmeans.labels_

    clusters = [[] for _ in range(n_clusters)]
    for item, label in zip(submissions, labels):
        if label >= 0:
            clusters[label].append(item)
    return clusters


def merge_submissions(group, all_submissions):
    """Merges a group of submissions into a single submission"""
    res = Submission(
        name=" - ".join(str(p.name) for p in group),
        pairwise_scores={
            s2.name: sum(s1.pairwise_scores[s2.name] for s1 in group) / len(group)
            for s2 in all_submissions
        },
        group_of=group,
        weight=sum(s.weight for s in group),
    )
    res.pairwise_scores[res.name] = sum(
        s1.pairwise_scores[s2.name] for s1 in group for s2 in group
    ) / len(group)
    return res


def iterative_merge_clustering(
        submissions: list[Submission],
        merging_bound: int,
        n_cluster_ratio_min: float = 0,
        n_cluster_ratio_max: float = 1,
):
    """Iteratively clusters submissions and merges them. Re-inject merged submisssions so that
    they can be merged further down the line."""
    all_submissions = set(submissions)
    current_submissions = set(submissions)
    new_submissions = set()
    while True:
        global_merged_happened = False
        min_n_clusters = max(2, int(n_cluster_ratio_min * len(current_submissions)))
        max_n_clusters = min(
            len(current_submissions), int(n_cluster_ratio_max * len(current_submissions))
        )
        for n_clusters in range(min_n_clusters, max_n_clusters):
            clusters = cluster_submissions(current_submissions, n_clusters)
            local_merged_happened = False
            for c in clusters:
                if len(c) > 1 and sum(s.weight for s in c) <= merging_bound:
                    current_submissions.difference_update(c)
                    new_group = []
                    for s in c:
                        if s.group_of:
                            new_group.extend(s.group_of)
                        else:
                            new_group.append(s)
                    merged_submission = merge_submissions(new_group, all_submissions)
                    new_submissions.add(merged_submission)
                    all_submissions.add(merged_submission)
                    for s in all_submissions:
                        s.pairwise_scores[merged_submission.name] = (
                            merged_submission.pairwise_scores[s.name]
                        )
                    print(
                        f"\tMerged {c} into a single submission"
                    )
                    local_merged_happened = True
                    global_merged_happened = True
            if local_merged_happened:
                break
        if not global_merged_happened:
            if len(new_submissions) > 0:
                current_submissions = current_submissions.union(new_submissions)
                new_submissions = set()
                print("Remixing the new submissions in.")
            else:
                break
    print("Nothing to merge, we stop here.")
    return current_submissions


def instantiate_submissions(submission_df: DataFrame, similarity_dict):
    """Construct a list of Submission object from the rows of the submission DataFrame."""
    all_submissions = []
    submission_df.apply(
        lambda df_row: all_submissions.append(
            Submission(
                df_row["#"],
                title=df_row["title"],
                pairwise_scores={
                    str(k): v for k, v in similarity_dict[df_row["#"]].items()
                },
            )
        ),
        axis=1,
    )
    return all_submissions


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(current_dir, "..", "easychair_sample_files")

    # Read the committee file with the bids
    committee_df = read_committee(
        os.path.join(root_dir, "committee.csv"),
        bids_file_path=os.path.join(root_dir, "bidding.csv"),
    )

    # Read the submission file
    submission_df = read_submission(
        os.path.join(root_dir, "submission.csv"),
        submission_topic_file_path=os.path.join(root_dir, "submission_topic.csv"),
    )
    submission_df = submission_df.head(100)

    # Compute and aggregate the bid similarity and the topic similarity
    bid_level_weights = {"yes": 1, "maybe": 0.5}
    bid_sim = bid_similarity(submission_df, committee_df, bid_level_weights)
    similarity = {s1: {s2: int(10000 * b) for s2, b in bid_sim[s1].items()} for s1 in bid_sim}

    # Instantiate all the Submission instances
    submissions = instantiate_submissions(submission_df, similarity)

    # Iteratively merge the submissions into groups of at most 12 submissions
    new_submissions = iterative_merge_clustering(submissions, 12, n_cluster_ratio_max=0.1)


if __name__ == "__main__":
    main()
